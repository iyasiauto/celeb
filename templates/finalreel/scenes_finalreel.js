/* scenes_finalreel.js - "Final Reel": childhood nostalgia + familiar faces + tragic endings.

   A film-archive memorial: charcoal and ivory, a muted gold for what they were known for, one crimson for the
   ending. Names in a high-contrast serif (Playfair), labels in condensed caps (Barlow), dates on a typewriter.
   Photographs sit in ivory film frames with sprocket holes; the ground is the same photograph, blurred and dark.

   Scenes
   castcard   who this is: framed portrait, rank, name wiping in, the role they are remembered for, years
   ageclock   the age they died at, counting up, with the date and one line
   memoriam   the closing card: black-and-white portrait in an arch, name, years, one line
   rollcall   a wall of faces filling in one by one (intro / outro / "how many do you remember")
   lifeline   a life on one line: born -> roles -> the end, each marker on its word, ages under it
   Overlays
   reelframe  a clip shown inside an ivory film frame on the charcoal ground (render: clip "inset")
   nameplate  who is on screen: name + role, lower left
*/
"use strict";

const FR = {
  coal: PAL.ink || "#121110", ivory: PAL.cream || "#EDE6D6", gold: PAL.gold || "#C9A45C",
  crimson: PAL.red || "#A3262A", ash: PAL.ash || "#8E887E", film: "#F1EBDD",
};

/* the photograph itself, blurred and darkened, as the ground (prep makes <img>_blur.jpg); else charcoal */
function frGround(root, img, dim) {
  if (img) {
    const g = pic(img.replace(/\.jpg$/, "_blur.jpg"), root, { left: "-40px", top: "-40px", width: (W + 80) + "px", height: (H + 80) + "px", objectFit: "cover" });
    el("div", "full", root, { background: `rgba(14,13,12,${dim != null ? dim : 0.74})` });
    vignette(root, 0.7);
    return g;
  }
  el("div", "full", root, { background: "radial-gradient(ellipse at 50% 42%, #2a2622 0%, #151311 58%, #0a0908 100%)" });
  vignette(root, 0.6);
  return null;
}
/* projector flicker: a faint warm light that breathes */
function frFlicker(root, amt) {
  const f = el("div", "full", root, { background: "radial-gradient(ellipse at 50% 40%, rgba(255,226,170,.10) 0%, rgba(0,0,0,0) 60%)", mixBlendMode: "screen" });
  return t => setO(f, (amt || 1) * (0.75 + 0.25 * Math.sin(t * 17.3) * Math.sin(t * 5.1 + 1.3)));
}
/* an ivory film frame with sprocket holes; returns {box, inner} - put a picture in inner */
function frFrame(parent, x, y, w, h, opts) {
  const o = opts || {};
  const pad = o.pad || 26, sp = o.sprocket !== false;
  const box = el("div", "abs", parent, { left: x + "px", top: y + "px", width: w + "px", height: h + "px", background: FR.film,
    boxShadow: "0 40px 90px rgba(0,0,0,.65), 0 4px 14px rgba(0,0,0,.4)", transformOrigin: "50% 50%" });
  if (sp) {
    for (const side of ["left", "right"]) {
      const strip = el("div", "abs", box, { [side]: "6px", top: "10px", bottom: "10px", width: (pad - 12) + "px",
        background: `repeating-linear-gradient(180deg, rgba(20,18,16,.85) 0 12px, rgba(0,0,0,0) 12px 30px)` });
      strip.style.borderRadius = "2px";
    }
  }
  const inner = el("div", "abs", box, { left: (sp ? pad + 4 : pad) + "px", top: pad + "px", right: (sp ? pad + 4 : pad) + "px",
    bottom: (o.foot || pad) + "px", overflow: "hidden", background: "#0c0b0a" });
  if (o.label) el("div", "abs", box, { left: (pad + 8) + "px", bottom: "12px", font: "22px 'Mono'", color: "rgba(30,28,26,.75)",
    letterSpacing: ".08em", whiteSpace: "nowrap" }, esc(o.label));
  return { box, inner };
}
/* a picture covering a box (bw x bh px), with a slow push; sized with width/height, not a scaled transform */
function frCover(inner, img, fx, fy, bw, bh) {
  const im = pic(img, inner, { left: 0, top: 0, maxWidth: "none" });
  return (z) => {
    const W0 = bw || inner.clientWidth || 600, H0 = bh || inner.clientHeight || 800;
    const iw = im.naturalWidth || W0, ih = im.naturalHeight || H0;
    const k = Math.max(W0 / iw, H0 / ih) * (z || 1);
    const w = iw * k, h = ih * k;
    css(im, "width", w.toFixed(1) + "px"); css(im, "height", h.toFixed(1) + "px");
    setT(im, (W0 - w) * (fx != null ? fx : 0.5), (H0 - h) * (fy != null ? fy : 0.3), 1);
  };
}
function frRule(parent, x, y, w, color, thick) {
  const d = el("div", "abs", parent, { left: x + "px", top: y + "px", width: "0", borderTop: `${thick || 2}px solid ${color || FR.gold}` });
  return p => css(d, "width", (w * p).toFixed(1) + "px");
}
function wipeIn(node, p) { css(node, "clipPath", `inset(-20% ${((1 - p) * 100).toFixed(2)}% -20% 0)`); }

