// Docu Studio - renderer. Plain JS: state, pages, and the live view of each production.
const S = window.studio;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const h = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (k === "html") e.innerHTML = v;
    else if (v !== false && v != null) e.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) e.append(k.nodeType ? k : document.createTextNode(String(k)));
  return e;
};
const _rc = Element.prototype.replaceChildren;
Element.prototype.replaceChildren = function (...kids) { return _rc.apply(this, kids.filter((k) => k != null && k !== false)); };
const fileUrl = (p) => "file:///" + String(p).replace(/\\/g, "/").replace(/^\/+/, "").split("/").map(encodeURIComponent).join("/").replace(/^([A-Za-z])%3A/, "$1:");
const fmtBytes = (n) => (n > 1e9 ? (n / 1e9).toFixed(2) + " GB" : (n / 1e6).toFixed(0) + " MB");
const STAGE_NAMES = {
  project: "Project", voice: "Voiceover", timing: "Word timing", shotlist: "Shot list", plan: "Plan check", prep: "Assets",
  stills: "Stills", qa: "Visual QA", render: "Render", mix: "Sound mix", final: "Final video", deliver: "Deliver", metadata: "YouTube metadata",
};
const STAGES = Object.keys(STAGE_NAMES);

const state = {
  info: null, settings: null, secrets: {},
  niche: null, style: null, voice: "famespeak", shotlist: "ai",
  nicheSource: "folder", nicheFolder: null, nicheTags: null,
  script: null, scriptText: "", mp3: null, srt: null,
  runs: [], current: null, tasks: {},
};

// a key counts when the app holds it or the engine finds it elsewhere (api_keys/keys.env, your Frontier .env)
const hasKey = (k) => !!(state.secrets[k] || (state.info && state.info.keys && state.info.keys[k]));
const AI = () => (state.info && state.info.ai) || {};
const AI_PROVIDERS = [
  ["auto", "Auto (first one set up)"], ["claude_code", "Claude Code CLI (your plan, no API key)"], ["openrouter", "OpenRouter"],
  ["openlux", "OpenLux (sees pictures)"], ["antigravity", "Antigravity (local router)"], ["custom", "Custom endpoint"],
  ["claude_api", "Claude API"], ["none", "Off"],
];

function toast(msg, bad = false) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "toast" + (bad ? " bad" : "");
  t.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (t.hidden = true), bad ? 7000 : 3200);
}

// ------------------------------------------------------------------ navigation
function go(page) {
  $$("nav a").forEach((a) => a.classList.toggle("active", a.dataset.page === page));
  $$(".page").forEach((p) => p.classList.toggle("active", p.id === "page-" + page));
  if (page === "library") renderLibrary();
  if (page === "niches") renderNiches();
  if (page === "settings") renderSettings();
  if (page === "runs") renderRuns();
}
$$("nav a").forEach((a) => a.addEventListener("click", () => go(a.dataset.page)));

// ------------------------------------------------------------------ load
async function loadInfo() {
  const r = await S.query(["info"]);
  if (!r.ok) {
    toast("The engine did not answer: " + r.error, true);
    state.info = { styles: [], niches: [], projects: [], keys: {} };
  } else state.info = r.data;
  return state.info;
}

async function boot() {
  state.settings = await S.settings();
  state.secrets = await S.secrets();
  state.runs = (await S.runs()) || [];
  for (const r of state.runs) if (r.status === "running") { r.status = "error"; r.error = r.error || "The app was closed while this was running. Resume it from the stage that was running."; }
  $("#f-qa").checked = state.settings.aiQa;
  $("#f-upload").checked = state.settings.upload;
  await loadInfo();
  if (!$("#f-voice").value && state.info.voice_id) $("#f-voice").value = state.info.voice_id;
  renderCreate();
  renderSideStatus();
  renderRuns();
  doctor(false);
}

function renderSideStatus() {
  const pill = (ok, label, warn) => h("div", { class: "pill" }, h("span", { class: "dot " + (ok ? "ok" : warn ? "warn" : "bad") }), label);
  const ai = AI();
  $("#side-status").replaceChildren(
    pill(hasKey("FAMESPEAK_API_KEY"), "FameSpeak voice", true),
    pill(!!ai.editor, ai.editor ? "AI editor: " + ai.editor_label : "AI editor: offline rules", true),
    pill(!!ai.vision, ai.vision ? "AI vision: " + ai.vision_label : "AI vision: off", true),
    pill(!!(state.doctorOk), state.doctorOk === undefined ? "Engine: checking…" : state.doctorOk ? "Engine ready" : "Engine needs setup"),
  );
}

