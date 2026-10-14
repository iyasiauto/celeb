/* scenes_emerge.js - Emerge X "Documentary" (New Style 3): the pieces of its look that sit on real footage.

   The calm serif graphics (dateline, number, chart, timeline, quote, pivot, question, social, card, step) are
   Frontier's documentary graphics (scenes_emerge-documentary.js, drawn through docu/scenes_frontier.js). This file
   adds what EDITING-STYLE.md specifies on top of them, measured in px at 1080p:

     overlay emname    a person's name: caps bottom-left, a gold rule, the role in serif italic, a soft blurred shade
     overlay emplace   a place / date stamp, top-left, a short gold rule, a detail line
     overlay emfigure  a figure counting up in 9 eased steps, bottom-left, its unit under a gold rule
     overlay emphrase  a key term (one or two a video): dark caps on a gold box that wipes open
     emmatch           the match cut: 6-10 real photos of the main person, the face on one spot every time, a white
                       flash on every cut, each photo pushing in 4.5 %, the last held with a 7 % push
     emtextcut         the text match cut: 3-5 punches of 1-4 words in caps over hard cuts of real photos (darkened
                       to 62 %), a red / cyan split snapping shut, a flash on every cut, the last line held
     empage            the real headline page: a tilted browser window with the real address rises in, the camera
                       pushes in on the headline, a yellow marker sweeps the marked lines as they are said

   Fonts (template.json theme_def): EmSerif / EmSerifI = EB Garamond, EmCond = Roboto Condensed, EmDisplay = Inter
   Display Black, EmBody = Inter SemiBold. Colours: cream #F3EEE4, gold #E3B25B.
*/
"use strict";

const EM = { cream: "#F3EEE4", gold: PAL.gold || "#E3B25B", ink: "#121212", sub: "#F2EDE6", marker: "rgba(242,208,39,.86)" };

/* label timing: in over 0.26 s from `at`, out over 0.32 s at `out` (default 3.6 s on screen) */
function emAlpha(t, at, out) {
  return eOut(seg(t, at, 0.26)) * (1 - seg(t, out, 0.32));
}

OVERLAYS.emname = (o, root) => {
  const at = o.at != null ? o.at : 0.3, out = o.out != null ? o.out : at + 3.6;
  const wrap = el("div", "abs", root, { left: "0", top: "0", width: W + "px", height: H + "px", opacity: 0 });
  el("div", "abs", wrap, { left: "40px", top: "720px", width: "1040px", height: "260px", background: "rgba(0,0,0,.4)",
    filter: "blur(46px)", borderRadius: "60px" });
  const nm = el("div", "abs", wrap, { left: "120px", top: "760px", font: "700 62px 'EmCond'", letterSpacing: "2px",
    color: "#FFFFFF", textTransform: "uppercase", whiteSpace: "nowrap", textShadow: "0 2px 3.6px rgba(0,0,0,.75)" }, esc(o.name || ""));
  const rule = el("div", "abs", wrap, { left: "120px", top: "846px", width: "128px", height: "5px", background: EM.gold });
  const rl = o.role ? el("div", "abs", wrap, { left: "122px", top: "860px", font: "italic 400 44px 'EmSerifI'", color: EM.sub,
    whiteSpace: "nowrap", textShadow: "0 1.5px 3px rgba(0,0,0,.7)" }, esc(o.role)) : null;
  return t => {
    setO(wrap, emAlpha(t, at, out));
    const p = eOut5(seg(t, at, 0.42));
    setT(nm, (1 - p) * -24, 0);
    css(rule, "clipPath", `inset(0 ${((1 - p) * 100).toFixed(1)}% 0 0)`);
    if (rl) setO(rl, eOut(seg(t, at + 0.15, 0.4)));
  };
};

OVERLAYS.emplace = (o, root) => {
  const at = o.at != null ? o.at : 0.3, out = o.out != null ? o.out : at + 3.6;
  const wrap = el("div", "abs", root, { left: "0", top: "0", width: W + "px", height: "320px", opacity: 0 });
  el("div", "abs", wrap, { left: "40px", top: "40px", width: "900px", height: "220px", background: "rgba(0,0,0,.32)",
    filter: "blur(44px)", borderRadius: "60px" });
  el("div", "abs", wrap, { left: "120px", top: "138px", width: "30px", height: "5px", background: EM.gold });
  const tx = el("div", "abs", wrap, { left: "166px", top: "100px", font: "700 62px 'EmCond'", letterSpacing: "5px",
    color: "#FFFFFF", textTransform: "uppercase", whiteSpace: "nowrap", textShadow: "0 2px 3.6px rgba(0,0,0,.75)" }, esc(o.text || o.place || ""));
  const sub = (o.sub || o.date) ? el("div", "abs", wrap, { left: "168px", top: "176px", font: "italic 400 40px 'EmSerifI'",
    color: EM.sub, whiteSpace: "nowrap", textShadow: "0 1.5px 3px rgba(0,0,0,.7)" }, esc(o.sub || o.date)) : null;
  return t => {
    setO(wrap, emAlpha(t, at, out));
    setT(tx, (1 - eOut5(seg(t, at, 0.42))) * -22, 0);
    if (sub) setO(sub, eOut(seg(t, at + 0.2, 0.4)));
  };
};