/* ------------------------------------------------------------------ castcard */
SCENES.castcard = async (s, root) => {
  frGround(root, s.img, 0.76);
  const fl = frFlicker(root, 1);
  const fw = s.fw || 600, fh = s.fh || 760;
  const F = frFrame(root, 190, (H - fh) / 2, fw, fh, { label: s.frameLabel || "" , foot: 56 });
  const draw = frCover(F.inner, s.img, s.fx, s.fy, fw - 2 * 30, fh - 26 - 56);
  const X = 190 + fw + 120, at = s.at != null ? s.at : 0.3;
  const rank = s.n != null ? el("div", "abs", root, { left: X + "px", top: "268px", font: "30px 'LabelB'", letterSpacing: ".42em",
    color: FR.gold, whiteSpace: "nowrap" }, esc(s.rankText || ("NO. " + String(s.n).padStart(2, "0")))) : null;
  const r0 = frRule(root, X, 318, 520, FR.gold, 2);
  const name = el("div", "abs", root, { left: X - 4 + "px", top: "336px", width: (W - X - 120) + "px", font: `${s.size || 112}px 'Reel'`,
    lineHeight: "1.02", color: FR.ivory, textShadow: "0 8px 40px rgba(0,0,0,.6)" }, esc(s.name || ""));
  const role = s.role ? el("div", "abs", root, { left: X + "px", top: (s.size || 112) * (s.lines || 1) + 360 + "px", width: (W - X - 140) + "px",
    font: "44px 'ReelI'", color: FR.gold, lineHeight: "1.2" }, esc(s.role)) : null;
  const yrs = s.years ? el("div", "abs", root, { left: X + "px", top: (s.size || 112) * (s.lines || 1) + 470 + "px", font: "46px 'Label'",
    letterSpacing: ".18em", color: FR.ivory, whiteSpace: "nowrap" }, esc(s.years)) : null;
  const age = s.age != null ? el("div", "abs", root, { left: X + "px", top: (s.size || 112) * (s.lines || 1) + 548 + "px", font: "30px 'LabelB'",
    letterSpacing: ".3em", color: FR.ivory, background: FR.crimson, padding: "8px 20px 6px", whiteSpace: "nowrap" }, esc("AGE " + s.age)) : null;
  const D = s.duration;
  return t => {
    fl(t);
    const a = eOut5(seg(t, 0, 0.9));
    setO(F.box, a); F.box.style.transform = `translateY(${((1 - a) * 60).toFixed(1)}px) rotate(${(s.tilt != null ? s.tilt : -2) * (0.6 + 0.4 * a)}deg)`;
    draw(lerp(1.0, s.zoom || 1.10, drift(cl(t / D, 0, 1))));
    if (rank) setO(rank, eOut(seg(t, at, 0.6)));
    r0(eInOut(seg(t, at + 0.1, 0.9)));
    const q = eOut(seg(t, at + 0.25, 0.9)); wipeIn(name, q); setT(name, (1 - q) * -16, 0);
    if (role) { const p = eOut(seg(t, s.roleAt != null ? s.roleAt : at + 0.9, 0.8)); setO(role, p); setT(role, 0, (1 - p) * 14); }
    if (yrs) { const p = eOut(seg(t, s.yearsAt != null ? s.yearsAt : at + 1.4, 0.8)); setO(yrs, p); }
    if (age) { const p = eOut5(seg(t, s.ageAt != null ? s.ageAt : at + 1.9, 0.5)); setO(age, p); age.style.transform = `scale(${(1.25 - 0.25 * p).toFixed(3)})`; age.style.transformOrigin = "0 50%"; }
  };
};