// ------------------------------------------------------------------ create
function renderCreate() {
  const info = state.info;
  if (!state.niche && info.niches.length) state.niche = info.niches[0].id;
  $("#niche-choices").replaceChildren(...info.niches.map((n) => {
    const st = n.status || {};
    return h("div", { class: "choice" + (state.niche === n.id ? " on" : ""), onclick: () => { state.niche = n.id; state.style = null; const v = n.clip_share || 30; $("#f-clips").value = v; updateClips(); renderCreate(); } },
      h("h3", {}, n.name), h("p", {}, n.description || ""),
      h("div", { class: "meta" },
        h("span", { class: "tag " + (st.downloaded ? "ok" : "warn") }, st.downloaded ? `${st.clips_on_disk} clips · ${st.images_on_disk} pictures` : "footage not downloaded"),
        h("span", { class: "tag " + (st.image_catalog ? "ok" : "warn") }, st.image_catalog ? "catalogued" : "needs AI catalog"),
        h("span", { class: "tag" }, `${n.clip_share || 30} % clips`)));
  }));
  const niche = info.niches.find((n) => n.id === state.niche);
  if (!state.style || !info.styles.find((s) => s.id === state.style)) state.style = niche ? niche.default_style : "documentary";
  const card = (s) => h("div", { class: "choice style-card" + (state.style === s.id ? " on" : ""), onclick: () => { state.style = s.id; renderCreate(); } },
    s.preview_path ? h("div", { class: "thumb", style: `background-image:url('${fileUrl(s.preview_path)}')` },
      s.engine === "frontier" ? h("span", { class: "engine frontier" }, "FRONTIER") : null,
      s.sample_path ? h("span", { class: "play", onclick: (e) => { e.stopPropagation(); lightbox(s.sample_path, true); } }, "▶ Sample") : null)
      : h("div", { class: "thumb none" }, "no preview", s.engine === "frontier" ? h("span", { class: "engine frontier" }, "FRONTIER") : null),
    h("div", { class: "info" }, h("h3", {}, h("span", { class: "letter" }, s.letter || "•"), s.name), h("p", {}, s.blurb || s.description || "")));
  const groups = [
    ["Docu Studio templates", "rendered by this studio from your own footage", info.styles.filter((s) => s.engine === "docu" && !String(s.id).startsWith("custom:"))],
    ["Your templates", "folders in " + (info.styles_folder || "styles/"), info.styles.filter((s) => String(s.id).startsWith("custom:"))],
    ["Frontier styles", info.frontier && info.frontier.dir ? (info.frontier.engine ? "made by Frontier's engine with its own sources and keys" : "catalogue only — Frontier's engine is not in the folder") : "set the Frontier folder in Settings", info.styles.filter((s) => s.engine === "frontier")],
  ];
  $("#style-choices").replaceChildren(...groups.filter((g) => g[2].length).map(([t, sub, list]) =>
    h("div", { class: "style-group" }, h("h4", {}, t, h("span", { class: "sub" }, sub)), h("div", { class: "grid styles-grid" }, ...list.map(card)))));
  const st = info.styles.find((s) => s.id === state.style);
  const isF = st && st.engine === "frontier";
  $$(".step")[0].classList.toggle("dim", !!isF);
  $("#vm-frontier").hidden = !(isF && info.frontier && info.frontier.env);
  if (!isF && state.voice === "frontier") $("#voice-mode button[data-v=famespeak]").click();
  const ai = AI();
  $("#shotlist-sub").textContent = ai.editor ? `AI editor: ${ai.editor_label} (Settings → AI)` : "no AI editor set up: the offline rules pick the visuals (Settings → AI)";
  $("#qa-sub").textContent = ai.vision ? `${ai.vision_label} checks the stills; the AI editor fixes what it finds` : "needs an AI vision provider, e.g. OpenLux (Settings → AI)";
  let note = $("#frontier-note");
  if (isF && !note) {
    note = h("div", { id: "frontier-note", class: "note" }, "Frontier styles find their own footage and pictures and render with Frontier's engine and its .env keys. Your script and your voice (FameSpeak, your recording, or Frontier's own voice from its .env) are used as they are; the niche is not needed.");
    $("#niche-choices").before(note);
  } else if (!isF && note) note.remove();
  summary();
}

function updateClips() { $("#clip-share-val").textContent = $("#f-clips").value + " %"; summary(); }
$("#f-clips").addEventListener("input", updateClips);
["#f-title", "#f-voice"].forEach((s) => $(s).addEventListener("input", summary));

function seg(id, key, after) {
  $$(`#${id} button`).forEach((b) => b.addEventListener("click", () => {
    state[key] = b.dataset.v;
    $$(`#${id} button`).forEach((x) => x.classList.toggle("on", x === b));
    after && after();
    summary();
  }));
}
seg("voice-mode", "voice", () => { $("#voice-famespeak").hidden = state.voice !== "famespeak"; $("#voice-file").hidden = state.voice !== "file"; $("#voice-frontier").hidden = state.voice !== "frontier"; });
seg("shotlist-mode", "shotlist");

async function pickInto(el, key, filters, after) {
  const r = await S.pick({ properties: ["openFile"], filters });
  if (!r) return;
  state[key] = r[0];
  el.classList.add("has");
  $(".fp-label", el).textContent = r[0].split(/[\\/]/).pop();
  after && (await after(r[0]));
  summary();
}
$("#pick-script").addEventListener("click", () => pickInto($("#pick-script"), "script", [{ name: "Script", extensions: ["txt", "md"] }], async (p) => {
  const st = await S.stat(p);
  state.scriptText = (st && st.text) || "";
  const chars = state.scriptText.length, words = state.scriptText.split(/\s+/).filter(Boolean).length;
  const mins = words / 150;
  $("#script-info").textContent = `${words.toLocaleString()} words · ${chars.toLocaleString()} characters · about ${mins.toFixed(1)} min of narration · FameSpeak ≈ ${chars.toLocaleString()} credits`;
  if (!$("#f-title").value) {
    const name = p.split(/[\\/]/).pop().replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ");
    if (!/^script$/i.test(name)) $("#f-title").value = name;
  }
}));
$("#pick-mp3").addEventListener("click", () => pickInto($("#pick-mp3"), "mp3", [{ name: "Audio", extensions: ["mp3", "wav", "m4a"] }]));
$("#pick-srt").addEventListener("click", () => pickInto($("#pick-srt"), "srt", [{ name: "Subtitles", extensions: ["srt"] }]));