OVERLAYS.emfigure = (o, root) => {
  const at = o.at != null ? o.at : 0.3, out = o.out != null ? o.out : at + 3.6;
  const wrap = el("div", "abs", root, { left: "0", top: "0", width: W + "px", height: H + "px", opacity: 0 });
  el("div", "abs", wrap, { left: "40px", top: "640px", width: "980px", height: "340px", background: "rgba(0,0,0,.4)",
    filter: "blur(46px)", borderRadius: "60px" });
  const fig = el("div", "abs", wrap, { left: "120px", top: "690px", font: "700 132px 'EmCond'", color: "#FFFFFF",
    whiteSpace: "nowrap", textShadow: "0 2.4px 5px rgba(0,0,0,.75)", fontVariantNumeric: "lining-nums tabular-nums" }, "");
  const rule = el("div", "abs", wrap, { left: "124px", top: "850px", width: "60px", height: "4px", background: EM.gold });
  el("div", "abs", wrap, { left: "124px", top: "872px", font: "600 40px 'EmCond'", letterSpacing: ".12em", color: EM.sub,
    textTransform: "uppercase", whiteSpace: "nowrap", textShadow: "0 1.5px 3px rgba(0,0,0,.7)" }, esc(o.label || ""));
  const target = String(o.value == null ? "" : o.value);
  const num = parseFloat(target.replace(/[^\d.]/g, ""));
  return t => {
    setO(wrap, emAlpha(t, at, out));
    /* figures of 10 or more count up in 9 eased steps over 0.6 s */
    let p = 1;
    if (num >= 10) p = Math.round(eOut(seg(t, at, 0.6)) * 9) / 9;
    const s = num >= 10 ? countText(target, p) : target;
    if (fig._s !== s) { fig.textContent = s; fig._s = s; }
    css(rule, "clipPath", `inset(0 ${((1 - eOut(seg(t, at + 0.1, 0.4))) * 100).toFixed(1)}% 0 0)`);
  };
};

OVERLAYS.emphrase = (o, root) => {
  const at = o.at != null ? o.at : 0.3, out = o.out != null ? o.out : at + 3.6;
  const box = el("div", "abs", root, { left: "136px", top: "858px", background: EM.gold, color: EM.ink, padding: "10px 26px 8px",
    font: "700 66px 'EmCond'", letterSpacing: "1px", textTransform: "uppercase", whiteSpace: "nowrap", opacity: 0 }, esc(o.text || ""));
  return t => {
    setO(box, 1 - seg(t, out, 0.32));
    const p = eOut(seg(t, at, 0.38));
    css(box, "clipPath", `inset(0 ${((1 - p) * 100).toFixed(1)}% 0 0)`);
    if (p > 0) setO(box, 1 - seg(t, out, 0.32));
  };
};

