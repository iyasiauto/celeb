// Docu Studio - Electron main process.
// Runs the Python backend (docu/studio/studio.py), streams its JSON events to the window, keeps settings
// and API keys (encrypted with the OS keychain through safeStorage) in the app's user-data folder.

const { app, BrowserWindow, ipcMain, dialog, shell, safeStorage, nativeTheme, clipboard } = require("electron");
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn, execFile } = require("child_process");

const isWin = process.platform === "win32";
const USER = () => app.getPath("userData");
const SETTINGS = () => path.join(USER(), "settings.json");
const SECRETS = () => path.join(USER(), "secrets.json");
const RUNS = () => path.join(USER(), "runs.json");
const KEY_NAMES = ["FAMESPEAK_API_KEY", "ANTHROPIC_API_KEY", "GOFILE_TOKEN"];

let win;
const tasks = new Map(); // taskId -> child process

// ------------------------------------------------------------------ settings & secrets
function readJSON(p, fallback) {
  try { return JSON.parse(fs.readFileSync(p, "utf-8")); } catch { return fallback; }
}
function writeJSON(p, data) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(data, null, 1));
}

function bundledPipeline() {
  // packaged: resources/pipeline; from source: the repo this folder sits in
  return app.isPackaged ? path.join(process.resourcesPath, "pipeline") : path.resolve(__dirname, "..");
}

function defaultWorkspace() {
  if (!app.isPackaged) return path.resolve(__dirname, "..");
  return path.join(app.getPath("documents"), "DocuStudio");
}

function ensureWorkspace(ws) {
  // first run of the installed app: copy the bundled engine, templates and example projects
  if (!fs.existsSync(path.join(ws, "docu", "studio", "studio.py"))) {
    const src = bundledPipeline();
    if (fs.existsSync(path.join(src, "docu"))) {
      fs.mkdirSync(ws, { recursive: true });
      fs.cpSync(src, ws, { recursive: true, force: false, errorOnExist: false });
    }
  }
  fs.mkdirSync(path.join(ws, "media"), { recursive: true });
}

function settings() {
  const s = readJSON(SETTINGS(), {});
  const ws = s.workspace || defaultWorkspace();
  const venvPy = isWin ? path.join(ws, ".venv", "Scripts", "python.exe") : path.join(ws, ".venv", "bin", "python");
  return {
    workspace: ws,
    python: s.python || (fs.existsSync(venvPy) ? venvPy : isWin ? "python" : "python3"),
    workers: s.workers || Math.max(2, Math.min(8, os.cpus().length - 2)),
    model: s.model || "claude-opus-5-5",
    effort: s.effort || "high",
    upload: s.upload !== false,
    limitGb: s.limitGb || 1.0,
    aiQa: s.aiQa !== false,
    ...s,
    workspace: ws,
  };
}

function readSecrets() {
  const raw = readJSON(SECRETS(), {});
  const out = {};
  for (const k of KEY_NAMES) {
    const v = raw[k];
    if (!v) continue;
    try {
      out[k] = v.enc && safeStorage.isEncryptionAvailable()
        ? safeStorage.decryptString(Buffer.from(v.data, "base64"))
        : Buffer.from(v.data, "base64").toString("utf-8");
    } catch { /* unreadable on this machine */ }
  }
  return out;
}

function saveSecret(name, value) {
  if (!KEY_NAMES.includes(name)) throw new Error("unknown key " + name);
  const raw = readJSON(SECRETS(), {});
  if (!value) delete raw[name];
  else if (safeStorage.isEncryptionAvailable()) raw[name] = { enc: true, data: safeStorage.encryptString(value).toString("base64") };
  else raw[name] = { enc: false, data: Buffer.from(value, "utf-8").toString("base64") };
  writeJSON(SECRETS(), raw);
  try { fs.chmodSync(SECRETS(), 0o600); } catch { /* windows */ }
  return { encrypted: safeStorage.isEncryptionAvailable() };
}

// ------------------------------------------------------------------ backend
function backendEnv() {
  const s = settings();
  return {
    ...process.env,
    ...readSecrets(),
    STUDIO_WORKSPACE: s.workspace,
    VIDEO_ROOT: path.join(s.workspace, "media"),
    PYTHONUNBUFFERED: "1",
    PYTHONIOENCODING: "utf-8",
    WORKERS: String(s.workers),
    ...(s.frontierDir ? { FRONTIER_DIR: s.frontierDir } : {}),
    ...(s.frontierPython ? { FRONTIER_PYTHON: s.frontierPython } : {}),
  };
}

function studioScript() {
  return path.join(settings().workspace, "docu", "studio", "studio.py");
}

function spawnBackend(args, onEvent) {
  const s = settings();
  ensureWorkspace(s.workspace);
  const child = spawn(s.python, [studioScript(), "--workspace", s.workspace, ...args], {
    cwd: s.workspace, env: backendEnv(), windowsHide: true, detached: !isWin,
  });
  let buf = "";
  const feed = (chunk) => {
    buf += chunk.toString("utf-8");
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      let ev;
      try { ev = JSON.parse(line); } catch { ev = { t: "log", msg: line }; }
      onEvent(ev);
    }
  };
  child.stdout.on("data", feed);
  child.stderr.on("data", feed);
  return child;
}