/* ------------------------------------------------------------------ ageclock */
SCENES.ageclock = async (s, root) => {
  frGround(root, s.img, 0.84);
  const fl = frFlicker(root, 1.2);
  const at = s.at != null ? s.at : 0.3;
  const kick = s.kicker ? el("div", "abs", root, { left: 0, width: W + "px", top: "250px", textAlign: "center", font: "32px 'LabelB'",
    letterSpacing: ".46em", color: FR.gold }, esc(s.kicker)) : null;
  const num = el("div", "abs", root, { left: 0, width: W + "px", top: "270px", textAlign: "center", font: `${s.size || 340}px 'Reel'`,
    lineHeight: "1", color: FR.ivory, textShadow: "0 10px 60px rgba(0,0,0,.6)" }, "0");
  const U = 300 + (s.size || 340) * 1.16;
  const unit = el("div", "abs", root, { left: 0, width: W + "px", top: U + "px", textAlign: "center",
    font: "40px 'LabelB'", letterSpacing: ".5em", color: FR.crimson }, esc(s.unit || "YEARS OLD"));
  const r = frRule(root, W / 2 - 260, U + 70, 520, "rgba(237,230,214,.35)", 1);
  const note = s.note ? el("div", "abs", root, { left: "260px", width: (W - 520) + "px", top: (U + 96) + "px",
    textAlign: "center", font: "46px 'ReelI'", color: FR.ivory, lineHeight: "1.25" }, esc(s.note)) : null;
  const date = s.date ? el("div", "abs", root, { left: 0, width: W + "px", top: "980px", textAlign: "center", font: "28px 'Mono'",
    letterSpacing: ".12em", color: FR.ash }, esc(s.date)) : null;
  const val = Number(s.value) || 0, cnt = s.countFor || 1.4;
  return t => {
    fl(t);
    if (kick) setO(kick, eOut(seg(t, at - 0.2, 0.7)));
    const p = eOut(seg(t, at, cnt));
    num.textContent = String(Math.round(val * p));
    setO(num, cl(seg(t, at, 0.25) * 1.0, 0, 1));
    num.style.transform = `scale(${(1.06 - 0.06 * eOut(seg(t, at, cnt + 0.4))).toFixed(4)})`;
    setO(unit, eOut(seg(t, at + cnt * 0.7, 0.6)));
    r(eInOut(seg(t, at + cnt * 0.8, 0.8)));
    if (note) { const q = eOut(seg(t, s.noteAt != null ? s.noteAt : at + cnt + 0.4, 0.9)); setO(note, q); setT(note, 0, (1 - q) * 14); }
    if (date) setO(date, eOut(seg(t, at + 0.6, 0.8)));
  };
};