/* ---- the match cut: the main person, the face on one spot every time ------------------------------------ */
SCENES.emmatch = async (s, root) => {
  const photos = (s.photos || []).slice(0, 10);
  const n = Math.max(1, photos.length), D = s.duration || 4.6;
  const hold = Math.min(1.6, D * 0.32), each = (D - hold) / Math.max(1, n - 1);
  const FX = 960, FY = 470, FH = s.faceSize || 330;              // where the face lands and how tall it is
  const layers = photos.map((p, i) => {
    const g = el("div", "full", root, { visibility: "hidden", overflow: "hidden", background: "#000" });
    const bg = pic(p.img, g, { left: "-60px", top: "-40px", width: (W + 120) + "px", height: (H + 80) + "px", objectFit: "cover",
      filter: "blur(28px) brightness(.45) saturate(.8)" });
    const fr = el("div", "abs", g, { left: "0", top: "0", width: W + "px", height: H + "px", transformOrigin: `${FX}px ${FY}px` });
    const im = pic(p.img, fr, { position: "absolute", left: "0", top: "0" });
    return { g, fr, im, face: p.face || [0.5, 0.38, 0.28] };
  });
  await Promise.all(WAITS);
  /* place each portrait so its face (x, y, height as fractions of the photo) sits on (FX, FY) at FH px */
  layers.forEach(L => {
    const iw = L.im.naturalWidth || 1600, ih = L.im.naturalHeight || 1000;
    const sc = FH / Math.max(40, L.face[2] * ih);
    const w = iw * sc, h = ih * sc;
    Object.assign(L.im.style, { width: w + "px", height: h + "px", left: (FX - L.face[0] * w) + "px", top: (FY - L.face[1] * h) + "px",
      boxShadow: "0 30px 80px rgba(0,0,0,.6)" });
  });
  const flash = el("div", "full", root, { background: "#fff", opacity: 0 });
  vignette(root, 0.45, 55);
  return t => {
    const k = Math.min(n - 1, Math.floor(t / each));
    layers.forEach((L, i) => vis(L.g, i === k));
    const L = layers[k];
    const t0 = k * each;
    const last = k === n - 1;
    const p = last ? eInOut(seg(t, t0, D - t0)) * 0.07 : ((t - t0) / each) * 0.045;
    setT(L.fr, 0, 0, 1 + p);
    const since = t - t0;
    setO(flash, k > 0 || t > 0.05 ? Math.max(0, 0.92 * (1 - since / 0.13)) : 0);
    if (last) setO(L.g, 1 - seg(t, D - 0.3, 0.3));
  };
};

/* ---- the text match cut ------------------------------------------------------------------------------- */
SCENES.emtextcut = async (s, root) => {
  const lines = (s.lines || []).slice(0, 5), photos = s.photos || [];
  const n = Math.max(1, lines.length), D = s.duration || 5.0;
  const hold = Math.min(1.6, D * 0.3), each = (D - hold) / Math.max(1, n - 1);
  const shots = lines.map((ln, i) => {
    const g = el("div", "full", root, { visibility: "hidden", overflow: "hidden", background: "#000" });
    const im = pic(photos.length ? photos[i % photos.length] : s.img, g, { left: "-40px", top: "-24px", width: (W + 80) + "px",
      height: (H + 48) + "px", objectFit: "cover", filter: "brightness(.62) saturate(.85)" });
    const rule = el("div", "abs", g, { left: "132px", top: "382px", width: "120px", height: "6px", background: EM.gold });
    const tx = el("div", "abs", g, { left: "132px", top: "410px", width: "1600px", font: "900 150px 'EmDisplay'", color: "#FFFFFF",
      textTransform: "uppercase", lineHeight: "1.0", letterSpacing: "-.01em" }, esc(ln));
    return { g, im, tx };
  });
  const flash = el("div", "full", root, { background: "#fff", opacity: 0 });
  return t => {
    const k = Math.min(n - 1, Math.floor(t / each));
    shots.forEach((S, i) => vis(S.g, i === k));
    const S = shots[k], since = t - k * each;
    const off = Math.max(0, 14 * (1 - since / 0.18));                          /* the red / cyan split snapping shut */
    css(S.tx, "textShadow", off > 0.2 ? `${off}px 0 rgba(255,40,40,.85), ${-off}px 0 rgba(40,220,255,.85)` : "none");
    setT(S.im, 0, 0, 1 + 0.03 * (since / Math.max(0.5, each)));
    setO(flash, Math.max(0, 0.92 * (1 - since / 0.13)));
    if (k === n - 1) setO(S.tx, 1 - seg(t, D - 0.5, 0.5));
  };
};