$("#btn-check-voice").addEventListener("click", async () => {
  const id = $("#f-voice").value.trim();
  if (!id) return toast("Enter the ElevenLabs voice ID first.");
  if (!hasKey("FAMESPEAK_API_KEY")) return toast("Add your FameSpeak API key in Settings first (or set the Frontier folder: its .env key is used).", true);
  $("#voice-info").textContent = "Checking the voice…";
  const r = await S.query(["voice", "--voice-id", id]);
  if (!r.ok) { $("#voice-info").textContent = r.error; return; }
  const v = r.data.voice, u = r.data.usage || {};
  const name = v ? (v.name || v.voice_name || id) : null;
  const credits = u.credits != null ? ` · ${Number(u.credits).toLocaleString()} credits left` : "";
  $("#voice-info").innerHTML = v ? `<b style="color:var(--green)">✓ ${name}</b>${v.labels ? " · " + Object.values(v.labels).join(", ") : ""}${credits}`
    : `<span style="color:var(--red)">No ElevenLabs voice with this ID on your FameSpeak account.</span>${credits}`;
});

function summary() {
  const niche = state.info && state.info.niches.find((n) => n.id === state.niche);
  const style = state.info && state.info.styles.find((s) => s.id === state.style);
  const tag = (k, v) => h("span", { class: "tag" }, k + " ", h("b", {}, v));
  $("#launch-summary").replaceChildren(
    tag("Niche", style && style.engine === "frontier" ? "Frontier finds its own" : niche ? niche.name.split("(")[0].trim() : "—"),
    tag("Style", style ? style.name : "—"),
    tag("Voice", state.voice === "famespeak" ? ($("#f-voice").value ? "FameSpeak" : "FameSpeak (voice ID?)") : state.voice === "frontier" ? "Frontier's voice" : state.mp3 ? "my recording" : "recording?"),
    tag("Clips", $("#f-clips").value + " %"),
    tag("Shot list", state.shotlist === "auto" ? "offline" : AI().editor ? AI().editor_label : "offline (no AI set up)"),
  );
}

$("#btn-start").addEventListener("click", startProduction);

async function startProduction() {
  const title = $("#f-title").value.trim();
  if (!title) return toast("Give the video a title.", true);
  if (!state.script) return toast("Choose the script file.", true);
  const niche = state.info.niches.find((n) => n.id === state.niche);
  const stl = state.info.styles.find((s) => s.id === state.style);
  const isF = stl && stl.engine === "frontier";
  if (isF && !stl.runnable) return toast("Frontier's engine is not in the Frontier folder: Settings → Frontier → Download Frontier.", true);
  if (!isF) {
    if (!niche) return toast("Choose a niche.", true);
    if (!niche.status.downloaded) return toast("This niche's footage is not on this computer yet: Niches & assets → Download.", true);
  }
  let voice;
  if (state.voice === "famespeak") {
    const id = $("#f-voice").value.trim();
    if (!id) return toast("Enter the ElevenLabs voice ID.", true);
    if (!hasKey("FAMESPEAK_API_KEY")) return toast("Add your FameSpeak API key in Settings (or set the Frontier folder: its .env key is used).", true);
    voice = { mode: "famespeak", voice_id: id, language: $("#f-lang").value.trim() || null };
  } else if (state.voice === "frontier") {
    voice = { mode: "frontier" };
  } else {
    if (!state.mp3) return toast("Choose the voiceover file.", true);
    voice = { mode: "file", mp3: state.mp3, srt: state.srt };
  }
  if (!isF && state.shotlist === "ai" && !AI().editor) toast("No AI editor set up: the offline shot list will be used (Settings → AI).");
  const s = state.settings;
  const job = {
    title, niche: isF ? null : state.niche, style: state.style, clip_share: Number($("#f-clips").value), script: state.script, voice,
    shotlist: state.shotlist, ai_qa: $("#f-qa").checked, effort: s.effort, workers: s.workers,
    deliver: { upload: $("#f-upload").checked, limit_gb: s.limitGb },
  };
  const jobPath = await S.writeJob(job);
  const run = { id: "run_" + Date.now(), title, job, jobPath, started: Date.now(), status: "running", stages: {}, progress: {}, artifacts: [], log: [], error: null };
  state.runs.unshift(run);
  state.current = run.id;
  launch(run, ["make", "--job", jobPath]);
  go("runs");
}

function launch(run, args) {
  run.status = "running";
  run.error = null;
  state.tasks[run.id] = run;
  S.startTask(run.id, args);
  saveRuns();
  renderRuns();
}

