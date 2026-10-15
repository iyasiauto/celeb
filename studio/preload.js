// The only bridge between the window and the system: a small, explicit API.
const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("studio", {
  settings: () => ipcRenderer.invoke("settings:get"),
  saveSettings: (patch) => ipcRenderer.invoke("settings:set", patch),
  secrets: () => ipcRenderer.invoke("secrets:status"),
  setSecret: (name, value) => ipcRenderer.invoke("secrets:set", name, value),
  query: (args) => ipcRenderer.invoke("py:query", args),
  startTask: (id, args) => ipcRenderer.invoke("task:start", id, args),
  cancelTask: (id) => ipcRenderer.invoke("task:cancel", id),
  onTask: (fn) => ipcRenderer.on("task:event", (_e, payload) => fn(payload)),
  writeJob: (job) => ipcRenderer.invoke("job:write", job),
  runs: () => ipcRenderer.invoke("runs:get"),
  saveRuns: (runs) => ipcRenderer.invoke("runs:set", runs),
  pick: (opts) => ipcRenderer.invoke("dialog:open", opts),
  stat: (p) => ipcRenderer.invoke("file:stat", p),
  open: (p) => ipcRenderer.invoke("shell:open", p),
  show: (p) => ipcRenderer.invoke("shell:show", p),
  external: (url) => ipcRenderer.invoke("shell:external", url),
  copy: (text) => ipcRenderer.invoke("clipboard:write", text),
});
