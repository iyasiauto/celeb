/* scenes_example.js - a template's own scene code. Loaded automatically when a video uses this template.
   Every helper of docu/engine.js is available: el, pic, setT, setO, seg, eOut, PAL, FONTS, W, H, SCENES, OVERLAYS ... */
"use strict";

SCENES.exhead = async (s, root) => {
  paperGround(root, "dark");
  const t = el("div", "abs", root, { left: "140px", top: "430px", font: `110px 'Anton'`, color: PAL.cream }, esc(s.title || ""));
  const k = el("div", "abs", root, { left: "146px", top: "380px", font: "30px 'BarlowB'", letterSpacing: ".3em",
    color: PAL.mustard, textTransform: "uppercase" }, esc(s.kicker || ""));
  return tt => { const a = eOut(seg(tt, 0.3, 0.8)); setO(t, a); setT(t, 0, (1 - a) * 30); setO(k, eOut(seg(tt, 0.1, 0.6))); };
};