// ------------------------------------------------------------------ task events
S.onTask(({ taskId, ev }) => {
  const run = state.runs.find((r) => r.id === taskId) || state.tasks[taskId];
  if (!run) return;
  if (ev.t === "stage") {
    run.stages[ev.stage] = { status: ev.status, msg: ev.msg || "" };
    if (ev.status === "running") run.active = ev.stage;
  } else if (ev.t === "progress") {
    run.progress[ev.stage] = { value: ev.value, msg: ev.msg };
    if (run.stages[ev.stage]) run.stages[ev.stage].msg = ev.msg;
  } else if (ev.t === "artifact") {
    if (!run.artifacts.find((a) => a.path === ev.path)) run.artifacts.push({ kind: ev.kind, path: ev.path, label: ev.label });
  } else if (ev.t === "log") {
    run.log.push(ev.msg);
    if (run.log.length > 1500) run.log.splice(0, run.log.length - 1500);
  } else if (ev.t === "error") {
    run.error = ev.msg;
    run.log.push("ERROR: " + ev.msg);
    if (run.active && run.stages[run.active]) run.stages[run.active].status = "error";
  } else if (ev.t === "done") {
    run.status = ev.ok ? "done" : "error";
    if (ev.output) run.output = ev.output;
    if (ev.link) run.link = ev.link;
    if (ev.ok && run.kind !== "task") toast("✓ " + run.title + " is ready");
  } else if (ev.t === "exit") {
    if (run.status === "running") run.status = ev.code === 0 ? "done" : "error";
    delete state.tasks[taskId];
    saveRuns();
    if (run.kind === "task") { loadInfo().then(() => { renderNiches(); renderCreate(); }); }
  }
  scheduleRender(run);
});

let _rt = null;
function scheduleRender(run) {
  if (_rt) return;
  _rt = setTimeout(() => {
    _rt = null;
    if ($("#page-runs").classList.contains("active")) renderRuns();
    if ($("#page-niches").classList.contains("active") && run.kind === "task") renderNiches();
    const n = state.runs.filter((r) => r.status === "running").length;
    $("#runs-badge").hidden = !n;
    $("#runs-badge").textContent = n;
  }, 250);
}
let _saveT = null;
function saveRuns() {
  clearTimeout(_saveT);
  _saveT = setTimeout(() => S.saveRuns(state.runs.filter((r) => r.kind !== "task").map((r) => ({ ...r, log: r.log.slice(-300) }))), 500);
}

function overall(run) {
  let sum = 0;
  for (const s of STAGES) {
    const st = run.stages[s];
    if (!st) continue;
    if (st.status === "done" || st.status === "skipped") sum += 1;
    else if (st.status === "running") sum += (run.progress[s] && run.progress[s].value) || 0.1;
  }
  return Math.min(1, sum / STAGES.length);
}

// ------------------------------------------------------------------ runs page
function renderRuns() {
  const runs = state.runs.filter((r) => r.kind !== "task");
  if (!state.current && runs.length) state.current = runs[0].id;
  $("#runs-list").replaceChildren(...(runs.length ? runs.map((r) => h("div", { class: "run-item" + (r.id === state.current ? " on" : ""), onclick: () => { state.current = r.id; renderRuns(); } },
    h("div", { class: "t" }, r.title),
    h("div", { class: "s" }, h("span", { class: "dot " + (r.status === "done" ? "ok" : r.status === "error" ? "bad" : "warn") }),
      r.status === "running" ? (STAGE_NAMES[r.active] || "starting") + "…" : r.status === "done" ? "Ready" : r.status === "error" ? "Stopped" : r.status,
      h("span", {}, "· " + new Date(r.started).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }))),
    h("div", { class: "minibar" }, h("i", { style: `width:${Math.round(overall(r) * 100)}%` })))) : [h("div", { class: "empty" }, "No productions yet.")]));
  const run = runs.find((r) => r.id === state.current);
  const box = $("#run-detail");
  if (!run) return box.replaceChildren(h("div", { class: "empty" }, "Start a video on the Create page."));
  const pct = Math.round(overall(run) * 100);
  const act = run.active && run.progress[run.active];
  const head = h("div", { class: "run-head" },
    h("div", { style: "flex:1;min-width:0" }, h("h2", {}, run.title),
      h("div", { class: "sub" }, `${(state.info.styles.find((s) => s.id === run.job.style) || {}).name || run.job.style} · ${run.job.clip_share} % clips · ${{ famespeak: "FameSpeak voice", frontier: "Frontier's voice" }[run.job.voice.mode] || "own recording"} · ${run.job.shotlist === "auto" ? "offline shot list" : "AI shot list"}`),
      h("div", { class: "bigbar" }, h("i", { style: `width:${pct}%` })),
      h("div", { class: "sub" }, run.status === "running" ? `${pct} % · ${STAGE_NAMES[run.active] || ""}${act && act.msg ? " · " + act.msg : ""}` : run.status === "done" ? "Finished" : "Stopped")),
    h("div", { style: "display:flex;gap:8px" },
      run.status === "running" ? h("button", { class: "btn danger", onclick: () => { S.cancelTask(run.id); toast("Stopping…"); } }, "Stop") : null,
      run.status !== "running" ? resumeMenu(run) : null));
  const stages = h("div", { class: "stages" }, ...STAGES.map((s) => {
    const st = run.stages[s] || {};
    return h("div", { class: "stage " + (st.status || "") }, h("div", { class: "n" }, h("span", { class: "dot" }), STAGE_NAMES[s]), h("div", { class: "m", title: st.msg || "" }, st.msg || ""));
  }));
  const arts = run.artifacts.filter((a) => a.kind !== "sheet");
  const sheets = run.artifacts.filter((a) => a.kind === "sheet");
  const artIcon = { video: "▶", audio: "♪", srt: "CC", link: "↗", metadata: "≡", project: "▣", qa: "✓" };
  const artifacts = arts.length ? h("div", { class: "artifacts" }, ...arts.map((a) => h("div", { class: "artifact", onclick: () => openArtifact(a) }, h("span", {}, artIcon[a.kind] || "•"), a.label || a.kind))) : null;
  const log = h("div", { class: "log" });
  log.append(...run.log.slice(-400).map((l) => h("div", { class: /^ERROR|Traceback|Error:/.test(l) ? "err" : "" }, l)));
  box.replaceChildren(...[head,
    run.error ? h("div", { class: "error-box" }, run.error.slice(-2000)) : null,
    stages,
    artifacts ? h("div", { class: "section-label" }, "Files") : null, artifacts,
    sheets.length ? h("div", { class: "section-label" }, "Stills · QA contact sheets") : null,
    sheets.length ? h("div", { class: "sheets" }, ...sheets.map((a) => h("img", { src: fileUrl(a.path) + "?t=" + Date.now() % 100000, onclick: () => lightbox(a.path) }))) : null,
    h("div", { class: "section-label" }, "Log"), log].filter(Boolean));
  log.scrollTop = log.scrollHeight;
}