/* ---- the real headline page ---------------------------------------------------------------------------- */
SCENES.empage = async (s, root) => {
  const D = s.duration || 6.5, move = s.move || "window";
  const g = el("div", "full", root, { background: "radial-gradient(ellipse at 50% 40%, #2A2621 0%, #15130F 60%, #0A0907 100%)" });
  const cam = el("div", "full", root, { transformOrigin: "50% 40%" });
  const win = el("div", "abs", cam, { left: "260px", top: "120px", width: "1400px", background: "#FFFFFF", borderRadius: move === "window" ? "14px" : "2px",
    boxShadow: "0 50px 120px rgba(0,0,0,.65)", overflow: "hidden" });
  if (move === "window") {
    const bar = el("div", "", win, { height: "58px", background: "#ECECEC", display: "flex", alignItems: "center", padding: "0 22px", gap: "10px" });
    ["#FF5F57", "#FEBC2E", "#28C840"].forEach(c => el("div", "", bar, { width: "16px", height: "16px", borderRadius: "50%", background: c }));
    el("div", "", bar, { marginLeft: "24px", flex: "1", height: "34px", borderRadius: "17px", background: "#FFFFFF", font: "600 20px 'EmBody'",
      color: "#555", lineHeight: "34px", padding: "0 18px", whiteSpace: "nowrap", overflow: "hidden" }, esc(s.url || ""));
  }
  const body = el("div", "", win, { position: "relative" });
  const im = pic(s.img, body, { position: "relative", display: "block", width: "1400px", height: "auto",
    filter: move === "scan" ? "grayscale(.3) contrast(1.08)" : "none" });
  const blurIm = pic(s.img, body, { position: "absolute", left: "0", top: "0", width: "1400px", height: "auto", filter: "blur(5px)", opacity: 0 });
  const marks = (s.marks || []).map(m => {
    const b = m.box || m;
    const d = el("div", "abs", body, { background: EM.marker, mixBlendMode: "multiply", left: (b[0] * 100) + "%", top: (b[1] * 100) + "%",
      width: ((b[2] - b[0]) * 100) + "%", height: ((b[3] - b[1]) * 100) + "%", clipPath: "inset(0 100% 0 0)" });
    return { d, at: Number(m.at != null ? m.at : 1.3), dur: Number(m.dur || 0.7) };
  });
  const sheen = el("div", "abs", win, { left: "-40%", top: "0", width: "30%", height: "100%", background:
    "linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.35) 50%, rgba(255,255,255,0) 100%)" });
  const src = s.source ? el("div", "abs", root, { left: "132px", bottom: "64px", font: "400 23px 'EmCond'", letterSpacing: ".16em",
    color: "rgba(243,238,228,.72)", textTransform: "uppercase", whiteSpace: "nowrap" }, esc("SOURCE: " + s.source)) : null;
  vignette(root, 0.5, 50);
  await Promise.all(WAITS);
  /* the headline region (fractions of the page) the camera pushes towards */
  const focus = s.focus || (s.marks && s.marks[0] && (s.marks[0].box || s.marks[0])) || [0.1, 0.1, 0.9, 0.3];
  /* the page sinks out of focus around the headline: the blurred copy has a hole where the marked lines are */
  const all = (s.marks || []).map(m => m.box || m).concat([focus]);
  const hx0 = Math.max(0, Math.min(...all.map(b => b[0])) - 0.02) * 100, hy0 = Math.max(0, Math.min(...all.map(b => b[1])) - 0.02) * 100;
  const hx1 = Math.min(1, Math.max(...all.map(b => b[2])) + 0.02) * 100, hy1 = Math.min(1, Math.max(...all.map(b => b[3])) + 0.02) * 100;
  blurIm.style.clipPath = `polygon(evenodd, 0% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, ${hx0}% ${hy0}%, ${hx0}% ${hy1}%, ${hx1}% ${hy1}%, ${hx1}% ${hy0}%, ${hx0}% ${hy0}%)`;
  return t => {
    const rise = eOut5(seg(t, 0, 0.9));
    const tilt = move === "window" ? -4 : move === "paper" ? 3 : 0;
    setT(win, 0, (1 - rise) * 380, 1, tilt * (1 - 0.6 * rise));
    setO(win, Math.min(1, rise * 2));
    const push = eInOut(seg(t, 0.6, D - 0.6));
    const fx = (focus[0] + focus[2]) / 2, fy = (focus[1] + focus[3]) / 2;
    const hgt = im.offsetHeight || 900;
    const px = (0.5 - fx) * 1400 * 0.35 * push, py = (0.35 - fy) * hgt * 0.35 * push;
    setT(cam, px, py, 1 + 0.35 * push);
    setO(blurIm, 0.85 * seg(t, 1.6, 0.8));
    marks.forEach(M => css(M.d, "clipPath", `inset(0 ${((1 - eInOut(seg(t, M.at, M.dur))) * 100).toFixed(1)}% 0 0)`));
    marks.forEach(M => { M.d.style.zIndex = 2; });
    const fl = seg(t, 0.85, 0.2) * (1 - seg(t, 1.05, 0.2));                 /* the red-cyan flicker as it lands */
    css(win, "filter", fl > 0.02 ? `drop-shadow(${6 * fl}px 0 0 rgba(255,40,40,.5)) drop-shadow(${-6 * fl}px 0 0 rgba(40,220,255,.5))` : "none");
    setT(sheen, (seg(t, 1.0, 1.4)) * 2400, 0);
    if (src) setO(src, eOut(seg(t, 1.2, 0.5)));
  };
};