/* ------------------------------------------------------------------ memoriam */
SCENES.memoriam = async (s, root) => {
  el("div", "full", root, { background: "radial-gradient(ellipse at 50% 38%, #24201c 0%, #110f0e 60%, #070606 100%)" });
  const glow = el("div", "full", root, { background: "radial-gradient(ellipse at 50% 34%, rgba(255,214,150,.16) 0%, rgba(0,0,0,0) 46%)", mixBlendMode: "screen" });
  const aw = s.aw || 520, ah = s.ah || 640, ax = (W - aw) / 2, ay = 96;
  const arch = el("div", "abs", root, { left: ax + "px", top: ay + "px", width: aw + "px", height: ah + "px", overflow: "hidden",
    borderRadius: `${aw / 2}px ${aw / 2}px 8px 8px`, border: `6px solid ${FR.film}`, boxShadow: "0 40px 100px rgba(0,0,0,.7)", background: "#111" });
  const draw = frCover(arch, s.img, s.fx, s.fy, aw - 12, ah - 12);
  arch.firstChild.style.filter = "grayscale(1) contrast(1.06) brightness(.96)";
  const name = el("div", "abs", root, { left: 0, width: W + "px", top: (ay + ah + 36) + "px", textAlign: "center", font: `${s.size || 78}px 'Reel'`,
    color: FR.ivory }, esc(s.name || ""));
  const yrs = el("div", "abs", root, { left: 0, width: W + "px", top: (ay + ah + 36 + (s.size || 78) + 14) + "px", textAlign: "center",
    font: "38px 'Label'", letterSpacing: ".34em", color: FR.gold }, esc(s.years || ""));
  const line = s.line ? el("div", "abs", root, { left: "300px", width: (W - 600) + "px", top: (ay + ah + 36 + (s.size || 78) + 76) + "px",
    textAlign: "center", font: "36px 'ReelI'", color: "rgba(237,230,214,.82)", lineHeight: "1.3" }, esc(s.line)) : null;
  const D = s.duration, at = s.at != null ? s.at : 0.2;
  return t => {
    setO(glow, 0.8 + 0.2 * Math.sin(t * 9.1) * Math.sin(t * 3.7 + 0.7));
    const a = eOut(seg(t, 0, 1.4)); setO(arch, a);
    draw(lerp(1.0, s.zoom || 1.07, drift(cl(t / D, 0, 1))));
    setO(name, eOut(seg(t, at + 0.6, 1.0)));
    setO(yrs, eOut(seg(t, at + 1.1, 1.0)));
    if (line) setO(line, eOut(seg(t, s.lineAt != null ? s.lineAt : at + 1.7, 1.0)));
    const fo = 1 - eInOut(seg(t, D - 0.8, 0.8)) * (s.fadeout ? 1 : 0);
    css(root, "opacity", fo.toFixed(3));
  };
};