function resumeMenu(run) {
  const sel = h("select", { style: "width:auto" }, ...STAGES.map((s) => h("option", { value: s }, "from " + STAGE_NAMES[s])));
  const failed = STAGES.find((s) => run.stages[s] && run.stages[s].status === "error");
  if (failed) sel.value = failed;
  return h("div", { class: "inline" }, sel, h("button", { class: "btn", onclick: () => { run.log.push(`— resumed from ${sel.value} —`); launch(run, ["make", "--job", run.jobPath, "--from", sel.value]); } }, "Resume"));
}

function openArtifact(a) {
  if (a.kind === "link") { S.copy(a.path); S.external(a.path); return toast("Link copied"); }
  if (a.kind === "project") return S.open(a.path);
  S.show(a.path);
}
function lightbox(p, video) {
  const v = $("#lightbox-video"), im = $("#lightbox-img");
  v.hidden = !video; im.hidden = !!video;
  if (video) { v.src = fileUrl(p); v.play().catch(() => {}); } else im.src = fileUrl(p);
  $("#lightbox").hidden = false;
}
$("#lightbox").addEventListener("click", (e) => { if (e.target.tagName === "VIDEO") return; const v = $("#lightbox-video"); v.pause(); v.removeAttribute("src"); $("#lightbox").hidden = true; });
$("#btn-refresh-styles").addEventListener("click", async () => { await loadInfo(); renderCreate(); toast(`${state.info.styles.length} styles`); });
window.addEventListener("focus", async () => { if ($("#page-create").classList.contains("active") && !document.querySelector(".lightbox:not([hidden])")) { await loadInfo(); renderCreate(); } });

// ------------------------------------------------------------------ library
async function renderLibrary() {
  await loadInfo();
  const ps = state.info.projects;
  const accent = { gold: "#D8B26E", copper: "#C98B5B", teal: "#79B4B0", sage: "#A7BE8C", rose: "#D49A8C", slate: "#9DB3CF", amber: "#E0A64B", ivory: "#E4D6B8" };
  $("#library").replaceChildren(...(ps.length ? ps.map((p) => h("div", { class: "card lib-card" },
    h("h3", {}, p.title),
    h("div", { class: "meta" },
      p.style ? h("span", { class: "tag" }, (state.info.styles.find((s) => s.id === p.style) || {}).name || p.style) : null,
      p.look && p.look.accent ? h("span", { class: "tag" }, h("i", { class: "swatch", style: `background:${accent[p.look.accent] || "#888"}` }), p.look.accent + " · " + (p.look.kicker || "")) : null,
      p.video ? h("span", { class: "tag ok" }, fmtBytes(p.size)) : h("span", { class: "tag" }, "not rendered here")),
    h("div", { class: "lib-actions" },
      p.video ? h("button", { class: "btn tiny", onclick: () => S.open(p.video) }, "▶ Play") : null,
      p.video ? h("button", { class: "btn tiny ghost", onclick: () => S.show(p.video) }, "Show file") : null,
      p.link ? h("button", { class: "btn tiny ghost", onclick: () => { S.copy(p.link); toast("Link copied"); } }, "Copy link") : null,
      p.metadata ? h("button", { class: "btn tiny ghost", onclick: () => S.open(p.metadata) }, "Metadata") : null,
      h("button", { class: "btn tiny ghost", onclick: () => S.open(p.path) }, "Project")))) : [h("div", { class: "empty" }, "No videos yet.")]));
}
$("#btn-refresh-lib").addEventListener("click", renderLibrary);

// ------------------------------------------------------------------ niches
function taskRun(id, title, args) {
  let run = state.runs.find((r) => r.id === id);
  if (run && run.status === "running") return toast("Already running.");
  run = { id, kind: "task", title, started: Date.now(), status: "running", stages: {}, progress: {}, artifacts: [], log: [] };
  state.runs = state.runs.filter((r) => r.id !== id);
  state.runs.push(run);
  state.tasks[id] = run;
  S.startTask(id, args);
  renderNiches();
}
function taskLine(id) {
  const run = state.runs.find((r) => r.id === id);
  if (!run) return null;
  const st = run.active && run.stages[run.active];
  const pr = run.active && run.progress[run.active];
  const text = run.status === "running" ? `${run.active || "starting"}… ${pr ? Math.round(pr.value * 100) + " % " + (pr.msg || "") : (run.log.slice(-1)[0] || "")}`
    : run.status === "done" ? "✓ done" : "✗ " + (run.error || run.log.slice(-1)[0] || "stopped");
  return h("div", { class: "sub", style: "font-family:var(--mono);font-size:11.5px" }, text.slice(0, 160));
}

