/* scenes_frontier.js - Frontier's graphics languages, native in the Docu engine.

   Frontier (the other studio) draws its graphics as one HTML page per scene: a look kit (DOSSIER, KINETIC, ATLAS,
   DEEP, NEWS, LEGEND, HUSTLE), the documentary graphics (docgfx) or the motion graphics (motion). Every page is a
   function of t alone - window.renderFrame(t) - the same contract as a Docu scene. So a template imported from
   Frontier (docu/tools/frontier_import.py) does not copy or rewrite those pages: its scenes file registers each
   page here with FRONTIER.page(id, {...}) and each scene type with

       SCENES.dossier_alert = FRONTIER.scene("dossier", "alert");

   and the page is drawn in an <iframe> on the stage, driven frame by frame from renderFrame(t). Fonts, pictures and
   props come from the kit folder (media/kit), so nothing is downloaded and nothing is embedded twice.

   Over footage: the same page can sit on a clip as an overlay (transparent, no ground):
       clip(..., overlays=[{"type": "frontier", "page": "frontline", "kind": "newsbar", "tag": "BREAKING", ...}])

   Pictures: any field that names a picture (".jpg", ".png", "kit:...") is turned into a URL the page can load;
   a scene's `img` becomes its ground (the blurred real picture behind docgfx lines, the footage still under a kit
   scene) unless it sets `ground` itself.
*/
"use strict";

const FRONTIER = (() => {
  const PAGES = {};
  const IMG = /\.(jpe?g|png|webp|gif|svg)$/i;
  const SKIP = new Set(["id", "t0", "type", "page", "overlays", "fx", "texture_png", "texture_opacity", "sfx", "footage_frame",
                        "frame_text", "frame_n", "audio"]);

  function fontCSS(fonts) {
    return (fonts || []).map(([fam, file, wt, st]) =>
      `@font-face{font-family:'${fam}';font-style:${st || "normal"};font-weight:${wt || "400"};` +
      `src:url('${CFG.kit}/fonts/${file}');font-display:block}`).join("\n");
  }
  /* every picture named anywhere in the scene -> a loadable URL; collects them so they are decoded before frame 0 */
  function urls(v, found) {
    if (typeof v === "string") {
      if (/^(data|https?):/.test(v)) return v;
      if (v.startsWith("kit:") || (IMG.test(v) && v.length < 600)) { const u = asset(v); found.push(u); return u; }
      return v;
    }
    if (Array.isArray(v)) return v.map(x => urls(x, found));
    if (v && typeof v === "object") { const o = {}; for (const k of Object.keys(v)) o[k] = urls(v[k], found); return o; }
    return v;
  }
  function preload(list) {
    return Promise.all(list.map(u => new Promise(res => {
      const i = new Image(); i.onload = () => i.decode().then(res, res); i.onerror = () => { console.warn("missing", u); res(); }; i.src = u;
    })));
  }

  /* the scene a Frontier page reads: the spec's own fields + the page's defaults for this type + palette, ground */
  function sceneOf(pg, type, spec) {
    const S = {};
    Object.assign(S, (pg.defaults && pg.defaults["*"]) || {}, (pg.defaults && pg.defaults[type]) || {});
    for (const k of Object.keys(spec)) if (!SKIP.has(k)) S[k] = spec[k];
    S.type = type;
    S.duration = Number(spec.duration || S.duration || 6);
    S.seed = S.seed || 7;
    if (pg.palette) S.palette = Object.assign({}, pg.palette, spec.palette || {});
    if (!S.ground && spec.img && pg.groundFromImg !== false && !S.paper) S.ground = spec.img;   /* a chart sits on its paper */
    if (!S.frame && spec.img) S.frame = spec.img;          /* the kits' still of the footage (a board, a wave, a monitor) */
    delete S.img;
    const found = [];
    const out = urls(S, found);
    return { S: out, pics: found };
  }

  /* draw one page in an iframe on `root`; resolves when the page has laid itself out (fonts + build) */
  function mount(pageId, type, spec, root, overlay) {
    const pg = PAGES[pageId];
    if (!pg) throw new Error("frontier page not registered: " + pageId);
    const { S, pics } = sceneOf(pg, type, spec);
    if (overlay) { S.overlay = true; delete S.ground; }
    const fr = el("iframe", "full", root, { border: "0", width: W + "px", height: H + "px", background: "transparent",
                                             overflow: "hidden", pointerEvents: "none" });
    fr.setAttribute("scrolling", "no");
    const json = JSON.stringify(S).replace(/</g, "\\u003c").split(String.fromCharCode(8232)).join(" ").split(String.fromCharCode(8233)).join(" ");
    let html = pg.html.replace("__FONTS__", () => fontCSS(pg.fonts))
      .replace("__SCENE__", () => json);   /* a function: "$4,200" must not read as a replacement pattern */
    const extra = (pg.css || "") + (overlay
      ? "html,body,#stage,#cam{background:transparent!important}#ground,#ground2,#shade,#vig{display:none!important}"
      : "");
    if (extra) html = html.replace("</head>", () => `<style>${extra}</style></head>`);
    let win = null;
    const ready = preload(pics).then(() => new Promise(res => { fr.onload = res; fr.srcdoc = html; }))
      .then(async () => {
        win = fr.contentWindow;
        for (let i = 0; i < 600 && !win.__ready; i++) await new Promise(r => setTimeout(r, 10));
        if (win.__err) console.warn(`frontier ${pageId}.${type}: ${win.__err}`);
        const d = fr.contentDocument;
        await Promise.all([...d.images].map(im => (im.complete ? im.decode().catch(() => {}) : new Promise(r => { im.onload = im.onerror = r; }))));
        await d.fonts.ready;
        try { win.renderFrame(0); } catch (e) { console.warn(e); }
      });
    const update = t => { if (win && win.renderFrame) { try { win.renderFrame(Math.max(0, t)); } catch (e) { /* a page error must not stop the render */ } } };
    return { ready, update };
  }

  return {
    pages: PAGES,
    /* FRONTIER.page(id, {html, fonts:[[family, file, weight, style]], palette, defaults:{type:{...}}, css}) */
    page(id, def) { PAGES[id] = def; },
    /* a scene type: the page fills the stage */
    scene(pageId, type) {
      return async (spec, root) => {
        /* a template with several pages for one type (motion graphics: one page per skin) names it in the spec */
        const m = mount(spec.page && PAGES[spec.page] ? spec.page : pageId, type, spec, root, false);
        await m.ready;
        return m.update;
      };
    },
    mount,
  };
})();

/* a Frontier graphic over footage (a clip or a photo): {"type": "frontier", "page": "frontline", "kind": "newsbar", ...} */
OVERLAYS.frontier = (o, root) => {
  const at = Number(o.at || 0);
  const m = FRONTIER.mount(o.page, o.kind, Object.assign({}, o, { duration: o.duration || (SCENE.duration - at) }), root, true);
  WAITS.push(m.ready);
  return t => m.update(t - at);
};