/* ------------------------------------------------------------------ rollcall */
SCENES.rollcall = async (s, root) => {
  el("div", "full", root, { background: "#0d0c0b" });
  const imgs = s.imgs || [], n = imgs.length;
  const cols = s.cols || Math.ceil(Math.sqrt(n * 16 / 9 * 0.62)), rows = Math.ceil(n / cols);
  const gap = 10, tw = (W - 120 - gap * (cols - 1)) / cols, th = Math.min((H - 120 - gap * (rows - 1)) / rows, tw * 1.25);
  const top = (H - (th * rows + gap * (rows - 1))) / 2;
  const tiles = imgs.map((im, i) => {
    const c = i % cols, r = Math.floor(i / cols);
    const tile = el("div", "abs", root, { left: (60 + c * (tw + gap)) + "px", top: (top + r * (th + gap)) + "px", width: tw + "px", height: th + "px",
      overflow: "hidden", background: "#1a1816", outline: "1px solid rgba(237,230,214,.12)" });
    const p = pic(im, tile, { left: 0, top: 0, width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 22%" });
    p.style.filter = "grayscale(1) contrast(1.05) brightness(.82)";
    const lab = (s.names && s.names[i]) ? el("div", "abs", tile, { left: 0, right: 0, bottom: 0, padding: "18px 8px 6px",
      background: "linear-gradient(0deg, rgba(0,0,0,.85), rgba(0,0,0,0))", font: `${Math.max(15, Math.min(22, tw / 9))}px 'LabelB'`,
      letterSpacing: ".06em", color: FR.ivory, textAlign: "center", whiteSpace: "nowrap", overflow: "hidden" }, esc(s.names[i].toUpperCase())) : null;
    return { tile, p, lab };
  });
  const shade = el("div", "full", root, { background: "radial-gradient(ellipse at 50% 50%, rgba(8,7,6,.86) 0%, rgba(8,7,6,.55) 48%, rgba(8,7,6,.15) 100%)", opacity: 0 });
  const title = s.title ? el("div", "abs", root, { left: "120px", width: (W - 240) + "px", top: (s.titleY || 420) + "px", textAlign: "center",
    font: `${s.size || 96}px 'Reel'`, color: FR.ivory, lineHeight: "1.08", opacity: 0, textShadow: "0 8px 50px rgba(0,0,0,.8)" }, esc(s.title)) : null;
  const sub = s.sub ? el("div", "abs", root, { left: 0, width: W + "px", top: ((s.titleY || 420) + (s.size || 96) * 1.2 + 24) + "px", textAlign: "center",
    font: "34px 'LabelB'", letterSpacing: ".42em", color: FR.gold, opacity: 0 }, esc(s.sub)) : null;
  const fill = s.fillFor || 3.0, at = s.at != null ? s.at : 0.1, hi = new Set(s.color || []);
  const order = tiles.map((_, i) => i);
  if (s.shuffle !== false) { const R = rng(s.seed || 11); for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; } }
  const when = new Array(n); order.forEach((idx, k) => { when[idx] = at + fill * k / Math.max(1, n - 1); });
  const D = s.duration;
  return t => {
    tiles.forEach((T, i) => {
      const a = eOut(seg(t, when[i], 0.45)); setO(T.tile, a);
      T.p.style.transform = `scale(${(1.12 - 0.12 * a + 0.04 * cl(t / D, 0, 1)).toFixed(4)})`;
      if (hi.has(i)) { const c = eOut(seg(t, s.colorAt || at + fill + 0.3, 0.8)); T.p.style.filter = `grayscale(${(1 - c).toFixed(3)}) contrast(1.05) brightness(${(0.82 + 0.18 * c).toFixed(3)})`;
        T.tile.style.outline = `${(3 * c).toFixed(1)}px solid ${FR.crimson}`; }
    });
    if (title) { const ta = s.titleAt != null ? s.titleAt : at + fill + 0.2; setO(shade, eOut(seg(t, ta - 0.3, 0.9)));
      const q = eOut(seg(t, ta, 1.0)); setO(title, q); setT(title, 0, (1 - q) * 18);
      if (sub) setO(sub, eOut(seg(t, ta + 0.7, 0.9))); }
  };
};

/* ------------------------------------------------------------------ lifeline */
SCENES.lifeline = async (s, root) => {
  frGround(root, s.img, 0.86);
  const fl = frFlicker(root, 0.8);
  const x0 = 260, x1 = W - 200, y = 600;
  const b = Number(s.born), d = Number(s.died);
  const X = yr => x0 + (x1 - x0) * cl((yr - b) / Math.max(1, d - b), 0, 1);
  const name = s.name ? el("div", "abs", root, { left: x0 + "px", top: "200px", font: "70px 'Reel'", color: FR.ivory, whiteSpace: "nowrap" }, esc(s.name)) : null;
  const kick = el("div", "abs", root, { left: x0 + "px", top: "160px", font: "28px 'LabelB'", letterSpacing: ".42em", color: FR.gold }, esc(s.kicker || "A LIFE IN YEARS"));
  const base = el("div", "abs", root, { left: x0 + "px", top: y + "px", width: "0", height: "4px", background: FR.ivory });
  const end = el("div", "abs", root, { left: "0", top: y + "px", width: "0", height: "4px", background: FR.crimson });
  const ends = [[b, "BORN"], [d, "DIED"]].map(([yr, lab], k) => {
    const g = el("div", "abs", root, { left: (X(yr) - 120) + "px", top: (y + 34) + "px", width: "240px", textAlign: "center", opacity: 0 });
    el("div", "", g, { font: "26px 'LabelB'", letterSpacing: ".3em", color: k ? FR.crimson : FR.ash }, lab);
    el("div", "", g, { font: "58px 'Reel'", color: FR.ivory }, String(yr));
    const dot = el("div", "abs", root, { left: (X(yr) - 13) + "px", top: (y - 11) + "px", width: "26px", height: "26px", borderRadius: "50%",
      background: k ? FR.crimson : FR.ivory, opacity: 0 });
    return { g, dot };
  });
  const evs = (s.events || []).map((e, i) => {
    const up = i % 2 === 0;
    const x = X(Number(e.year));
    const stem = el("div", "abs", root, { left: (x - 1) + "px", top: (up ? y - 110 : y + 4) + "px", width: "2px", height: "0", background: FR.gold });
    const g = el("div", "abs", root, { left: (x - 170) + "px", top: (up ? y - 250 : y + 128) + "px", width: "340px", textAlign: "center", opacity: 0 });
    el("div", "", g, { font: "40px 'Reel'", color: FR.gold }, esc(String(e.year)));
    el("div", "", g, { font: "30px 'ReelI'", color: FR.ivory, lineHeight: "1.2" }, esc(e.label || ""));
    if (e.age != null) el("div", "", g, { font: "22px 'LabelB'", letterSpacing: ".3em", color: FR.ash, marginTop: "4px" }, "AGE " + e.age);
    return { e, stem, g, up };
  });
  const at = s.at != null ? s.at : 0.3, endAt = s.endAt != null ? s.endAt : at + 2.6 + evs.length * 0.6;
  return t => {
    fl(t);
    setO(kick, eOut(seg(t, at - 0.2, 0.7))); if (name) setO(name, eOut(seg(t, at, 0.8)));
    const reach = Math.max(eInOut(seg(t, at + 0.3, 1.6)) * 0.12, ...evs.map(v => seg(t, v.e.at != null ? v.e.at : 0, 0.8) > 0 ? (X(Number(v.e.year)) - x0) / (x1 - x0) * eOut(seg(t, v.e.at, 0.8)) : 0));
    const full = eInOut(seg(t, endAt - 0.6, 1.0));
    const r = Math.max(reach, full);
    css(base, "width", ((x1 - x0) * r).toFixed(1) + "px");
    setO(ends[0].g, eOut(seg(t, at + 0.3, 0.6))); setO(ends[0].dot, eOut(seg(t, at + 0.3, 0.4)));
    evs.forEach(v => { const q = eOut(seg(t, v.e.at != null ? v.e.at : 0, 0.7)); css(v.stem, "height", (106 * q).toFixed(1) + "px"); setO(v.g, q); });
    const e2 = eOut(seg(t, endAt, 0.6)); setO(ends[1].g, e2); setO(ends[1].dot, e2);
    /* the last stretch burns crimson when the end arrives */
    const lastX = evs.length ? X(Number(evs[evs.length - 1].e.year)) : x0;
    css(end, "left", lastX.toFixed(1) + "px"); css(end, "width", ((x1 - lastX) * e2).toFixed(1) + "px");
  };
};

/* ------------------------------------------------------------------ overlays */
/* the frame around a clip rendered with inset=[x, y, w, h]: charcoal ground outside, ivory film frame, caption */
OVERLAYS.reelframe = (o, root) => {
  const [x, y, w, h] = o.box || [300, 120, 1320, 742];
  const pad = 26;
  const g = "rgba(16,15,14,1)";
  el("div", "abs", root, { left: 0, top: 0, width: W + "px", height: (y - pad) + "px", background: g });
  el("div", "abs", root, { left: 0, top: (y + h + pad + 46) + "px", width: W + "px", height: (H - y - h - pad - 46) + "px", background: g });
  el("div", "abs", root, { left: 0, top: (y - pad) + "px", width: (x - pad - 8) + "px", height: (h + pad * 2 + 46) + "px", background: g });
  el("div", "abs", root, { left: (x + w + pad + 8) + "px", top: (y - pad) + "px", width: (W - x - w - pad - 8) + "px", height: (h + pad * 2 + 46) + "px", background: g });
  /* the ivory frame: four bars around the window, sprockets on the sides */
  const film = FR.film;
  el("div", "abs", root, { left: (x - pad - 8) + "px", top: (y - pad) + "px", width: (w + pad * 2 + 16) + "px", height: pad + "px", background: film });
  el("div", "abs", root, { left: (x - pad - 8) + "px", top: (y + h) + "px", width: (w + pad * 2 + 16) + "px", height: (pad + 46) + "px", background: film });
  for (const sx of [x - pad - 8, x + w]) {
    const bar = el("div", "abs", root, { left: sx + "px", top: (y - pad) + "px", width: (pad + 8) + "px", height: (h + pad * 2 + 46) + "px", background: film });
    el("div", "abs", bar, { left: "8px", top: "10px", bottom: "10px", width: (pad - 8) + "px",
      background: "repeating-linear-gradient(180deg, rgba(20,18,16,.85) 0 12px, rgba(0,0,0,0) 12px 30px)" });
  }
  el("div", "abs", root, { left: x + "px", top: y + "px", width: w + "px", height: h + "px", boxShadow: "inset 0 0 60px rgba(0,0,0,.55)" });
  if (o.caption) el("div", "abs", root, { left: (x + 4) + "px", top: (y + h + 10) + "px", font: "24px 'Mono'", color: "rgba(30,28,26,.82)",
    letterSpacing: ".08em", whiteSpace: "nowrap" }, esc(o.caption));
  if (o.right) el("div", "abs", root, { left: (x + w - 600) + "px", width: "596px", textAlign: "right", top: (y + h + 10) + "px", font: "24px 'Mono'",
    color: "rgba(30,28,26,.82)", letterSpacing: ".08em", whiteSpace: "nowrap" }, esc(o.right));
  if (o.name) {
    el("div", "abs", root, { left: (x - pad - 8) + "px", top: (y + h + pad + 66) + "px", font: "44px 'Reel'", color: FR.ivory, whiteSpace: "nowrap" }, esc(o.name));
    if (o.role) el("div", "abs", root, { left: (x - pad - 8) + "px", top: (y + h + pad + 122) + "px", font: "30px 'ReelI'", color: FR.gold, whiteSpace: "nowrap" }, esc(o.role));
  }
  return () => {};
};
OVERLAYS.nameplate = (o, root) => {
  const at = o.at != null ? o.at : 0.5;
  const sh = el("div", "full", root, { background: "linear-gradient(0deg, rgba(8,7,6,.72) 0%, rgba(8,7,6,0) 34%)", opacity: 0 });
  const box = el("div", "abs", root, { left: "110px", bottom: "92px" });
  const rule = el("div", "", box, { width: "0", borderTop: `2px solid ${FR.gold}`, marginBottom: "14px" });
  const nm = el("div", "", box, { font: `${o.size || 62}px 'Reel'`, color: FR.ivory, whiteSpace: "nowrap", textShadow: "0 4px 24px rgba(0,0,0,.7)" }, esc(o.name || ""));
  const rl = o.role ? el("div", "", box, { font: "32px 'ReelI'", color: FR.gold, whiteSpace: "nowrap", marginTop: "4px", textShadow: "0 3px 16px rgba(0,0,0,.7)" }, esc(o.role)) : null;
  return t => {
    setO(sh, eOut(seg(t, at - 0.2, 0.7)));
    css(rule, "width", (260 * eInOut(seg(t, at, 0.8))).toFixed(1) + "px");
    const q = eOut(seg(t, at + 0.15, 0.8)); wipeIn(nm, q);
    if (rl) setO(rl, eOut(seg(t, at + 0.6, 0.7)));
  };
};