function renderNiches() {
  const info = state.info;
  const kitOk = state.doctor && state.doctor.filter((c) => c.name.startsWith("Asset kit")).every((c) => c.ok);
  const fa = info.frontier && info.frontier.assets;
  $("#kit-card").replaceChildren(
    h("div", {}, h("div", { class: "step-title", style: "margin:0 0 4px" }, "Asset kit"),
      h("div", { class: "sub" }, fa ? `Music beds, fonts, maps, cut-outs and textures. Your Frontier folder already has them (${fa}): use them, nothing is downloaded or duplicated.`
        : "Music beds, fonts, maps, cut-outs and the drawn props. Take them from a folder on this PC (e.g. Frontier's assets) or download once."), taskLine("task_kit")),
    h("div", { class: "inline" }, h("span", { class: "tag " + (kitOk ? "ok" : "warn") }, kitOk ? "installed" : "not installed"),
      fa ? h("button", { class: "btn" + (kitOk ? " ghost" : " primary"), onclick: () => taskRun("task_kit", "Asset kit", ["kit", "--folder", "frontier"]) }, "Use Frontier's assets") : null,
      h("button", { class: "btn ghost", onclick: async () => { const r = await S.pick({ properties: ["openDirectory"] }); if (r) taskRun("task_kit", "Asset kit", ["kit", "--folder", r[0]]); } }, "Choose kit folder…"),
      h("button", { class: "btn" + (kitOk || fa ? " ghost" : " primary"), onclick: () => taskRun("task_kit", "Asset kit", ["kit"]) }, kitOk ? "Re-download" : "Download kit")));
  $("#niche-admin").replaceChildren(...info.niches.map((n) => {
    const st = n.status || {};
    return h("div", { class: "card niche-card" },
      h("h3", {}, n.name), h("div", { class: "sub" }, n.description || ""),
      h("div", { class: "stats" },
        h("div", { class: "stat" }, h("b", {}, st.clips_on_disk || 0), h("span", {}, "clips on this computer")),
        h("div", { class: "stat" }, h("b", {}, st.images_on_disk || 0), h("span", {}, "pictures on this computer"))),
      h("div", { class: "meta" },
        h("span", { class: "tag " + (st.clip_catalog ? "ok" : "warn") }, st.clip_catalog ? "clip catalog ✓" : "no clip catalog"),
        h("span", { class: "tag " + (st.image_catalog ? "ok" : "warn") }, st.image_catalog ? "picture catalog ✓" : "pictures not described"),
        h("span", { class: "tag" }, "default: " + n.default_style)),
      taskLine("task_fetch_" + n.id), taskLine("task_cat_" + n.id),
      h("div", { class: "lib-actions" },
        n.drive && !n.local ? h("button", { class: "btn tiny" + (st.downloaded ? " ghost" : ""), onclick: () => taskRun("task_fetch_" + n.id, "Download " + n.name, ["niche-fetch", "--niche", n.id]) }, st.downloaded ? "Re-sync footage" : "Download footage")
          : h("button", { class: "btn tiny ghost", onclick: () => taskRun("task_fetch_" + n.id, "Link " + n.name, ["niche-fetch", "--niche", n.id]) }, "Re-link folders"),
        h("button", { class: "btn tiny" + (st.downloaded ? " ghost" : ""), title: "use footage already on this PC (no download)", onclick: async () => {
          const r = await S.pick({ properties: ["openDirectory"], title: "The folder with this niche's clips and pictures" });
          if (r) taskRun("task_fetch_" + n.id, "Link " + n.name, ["niche-link", "--niche", n.id, "--folder", r[0]]);
        } }, "Use a folder on this PC"),
        h("button", { class: "btn tiny ghost", disabled: !st.downloaded, onclick: () => {
          if (!AI().vision) toast("No AI vision provider: clips and pictures are described from your tags file and file names. Set OpenLux (or another) in Settings → AI for accurate picture choice.");
          taskRun("task_cat_" + n.id, "Catalog " + n.name, ["niche-catalog", "--niche", n.id]);
        } }, AI().vision ? "Catalog with AI" : "Catalog"),
        n.local && n.folder ? h("button", { class: "btn tiny ghost", onclick: () => S.open(n.folder) }, "Folder ↗") : null,
        n.drive ? h("button", { class: "btn tiny ghost", onclick: () => S.external("https://drive.google.com/drive/folders/" + n.drive) }, "Drive ↗") : null));
  }));
  const extra = ["task_frontier", "task_frontier_app", "task_setup"].concat(state.runs.filter((r) => r.id.startsWith("task_kit_")).map((r) => r.id))
    .filter((id) => state.runs.find((r) => r.id === id));
  let tl = $("#task-lines");
  if (!tl) { tl = h("div", { id: "task-lines", class: "card", style: "margin-bottom:16px" }); $("#kit-card").after(tl); }
  tl.hidden = !extra.length;
  tl.replaceChildren(h("div", { class: "step-title", style: "margin:0 0 8px" }, "Background tasks"),
    ...extra.map((id) => h("div", {}, h("b", {}, state.runs.find((r) => r.id === id).title), taskLine(id))));
  $("#n-style").replaceChildren(...info.styles.map((s) => h("option", { value: s.id }, s.name)));
}