function query(args) {
  // short commands: collect the result event
  return new Promise((resolve) => {
    let result = null, error = null;
    const logs = [];
    let child;
    try {
      child = spawnBackend(args, (ev) => {
        if (ev.t === "result") result = ev.data;
        else if (ev.t === "error") error = ev.msg;
        else if (ev.t === "log") logs.push(ev.msg);
      });
    } catch (e) { return resolve({ ok: false, error: String(e) }); }
    child.on("error", (e) => resolve({ ok: false, error: `Python could not be started (${settings().python}): ${e.message}` }));
    child.on("close", (code) => resolve(result !== null ? { ok: true, data: result }
      : { ok: false, error: error || logs.slice(-6).join("\n") || `exit ${code}` }));
  });
}

function startTask(taskId, args) {
  const child = spawnBackend(args, (ev) => send("task:event", { taskId, ev }));
  tasks.set(taskId, child);
  child.on("error", (e) => send("task:event", { taskId, ev: { t: "error", msg: `Python could not be started: ${e.message}` } }));
  child.on("close", (code) => {
    tasks.delete(taskId);
    send("task:event", { taskId, ev: { t: "exit", code } });
  });
  return { ok: true };
}

function cancelTask(taskId) {
  const child = tasks.get(taskId);
  if (!child) return { ok: false };
  if (isWin) execFile("taskkill", ["/pid", String(child.pid), "/T", "/F"]);
  else { try { process.kill(-child.pid, "SIGTERM"); } catch { child.kill("SIGTERM"); } }
  return { ok: true };
}

function send(channel, payload) {
  if (win && !win.isDestroyed()) win.webContents.send(channel, payload);
}

// ------------------------------------------------------------------ IPC
ipcMain.handle("settings:get", () => ({ ...settings(), platform: process.platform, version: app.getVersion(),
  encryption: safeStorage.isEncryptionAvailable(), packaged: app.isPackaged }));
ipcMain.handle("settings:set", (_e, patch) => {
  const cur = readJSON(SETTINGS(), {});
  writeJSON(SETTINGS(), { ...cur, ...patch });
  return settings();
});
ipcMain.handle("secrets:status", () => {
  const s = readSecrets();
  return Object.fromEntries(KEY_NAMES.map((k) => [k, s[k] ? "•••• " + s[k].slice(-4) : ""]));
});
ipcMain.handle("secrets:set", (_e, name, value) => saveSecret(name, (value || "").trim()));
ipcMain.handle("py:query", (_e, args) => query(args));
ipcMain.handle("task:start", (_e, taskId, args) => startTask(taskId, args));
ipcMain.handle("task:cancel", (_e, taskId) => cancelTask(taskId));
ipcMain.handle("job:write", (_e, job) => {
  const dir = path.join(USER(), "jobs");
  fs.mkdirSync(dir, { recursive: true });
  const p = path.join(dir, `job_${Date.now()}.json`);
  fs.writeFileSync(p, JSON.stringify(job, null, 1));
  return p;
});
ipcMain.handle("runs:get", () => readJSON(RUNS(), []));
ipcMain.handle("runs:set", (_e, runs) => { writeJSON(RUNS(), runs.slice(0, 60)); return true; });
ipcMain.handle("dialog:open", async (_e, opts) => {
  const r = await dialog.showOpenDialog(win, opts || {});
  return r.canceled ? null : r.filePaths;
});
ipcMain.handle("file:stat", (_e, p) => {
  try {
    const st = fs.statSync(p);
    const out = { size: st.size, name: path.basename(p) };
    if (/\.(txt|srt|md)$/i.test(p) && st.size < 2e6) out.text = fs.readFileSync(p, "utf-8");
    return out;
  } catch { return null; }
});
ipcMain.handle("shell:open", (_e, p) => shell.openPath(p));
ipcMain.handle("shell:show", (_e, p) => shell.showItemInFolder(p));
ipcMain.handle("shell:external", (_e, url) => (/^https?:\/\//.test(url) ? shell.openExternal(url) : null));
ipcMain.handle("clipboard:write", (_e, text) => clipboard.writeText(String(text)));

// ------------------------------------------------------------------ window
function createWindow() {
  nativeTheme.themeSource = "dark";
  win = new BrowserWindow({
    width: 1440, height: 920, minWidth: 1100, minHeight: 720,
    backgroundColor: "#0a0c11",
    title: "Docu Studio",
    icon: path.join(__dirname, "build", "icon.png"),
    titleBarStyle: process.platform === "darwin" ? "hiddenInset" : "hidden",
    titleBarOverlay: process.platform === "darwin" ? false : { color: "#0a0c11", symbolColor: "#c9ccd6", height: 40 },
    webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true, nodeIntegration: false, sandbox: true },
  });
  win.loadFile(path.join(__dirname, "src", "index.html"));
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: "deny" }; });
}

app.whenReady().then(() => {
  ensureWorkspace(settings().workspace);
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on("window-all-closed", () => {
  for (const id of tasks.keys()) cancelTask(id);
  if (process.platform !== "darwin") app.quit();
});