seg("n-source", "nicheSource", () => { $("#n-folder-row").hidden = state.nicheSource !== "folder"; $("#n-drive-row").hidden = state.nicheSource !== "drive"; });
$("#pick-niche-folder").addEventListener("click", async () => {
  const r = await S.pick({ properties: ["openDirectory"] });
  if (!r) return;
  state.nicheFolder = r[0];
  $("#pick-niche-folder").classList.add("has");
  $(".fp-label", $("#pick-niche-folder")).textContent = r[0];
  if (!$("#n-name").value) $("#n-name").value = r[0].split(/[\\/]/).filter(Boolean).pop();
});
$("#pick-niche-tags").addEventListener("click", () => pickInto($("#pick-niche-tags"), "nicheTags", [{ name: "Tags", extensions: ["json"] }]));

$("#btn-add-niche").addEventListener("click", async () => {
  const name = $("#n-name").value.trim(), drive = $("#n-drive").value.trim();
  const local = state.nicheSource === "folder";
  if (!name) return toast("Give the niche a name.", true);
  if (local && !state.nicheFolder) return toast("Choose the footage folder.", true);
  if (!local && !drive) return toast("Paste the Drive folder link.", true);
  const src = local ? ["--folder", state.nicheFolder].concat(state.nicheTags ? ["--tags", state.nicheTags] : [])
    : ["--drive", (drive.match(/folders\/([A-Za-z0-9_-]+)/) || [null, drive])[1]];
  const r = await S.query(["niche-add", "--name", name, ...src, "--style", $("#n-style").value, "--clip-share", $("#n-clips").value, "--map-hint", $("#n-map").value]);
  if (!r.ok) return toast(r.error, true);
  toast(local ? "Niche added from your folder. Now Catalog it so the editor knows what each clip and picture shows." : "Niche added. Download its footage, then Catalog it.");
  $("#n-name").value = $("#n-drive").value = $("#n-map").value = "";
  state.nicheFolder = state.nicheTags = null;
  for (const id of ["#pick-niche-folder", "#pick-niche-tags"]) { $(id).classList.remove("has"); }
  $(".fp-label", $("#pick-niche-folder")).textContent = "Choose the folder…";
  $(".fp-label", $("#pick-niche-tags")).textContent = "Choose tags.json…";
  await loadInfo();
  renderNiches();
  renderCreate();
});

// ------------------------------------------------------------------ settings
const KEY_INFO = {
  FAMESPEAK_API_KEY: ["FameSpeak API key", "Voiceovers in ElevenLabs voices + SRT subtitles", "https://famespeak.online/api-keys"],
  OPENROUTER_API_KEY: ["OpenRouter API key", "AI editor through OpenRouter (e.g. deepseek/deepseek-chat)", "https://openrouter.ai/settings/keys"],
  OPENLUX_API_KEY: ["OpenLux API key", "AI vision: visual QA and cataloging (e.g. gemini-2.5-flash-lite)", "https://openlux.ai"],
  ANTIGRAVITY_API_KEY: ["Antigravity router key (if your router asks for one)", "Your Antigravity / Gemini account through the local model router", null],
  CUSTOM_AI_API_KEY: ["Custom endpoint key (optional)", "Any OpenAI-compatible server (LM Studio, Ollama, a proxy…)", null],
  ANTHROPIC_API_KEY: ["Claude API key (optional)", "Only if you choose Claude API; Claude Code CLI uses your plan instead", "https://console.anthropic.com/settings/keys"],
  GOFILE_TOKEN: ["gofile token (optional)", "Upload into your gofile account so links last longer", "https://gofile.io/myprofile"],
};
const SRC_LABEL = { "Frontier .env": "found in your Frontier .env", "api_keys/keys.env": "found in api_keys/keys.env", environment: "set" };
async function renderSettings() {
  const s = (state.settings = await S.settings());
  state.secrets = await S.secrets();
  $("#keys").replaceChildren(...Object.entries(KEY_INFO).map(([k, [label, why, url]]) => {
    const src = state.info && state.info.key_source && state.info.key_source[k];
    const inp = h("input", { type: "password", placeholder: state.secrets[k] ? "saved " + state.secrets[k] : src && src !== "environment" ? SRC_LABEL[src] + " ✓ (paste to override)" : "paste the key" });
    return h("div", { class: "key-row" },
      h("label", { class: "field" }, h("span", {}, label, " ", url ? h("a", { onclick: () => S.external(url) }, "get it ↗") : null,
        src && !state.secrets[k] ? h("span", { class: "tag ok", style: "margin-left:6px" }, SRC_LABEL[src] || src) : null), inp, h("div", { class: "sub" }, why)),
      h("div", { class: "inline" },
        h("button", { class: "btn", onclick: async () => { const r = await S.setSecret(k, inp.value); inp.value = ""; state.secrets = await S.secrets(); renderSettings(); renderSideStatus(); toast(r.encrypted ? "Saved (encrypted)" : "Saved (this system has no keychain: stored only in the app's private folder)"); } }, "Save"),
        state.secrets[k] ? h("button", { class: "btn ghost", onclick: async () => { await S.setSecret(k, ""); state.secrets = await S.secrets(); renderSettings(); renderSideStatus(); } }, "Remove") : null));
  }));
  $("#s-ws").value = s.workspace;
  $("#s-py").value = s.python;
  for (const [id, val] of [["#s-editor", s.aiEditor], ["#s-vision", s.aiVision]]) {
    $(id).replaceChildren(...AI_PROVIDERS.filter(([v]) => id === "#s-editor" || v !== "openrouter").map(([v, l]) => h("option", { value: v }, l)));
    $(id).value = val || "auto";
  }
  $("#s-editor-model").value = s.aiEditorModel || "";
  $("#s-vision-model").value = s.aiVisionModel || "";
  $("#s-agy-url").value = s.antigravityUrl || "";
  $("#s-custom-url").value = s.customUrl || "";
  $("#s-effort").value = s.effort;
  const ai = AI();
  const ready = AI_PROVIDERS.filter(([v]) => ai[v]).map(([, l]) => l.split(" (")[0]);
  $("#ai-status").textContent = `Set up on this PC: ${ready.length ? ready.join(", ") : "none"} · editor → ${ai.editor ? ai.editor_label : "offline rules"} · vision → ${ai.vision ? ai.vision_label : "off"}`;
  $("#s-workers").value = s.workers;
  $("#s-limit").value = s.limitGb;
  $("#s-frontier").value = s.frontierDir || "";
  $("#s-fpy").value = s.frontierPython || "";
  const f = (state.info && state.info.frontier) || {};
  $("#frontier-status").innerHTML = f.dir ? `Using <b>${f.dir}</b> · engine ${f.engine ? "✓" : "missing"} · .env ${f.env ? "✓ (its keys are used here too)" : "missing — add Frontier's keys to its .env"} · assets ${f.assets ? "✓" : "—"} · ${state.info.styles.filter((x) => x.engine === "frontier").length} styles`
    : "No Frontier folder yet. Browse to your Frontier folder, or download it from the Drive (code, styles, samples; never its .env).";
  if (state.doctor) paintDoctor();
}
$("#btn-ws").addEventListener("click", async () => {
  const r = await S.pick({ properties: ["openDirectory", "createDirectory"] });
  if (r) { $("#s-ws").value = r[0]; }
});
$("#btn-py").addEventListener("click", async () => {
  const r = await S.pick({ properties: ["openFile"] });
  if (r) $("#s-py").value = r[0];
});
$("#btn-save-settings").addEventListener("click", async () => {
  state.settings = await S.saveSettings({
    workspace: $("#s-ws").value, python: $("#s-py").value,
    workers: Number($("#s-workers").value) || 4, limitGb: Number($("#s-limit").value) || 1.0,
    upload: $("#f-upload").checked, aiQa: $("#f-qa").checked,
    frontierDir: $("#s-frontier").value.trim(), frontierPython: $("#s-fpy").value.trim(),
  });
  toast("Settings saved");
  await loadInfo();
  renderCreate();
  doctor(false);
});
$("#btn-save-ai").addEventListener("click", async () => {
  state.settings = await S.saveSettings({
    aiEditor: $("#s-editor").value, aiVision: $("#s-vision").value, aiEditorModel: $("#s-editor-model").value.trim(),
    aiVisionModel: $("#s-vision-model").value.trim(), antigravityUrl: $("#s-agy-url").value.trim(), customUrl: $("#s-custom-url").value.trim(),
    effort: $("#s-effort").value,
  });
  await loadInfo();
  renderSettings();
  renderSideStatus();
  renderCreate();
  const ai = AI();
  toast(`AI editor: ${ai.editor ? ai.editor_label : "offline rules"} · AI vision: ${ai.vision ? ai.vision_label : "off"}`);
});
$("#btn-setup").addEventListener("click", () => {
  taskRun("task_setup", "Install / repair engine", ["setup"]);
  go("niches");
  toast("Installing the engine (Python packages, Chromium, FFmpeg). Progress is on Niches & assets.");
});
$("#btn-doctor").addEventListener("click", () => doctor(true));
$("#btn-frontier").addEventListener("click", async () => { const r = await S.pick({ properties: ["openDirectory"] }); if (r) $("#s-frontier").value = r[0]; });
$("#btn-frontier-fetch").addEventListener("click", () => { taskRun("task_frontier", "Download Frontier", ["frontier-fetch"]); go("niches"); toast("Downloading Frontier (code, styles, samples). Progress is on Niches & assets."); });
$("#btn-frontier-open").addEventListener("click", () => {
  taskRun("task_frontier_app", "Frontier app", ["frontier-open"]);
  const t = setInterval(() => { const r = state.runs.find((x) => x.id === "task_frontier_app"); const a = r && r.artifacts.find((x) => x.kind === "link");
    if (a) { clearInterval(t); S.external(a.path); } if (r && r.status !== "running") clearInterval(t); }, 1000);
  toast("Starting Frontier's own app…");
});
$("#btn-frontier-kits").addEventListener("click", () => {
  const k = $("#s-kit").value;
  taskRun("task_kit_" + k, "Kit preview " + k, ["frontier-kit", "--kit", k]);
  go("niches");
});

async function doctor(show) {
  const r = await S.query(["doctor"]);
  if (!r.ok) { state.doctorOk = false; state.doctor = [{ name: "Python backend", ok: false, detail: r.error, fix: "Settings → Python path, then Install / repair" }]; }
  else { state.doctor = r.data.checks; state.doctorOk = r.data.checks.filter((c) => !c.optional).every((c) => c.ok); }
  renderSideStatus();
  paintDoctor();
  if (show) toast(state.doctorOk ? "Engine ready" : "Some parts are missing — see System check", !state.doctorOk);
}
function paintDoctor() {
  $("#doctor").replaceChildren(...(state.doctor || []).map((c) => h("div", { class: "check" }, h("span", { class: "dot " + (c.ok ? "ok" : c.optional ? "warn" : "bad") }), c.name,
    h("span", { class: "d", title: c.ok ? c.detail : c.fix }, c.ok ? c.detail : c.fix))));
}

boot();
