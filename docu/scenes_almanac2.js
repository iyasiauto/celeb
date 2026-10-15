/* scenes_almanac2.js - the "almanac2" template: Heritage gazetteer, the almanac's second edition.

   Same calm, footage-led pacing as the almanac, a different book: a county atlas and land-survey
   gazetteer instead of a seed catalogue. Engraved caps (Cinzel) on a letterpress plate, high-contrast
   didone numerals (Playfair), Garamond body, a surveyor's pencil (Patrick Hand) for the notes, a
   ledger mono for figures, and a plat map with a township grid and square section markers.
   Cool slate ink on oatmeal paper; ochre, oxblood, verdigris, slate.

   Overlays (any scene, clips included):
   gzhead     Chapter heading over moving footage: a notched plate stamp with the chapter number, a
              kicker, an engraved title whose letter-spacing closes in, hairlines that open out from
              the middle, a pencil note. Animated, so on a clip it renders as a moving alpha layer.
   gztag      Place tag: the place engraved on a slate cartouche with a pencil note slipped under it.

   Scenes:
   gzcard     Key point on a ledger slip (punched holes, double keyline, ochre head band) over a photo.
   gzstat     One number stamped on a plate between two hairlines, with a pencil note.
   gzversus   Two columns compared row by row (population / settlements / districts), each value
              counting up on its own word, the leading side tinted.
   gzgiants   Giants against dots: one circle sized by its value beside a field of small dots that
              appear one by one while a counter runs.
   gzdivide   A district dividing: one cell inside a dashed boundary becomes two, three, ten.
   gzindex    Gazetteer index rows - name, dotted leader, figure - drawn in turn, one row highlighted.
   gzdelta    A decade of change: 2015 and 2025 either side of an arrow, with the difference stamped.
*/
"use strict";

const GZ = {
  ink: PAL.ink || "#1E2832", cream: PAL.cream || "#E8E2D0", slip: PAL.tagc || "#EFE9D9", sub: PAL.subc || "#4C5663",
  ochre: PAL.ochre || PAL.wheat || "#BE8A2C", oxblood: PAL.oxblood || PAL.barn || "#7A2F2A",
  verdigris: PAL.verdigris || PAL.field || "#38655C", slate: PAL.slate || PAL.denim || "#2C4760",
};
const PLATE_N = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV"];
const NOTCH = "polygon(0 9px, 9px 0, 100% 0, 100% calc(100% - 9px), calc(100% - 9px) 100%, 0 100%)";

/* oatmeal paper, ruled with a faint section grid */
function gzPaper(root, tone) {
  paperGround(root, "paper");
  el("div", "full", root, { background: `rgba(${PAL.paperWash || "234,228,211"},${tone != null ? tone : 0.62})` });
  el("div", "full", root, { background:
    "repeating-linear-gradient(0deg, rgba(30,40,50,.055) 0 1px, rgba(0,0,0,0) 1px 48px)," +
    "repeating-linear-gradient(90deg, rgba(30,40,50,.055) 0 1px, rgba(0,0,0,0) 1px 48px)," +
    "repeating-linear-gradient(0deg, rgba(30,40,50,.07) 0 1px, rgba(0,0,0,0) 1px 240px)," +
    "repeating-linear-gradient(90deg, rgba(30,40,50,.07) 0 1px, rgba(0,0,0,0) 1px 240px)" });
  el("div", "full", root, { background: `radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 56%, ${PAL.paperEdge || "rgba(40,50,62,.20)"} 100%)` });
}
/* a photograph under a cool dark wash */
function gzPhoto(root, s, dim) {
  const L = s.img ? photoLayer(root, Object.assign({ move: s.move || "in", zoom: s.zoom || 1.08 }, s)) : null;
  if (!L) paperGround(root, "dark");
  el("div", "full", root, { background: `rgba(14,19,26,${dim})` });
  vignette(root, 0.5);
  return L;
}
/* a thin hairline; returns a setter for 0..1. From the middle out when `mid` is set. */
function hair(parent, x, y, w, color, thick, mid) {
  const d = el("div", "abs", parent, { left: x + "px", top: y + "px", width: "0", height: "0",
    borderTop: `${thick || 2}px solid ${color || GZ.ink}` });
  return p => { css(d, "width", (w * p).toFixed(1) + "px"); if (mid) css(d, "left", (x + w * (1 - p) / 2).toFixed(1) + "px"); };
}
/* the notched plate stamp: "PLATE IV" or any short mark */
function plate(parent, text, opts) {
  const o = opts || {};
  const b = el("div", "abs", parent, { left: 0, top: 0, background: o.bg || GZ.ink, clipPath: NOTCH,
    padding: o.pad || "12px 22px 13px", whiteSpace: "nowrap" });
  if (o.kicker) el("div", "", b, { font: "20px 'Oswald'", letterSpacing: ".3em", color: "rgba(232,226,208,.72)",
    textTransform: "uppercase", marginBottom: "2px" }, esc(o.kicker));
  el("div", "", b, { font: `${o.size || 40}px 'Engr'`, letterSpacing: ".1em", color: o.color || GZ.cream, lineHeight: "1.02" }, esc(text));
  return b;
}
/* pencil note */
function pencil(parent, text, style) {
  return el("div", "abs", parent, Object.assign({ font: "34px 'Pencil'", color: GZ.sub, whiteSpace: "nowrap" }, style || {}), esc(text));
}
function gzSource(root, s, x, y, color) {
  return s.source ? el("div", "abs", root, { left: (x || 130) + "px", top: (y || 1000) + "px", font: "19px 'Oswald'", letterSpacing: ".2em",
    color: color || "rgba(232,226,208,.6)", textTransform: "uppercase" }, esc(s.source)) : null;
}

/* ------------------------------------------------------------------ overlays */
OVERLAYS.gzhead = (o, root) => {
  const at = o.at != null ? o.at : 0.4;
  const shade = el("div", "full", root, { background:
    "linear-gradient(90deg, rgba(10,14,20,.70) 0%, rgba(10,14,20,.42) 46%, rgba(10,14,20,0) 76%)," +
    "linear-gradient(0deg, rgba(10,14,20,.52) 0%, rgba(10,14,20,0) 48%)", opacity: 0 });
  const box = el("div", "abs", root, { left: (o.x || 132) + "px", bottom: (o.bottom || 148) + "px", width: (o.w || 1320) + "px" });
  /* top hairline pair, opening out from the left edge */
  const topRule = el("div", "", box, { position: "relative", height: "22px" });
  const r0 = hair(topRule, 2, 4, o.rule || 560, GZ.ochre, 2);
  const r1 = hair(topRule, 2, 11, o.rule || 560, "rgba(190,138,44,.5)", 1);
  const row = el("div", "", box, { position: "relative", height: o.n != null ? "104px" : "48px", marginTop: "14px" });
  const st = o.n != null ? plate(row, PLATE_N[o.n] || String(o.n), { kicker: o.plate || "plate", size: 42 }) : null;
  const kick = el("div", "abs", row, { left: st ? "190px" : "2px", top: st ? "34px" : "6px", font: "27px 'Oswald'", letterSpacing: ".34em",
    color: GZ.ochre, textTransform: "uppercase", whiteSpace: "nowrap" }, esc(o.kicker || ""));
  const title = el("div", "", box, { font: `${o.size || 86}px 'Engr'`, lineHeight: "1.08", color: GZ.cream, marginTop: "16px",
    textShadow: "0 6px 30px rgba(0,0,0,.5)" }, esc(o.title || ""));
  const sub = o.sub ? pencil(box, o.sub, { position: "relative", font: "38px 'Pencil'", color: "rgba(232,226,208,.9)", marginTop: "10px",
    textShadow: "0 3px 16px rgba(0,0,0,.6)", whiteSpace: "normal" }) : null;
  return t => {
    const D = (typeof SCENE !== "undefined" && SCENE.duration) || 8;
    const out = o.out != null ? o.out : D - 1.0;
    const fo = 1 - eInOut(seg(t, out, 0.9));
    setO(shade, eOut(seg(t, at - 0.2, 1.0)) * fo);
    r0(eInOut(seg(t, at, 1.0)) * fo); r1(eInOut(seg(t, at + 0.15, 1.0)) * fo);
    if (st) { const a = eOut(seg(t, at + 0.25, 0.6)); setO(st, a * fo); st.style.transform = `scale(${(1.14 - 0.14 * a).toFixed(3)})`; }
    setO(kick, eOut(seg(t, at + 0.5, 0.8)) * fo);
    /* engraved titles close their letter-spacing instead of rising */
    const q = eOut5(seg(t, at + 0.6, 1.3));
    setO(title, cl(q * 1.6, 0, 1) * fo);
    css(title, "letterSpacing", (0.26 - 0.24 * q).toFixed(3) + "em");
    setT(title, (1 - q) * -10, 0);
    if (sub) { const p = eOut(seg(t, at + 1.5, 0.9)); setO(sub, p * fo); setT(sub, (1 - p) * -14, 0); }
  };
};

OVERLAYS.gztag = (o, root) => {
  const at = o.at != null ? o.at : 0.6;
  const wrap = el("div", "abs", root, { left: (o.x != null ? o.x : 98) + "px", top: (o.y != null ? o.y : 876) + "px" });
  const band = el("div", "", wrap, { position: "relative", background: GZ.ink, clipPath: NOTCH, padding: "13px 30px 14px",
    boxShadow: "0 10px 26px rgba(10,14,20,.4)", whiteSpace: "nowrap" });
  el("div", "", band, { font: `${o.size || 32}px 'Engr'`, letterSpacing: ".12em", color: GZ.cream, textTransform: "uppercase" }, esc(o.text || ""));
  const slip = o.sub ? el("div", "", wrap, { position: "relative", marginLeft: "26px", marginTop: "-4px", background: GZ.slip,
    borderLeft: `4px solid ${GZ.ochre}`, padding: "7px 22px 8px", font: "30px 'Pencil'", color: GZ.ink,
    boxShadow: "0 8px 20px rgba(10,14,20,.3)", whiteSpace: "nowrap" }, esc(o.sub)) : null;
  return t => {
    const a = eOut(seg(t, at, 0.8)), fade = o.out != null ? 1 - seg(t, o.out, 0.6) : 1;
    setO(band, a * fade); setT(band, (1 - a) * -30, 0);
    if (slip) { const q = eOut(seg(t, at + 0.35, 0.7)); setO(slip, q * fade); setT(slip, 0, (1 - q) * -12); }
  };
};

/* ------------------------------------------------------------------ cards and figures */
SCENES.gzcard = async (s, root) => {
  const L = gzPhoto(root, s, s.dim != null ? s.dim : 0.6);
  const w = s.w || 1180;
  const slip = el("div", "abs", root, { left: (W - w) / 2 + "px", top: 0, width: w + "px", background: GZ.slip,
    boxShadow: "0 22px 60px rgba(10,14,20,.45)", padding: "62px 90px 66px", boxSizing: "border-box", opacity: 0 });
  el("div", "abs", slip, { left: 0, top: 0, width: "100%", height: "10px", background: GZ.ochre });
  el("div", "abs", slip, { left: "22px", top: "22px", right: "22px", bottom: "22px", border: `1px solid rgba(30,40,50,.28)` });
  el("div", "abs", slip, { left: "30px", top: "30px", right: "30px", bottom: "30px", border: `3px solid ${GZ.ink}` });
  const kick = s.kicker ? el("div", "", slip, { font: "26px 'Oswald'", letterSpacing: ".34em", color: GZ.oxblood,
    textTransform: "uppercase", marginBottom: "26px", textAlign: "center" }, esc(s.kicker)) : null;
  const lines = (s.lines || []).map(ln => ({ ln, d: el("div", "", slip, { font: `${ln.size || 62}px '${ln.font || "Engr"}'`,
    color: ln.color || GZ.ink, lineHeight: "1.22", marginTop: (ln.gap != null ? ln.gap : 16) + "px", textAlign: "center",
    letterSpacing: (ln.font || "Engr") === "Engr" ? ".02em" : "0" }, esc(ln.text)) }));
  let laid = false, holes = null;
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    if (!laid) {
      const h = slip.offsetHeight, y = (H - h) / 2;
      slip.style.top = y + "px";
      holes = [0, 1, 2].map(i => el("div", "abs", root, { left: (W - w) / 2 + 26 + "px", top: y + h * (0.28 + i * 0.22) + "px",
        width: "17px", height: "17px", borderRadius: "50%", background: "rgba(14,19,26,.55)",
        boxShadow: "inset 0 2px 4px rgba(0,0,0,.5)" }));
      laid = true;
    }
    const f = eOut(seg(t, 0.15, 1.0));
    setO(slip, f); slip.style.transform = `translateY(${((1 - f) * 18).toFixed(1)}px)`;
    if (holes) holes.forEach(h => setO(h, f));
    if (kick) setO(kick, eOut(seg(t, 0.45, 0.8)));
    lines.forEach(({ ln, d }, i) => {
      const a = eOut(seg(t, ln.at != null ? ln.at : 0.7 + i * 0.9, 0.9));
      setO(d, a); setT(d, 0, (1 - a) * 12);
    });
  };
};

SCENES.gzstat = async (s, root) => {
  const L = gzPhoto(root, s, s.dim != null ? s.dim : 0.68);
  const kick = el("div", "abs", root, { left: 0, width: W + "px", top: "262px", textAlign: "center", font: "27px 'Oswald'",
    letterSpacing: ".34em", color: GZ.cream, textTransform: "uppercase" }, esc(s.kicker || ""));
  const r1 = hair(root, W / 2 - 330, 324, 660, GZ.ochre, 2, true);
  const num = el("div", "abs", root, { left: 0, width: W + "px", top: "336px", textAlign: "center", font: `${s.size || 212}px 'Slab'`,
    color: s.color || GZ.cream, lineHeight: "1.02", textShadow: "0 10px 44px rgba(0,0,0,.5)" }, "");
  const unit = s.unit ? el("div", "abs", root, { left: 0, width: W + "px", top: "576px", textAlign: "center", font: "40px 'Engr'",
    letterSpacing: ".2em", color: GZ.ochre, textTransform: "uppercase" }, esc(s.unit)) : null;
  const r2 = hair(root, W / 2 - 330, s.unit ? 644 : 600, 660, GZ.ochre, 2, true);
  const note = el("div", "abs", root, { left: "250px", width: W - 500 + "px", top: (s.unit ? 674 : 630) + "px", textAlign: "center",
    font: "42px 'Pencil'", color: "rgba(232,226,208,.92)", lineHeight: "1.3" }, esc(s.note || ""));
  const src = gzSource(root, s, 130, 1000);
  const D = s.duration, A = s.at != null ? s.at : 0.5, CF = s.countFor || 1.4;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(kick, eOut(seg(t, A - 0.2, 0.8)));
    r1(eInOut(seg(t, A, 0.9))); r2(eInOut(seg(t, A + 0.2, 0.9)));
    const p = s.count === false ? 1 : eOut(seg(t, A + 0.2, CF));
    const txt = s.count === false ? String(s.value) : countText(s.value, p);
    if (num._s !== txt) { num.textContent = txt; num._s = txt; }
    setO(num, eOut(seg(t, A + 0.1, 0.6)));
    if (unit) setO(unit, eOut(seg(t, A + CF * 0.6, 0.8)));
    const q = eOut(seg(t, A + CF * 0.8, 1.0)); setO(note, q); setT(note, 0, (1 - q) * 10);
    if (src) setO(src, eOut(seg(t, A + 1.2, 1.0)));
  };
};

/* ------------------------------------------------------------------ comparison */
SCENES.gzversus = async (s, root) => {
  gzPaper(root);
  const head = gzHead(root, s);
  const LX = s.lx || 880, RX = s.rx || 1520, LAB = s.labx || 620, MID = (LX + RX) / 2 - 10;
  const cols = [s.left || {}, s.right || {}];
  const names = cols.map((c, i) => {
    const x = i ? RX : LX;
    const n = el("div", "abs", root, { left: x - 300 + "px", width: "600px", textAlign: "center", top: (s.y0 || 290) + "px",
      font: `${s.nameSize || 56}px 'Engr'`, letterSpacing: ".06em", color: c.color || (i ? GZ.verdigris : GZ.oxblood), lineHeight: "1.05" },
      esc(c.name || ""));
    const sb = c.sub ? el("div", "abs", root, { left: x - 300 + "px", width: "600px", textAlign: "center", top: (s.y0 || 290) + 66 + "px",
      font: "28px 'Oswald'", letterSpacing: ".22em", color: GZ.sub, textTransform: "uppercase" }, esc(c.sub)) : null;
    const u = hair(root, x - 190, (s.y0 || 290) + (c.sub ? 112 : 78), 380, c.color || (i ? GZ.verdigris : GZ.oxblood), 3, true);
    return { n, sb, u };
  });
  const divider = el("div", "abs", root, { left: MID + "px", top: (s.y0 || 290) + 140 + "px", width: "0", height: "0",
    borderLeft: "1px dashed rgba(30,40,50,.4)" });
  const Y0 = (s.y0 || 290) + 200, RH = s.rowH || 134;
  const rows = (s.rows || []).map((r, i) => {
    const y = Y0 + i * RH;
    const lab = el("div", "abs", root, { left: LAB - 480 + "px", width: "480px", textAlign: "right", top: y + 28 + "px",
      font: "31px 'Oswald'", letterSpacing: ".16em", color: GZ.sub, textTransform: "uppercase" }, esc(r.label || ""));
    const vals = [r.left, r.right].map((v, k) => el("div", "abs", root, { left: (k ? RX : LX) - 300 + "px", width: "600px",
      textAlign: "center", top: y + "px", font: `${r.size || 78}px 'Slab'`,
      color: r.win === (k ? "r" : "l") ? (k ? GZ.verdigris : GZ.oxblood) : GZ.ink }, ""));
    /* the pencil note sits under the winning figure, clear of the other column */
    const mark = r.mark ? el("div", "abs", root, { left: (r.win === "r" ? RX : LX) - 300 + "px", width: "600px",
      textAlign: "center", top: y + (r.size || 78) + 8 + "px", font: "34px 'Pencil'",
      color: r.win === "r" ? GZ.verdigris : GZ.oxblood, whiteSpace: "nowrap" }, esc(r.mark)) : null;
    const rule = hair(root, LAB - 480, y + RH - 26, RX - LAB + 780, "rgba(30,40,50,.16)", 1);
    return { r, lab, vals, mark, rule, at: r.at != null ? r.at : 1.2 + i * 1.6 };
  });
  const verdict = s.verdict ? el("div", "abs", root, { left: 0, width: W + "px", textAlign: "center",
    top: Math.min(990, Y0 + rows.length * RH + 34) + "px", font: "46px 'Pencil'", color: GZ.oxblood }, esc(s.verdict)) : null;
  const CF = s.countFor || 1.1;
  return t => {
    head(t);
    names.forEach((o, i) => {
      const a = eOut(seg(t, 0.4 + i * 0.3, 0.8));
      setO(o.n, a); setT(o.n, 0, (1 - a) * 12); if (o.sb) setO(o.sb, a);
      o.u(eInOut(seg(t, 0.7 + i * 0.3, 0.9)));
    });
    css(divider, "height", (eInOut(seg(t, 1.0, 1.2)) * (rows.length * RH + 20)).toFixed(1) + "px");
    rows.forEach(o => {
      const a = eOut(seg(t, o.at, 0.7));
      setO(o.lab, a); setT(o.lab, (1 - a) * -12, 0);
      o.rule(eInOut(seg(t, o.at + 0.2, 0.9)));
      [o.r.left, o.r.right].forEach((v, k) => {
        const p = eOut(seg(t, o.at + 0.15 + k * 0.25, CF));
        const txt = v == null ? "" : (o.r.count === false ? String(v) : countText(v, p));
        if (o.vals[k]._s !== txt) { o.vals[k].textContent = txt; o.vals[k]._s = txt; }
        setO(o.vals[k], cl(p * 3, 0, 1));
      });
      if (o.mark) { const q = eOut(seg(t, o.at + CF + 0.3, 0.6)); setO(o.mark, q); setT(o.mark, 0, (1 - q) * -8); }
    });
    if (verdict) { const v = eOut(seg(t, s.verdictAt != null ? s.verdictAt : rows.length * 1.6 + 1.6, 1.0)); setO(verdict, v); setT(verdict, 0, (1 - v) * 10); }
  };
};

/* the gazetteer page header: engraved title, pencil note, a double hairline */
function gzHead(root, s, x) {
  const X = x || 150;
  const tt = el("div", "abs", root, { left: X + "px", top: "92px", font: `${s.titleSize || 58}px 'Engr'`, letterSpacing: ".04em",
    color: GZ.ink, width: W - X * 2 + "px", lineHeight: "1.1" }, esc(s.title || ""));
  const nt = s.note ? el("div", "abs", root, { left: X + 2 + "px", top: (s.titleSize && s.titleSize > 58 ? 182 : 168) + "px",
    font: "32px 'Pencil'", color: GZ.sub }, esc(s.note)) : null;
  const y = nt ? 232 : 174;
  const r0 = hair(root, X, y, 420, GZ.ochre, 3);
  const r1 = hair(root, X, y + 9, 420, "rgba(190,138,44,.45)", 1);
  const src = gzSource(root, s, X, 1004, "rgba(30,40,50,.55)");
  return t => {
    const a = eOut(seg(t, 0.15, 0.8));
    setO(tt, a); setT(tt, (1 - a) * -10, 0);
    if (nt) setO(nt, eOut(seg(t, 0.45, 0.8)));
    r0(eInOut(seg(t, 0.5, 1.0))); r1(eInOut(seg(t, 0.65, 1.0)));
    if (src) setO(src, eOut(seg(t, 1.2, 1.0)));
  };
}

/* ------------------------------------------------------------------ giants and dots */
SCENES.gzgiants = async (s, root) => {
  gzPaper(root);
  const head = gzHead(root, s);
  const g = s.giant || {}, f = s.field || {};
  /* the giant: one circle sized by its value */
  const GR = g.r || 212, GCX = s.gcx || 540, GCY = s.gcy || 600;
  const ring = el("div", "abs", root, { left: GCX - GR - 26 + "px", top: GCY - GR - 26 + "px", width: 2 * (GR + 26) + "px",
    height: 2 * (GR + 26) + "px", borderRadius: "50%", border: "1px dashed rgba(30,40,50,.35)" });
  const disc = el("div", "abs", root, { left: GCX - GR + "px", top: GCY - GR + "px", width: 2 * GR + "px", height: 2 * GR + "px",
    borderRadius: "50%", background: g.color || GZ.oxblood, boxShadow: "0 18px 46px rgba(30,40,50,.3)" });
  const gnum = el("div", "abs", disc, { left: 0, top: GR - 62 + "px", width: 2 * GR + "px", textAlign: "center",
    font: `${g.size || 86}px 'Slab'`, color: GZ.cream, lineHeight: "1.0" }, "");
  const gunit = el("div", "abs", disc, { left: 0, top: GR + 34 + "px", width: 2 * GR + "px", textAlign: "center", font: "26px 'Oswald'",
    letterSpacing: ".26em", color: "rgba(232,226,208,.84)", textTransform: "uppercase" }, esc(g.unit || "people"));
  const gcap = el("div", "abs", root, { left: GCX - 420 + "px", width: "840px", textAlign: "center", top: GCY + GR + 62 + "px",
    font: "42px 'Engr'", color: g.color || GZ.oxblood, lineHeight: "1.2" }, esc(g.label || ""));
  const gsub = g.sub ? el("div", "abs", root, { left: GCX - 420 + "px", width: "840px", textAlign: "center", top: GCY + GR + 124 + "px",
    font: "32px 'Pencil'", color: GZ.sub }, esc(g.sub)) : null;
  const divider = el("div", "abs", root, { left: (s.midx || 980) + "px", top: "300px", width: "0", height: "0",
    borderLeft: "1px dashed rgba(30,40,50,.4)" });
  /* the field: N small dots scattered in a loose grid */
  const N = f.n || 68, X0 = s.fx || 1080, X1 = s.fx1 || 1810, Y0 = s.fy || 380, Y1 = s.fy1 || 820;
  const cols = Math.ceil(Math.sqrt(N * (X1 - X0) / (Y1 - Y0))), rows = Math.ceil(N / cols);
  const rnd = rng(f.seed || 7);
  const dots = [];
  for (let i = 0; i < N; i++) {
    const cx = X0 + ((i % cols) + 0.5) * (X1 - X0) / cols + (rnd() - 0.5) * 34;
    const cy = Y0 + (Math.floor(i / cols) + 0.5) * (Y1 - Y0) / rows + (rnd() - 0.5) * 30;
    const r = f.r || 15;
    dots.push(el("div", "abs", root, { left: cx - r + "px", top: cy - r + "px", width: 2 * r + "px", height: 2 * r + "px",
      borderRadius: "50%", background: f.color || GZ.verdigris, opacity: 0 }));
  }
  const fnum = el("div", "abs", root, { left: (X0 + X1) / 2 - 300 + "px", width: "600px", textAlign: "center", top: Y0 - 110 + "px",
    font: `${f.size || 92}px 'Slab'`, color: f.color || GZ.verdigris }, "");
  const fcap = el("div", "abs", root, { left: (X0 + X1) / 2 - 400 + "px", width: "800px", textAlign: "center", top: Y1 + 52 + "px",
    font: "42px 'Engr'", color: f.color || GZ.verdigris, lineHeight: "1.2" }, esc(f.label || ""));
  const fsub = f.sub ? el("div", "abs", root, { left: (X0 + X1) / 2 - 400 + "px", width: "800px", textAlign: "center", top: Y1 + 114 + "px",
    font: "32px 'Pencil'", color: GZ.sub }, esc(f.sub)) : null;
  const GA = g.at != null ? g.at : 0.9, FA = f.at != null ? f.at : GA + 2.2, FILL = f.fill || 2.0;
  return t => {
    head(t);
    const a = eOut(seg(t, GA, 1.0));
    setO(ring, a); setO(disc, a);
    disc.style.transform = `scale(${(0.4 + 0.6 * eOut(seg(t, GA, 1.2))).toFixed(3)})`;
    const gp = eOut(seg(t, GA + 0.3, 1.4));
    const gt = countText(g.value != null ? g.value : "", gp);
    if (gnum._s !== gt) { gnum.textContent = gt; gnum._s = gt; }
    setO(gnum, cl(gp * 3, 0, 1)); setO(gunit, eOut(seg(t, GA + 1.0, 0.8)));
    setO(gcap, eOut(seg(t, GA + 1.2, 0.9))); if (gsub) setO(gsub, eOut(seg(t, GA + 1.5, 0.9)));
    css(divider, "height", (eInOut(seg(t, FA - 0.5, 1.0)) * 520).toFixed(1) + "px");
    let on = 0;
    dots.forEach((d, i) => {
      const q = eOut(seg(t, FA + (i / N) * FILL, 0.3));
      setO(d, q); d.style.transform = `scale(${(0.3 + 0.7 * q).toFixed(3)})`;
      if (q > 0.5) on = i + 1;
    });
    const ft = String(f.count === false ? (f.value != null ? f.value : N) : on);
    if (fnum._s !== ft) { fnum.textContent = ft; fnum._s = ft; }
    setO(fnum, eOut(seg(t, FA, 0.5)));
    setO(fcap, eOut(seg(t, FA + FILL * 0.6, 0.9))); if (fsub) setO(fsub, eOut(seg(t, FA + FILL * 0.8, 0.9)));
  };
};

/* ------------------------------------------------------------------ a district dividing */
SCENES.gzdivide = async (s, root) => {
  gzPaper(root);
  const head = gzHead(root, s);
  const FX = s.fx || 460, FY = s.fy || 320, FW = s.fw || 1000, FH = s.fh || 520, PAD = 26;
  const frame = el("div", "abs", root, { left: FX + "px", top: FY + "px", width: FW + "px", height: FH + "px",
    border: "3px dashed rgba(30,40,50,.5)", boxSizing: "border-box", background: "rgba(190,138,44,.07)" });
  const flab = el("div", "abs", root, { left: FX + "px", top: FY - 46 + "px", font: "27px 'Oswald'", letterSpacing: ".26em",
    color: GZ.sub, textTransform: "uppercase" }, esc(s.frameLabel || "one settlement"));
  const steps = (s.steps || []).map((st, i) => Object.assign({ at: 1.0 + i * 2.0 }, st));
  const maxN = Math.max(...steps.map(st => st.n));
  function layout(n) {
    const cols = Math.ceil(Math.sqrt(n)), rows = Math.ceil(n / cols);
    const cw = (FW - PAD * (cols + 1)) / cols, ch = (FH - PAD * (rows + 1)) / rows;
    return Array.from({ length: n }, (_, i) => {
      const c = i % cols, r = Math.floor(i / cols);
      const inRow = Math.min(cols, n - r * cols);
      const off = (cols - inRow) * (cw + PAD) / 2;
      return [FX + PAD + off + c * (cw + PAD), FY + PAD + r * (ch + PAD), cw, ch];
    });
  }
  const lay = {}; steps.forEach(st => { lay[st.n] = layout(st.n); });
  const cells = Array.from({ length: maxN }, (_, i) => {
    const d = el("div", "abs", root, { left: 0, top: 0, width: "10px", height: "10px", background: GZ.slip,
      border: `3px solid ${GZ.ink}`, boxSizing: "border-box", boxShadow: "0 10px 24px rgba(30,40,50,.18)", opacity: 0 });
    const n = el("div", "abs", d, { left: 0, top: 0, width: "100%", textAlign: "center", font: "0px 'Slab'", color: GZ.oxblood }, String(i + 1));
    return { d, n };
  });
  const count = el("div", "abs", root, { left: 0, width: W + "px", textAlign: "center", top: FY + FH + 40 + "px",
    font: "56px 'Engr'", color: GZ.ink, letterSpacing: ".06em" }, "");
  const note = el("div", "abs", root, { left: 0, width: W + "px", textAlign: "center", top: FY + FH + 116 + "px",
    font: "40px 'Pencil'", color: GZ.sub }, "");
  return t => {
    head(t);
    const a = eOut(seg(t, 0.5, 1.0)); setO(frame, a); setO(flab, a);
    /* which step are we on, and how far into the move to the next */
    let cur = 0, p = 0;
    for (let i = 0; i < steps.length; i++) {
      if (t >= steps[i].at) { cur = i; p = 1; }
    }
    if (cur < steps.length - 1) {
      /* the move to the next layout runs in the second before that step's word */
      const nx = steps[cur + 1];
      p = eInOut(seg(t, nx.at - (nx.d || 1.0), nx.d || 1.0));
    }
    const nFrom = steps[cur].n, nTo = cur < steps.length - 1 ? steps[cur + 1].n : nFrom;
    const from = lay[nFrom], to = lay[nTo];
    cells.forEach(({ d, n }, i) => {
      const inFrom = i < nFrom, inTo = i < nTo;
      if (!inFrom && !inTo) { setO(d, 0); return; }
      const A = inFrom ? from[i] : to[i], B = inTo ? to[i] : from[i];
      const q = inFrom && inTo ? p : inTo ? p : 1 - p;          /* new cells grow in, dropped ones fade */
      const x = lerp(A[0], B[0], p), y = lerp(A[1], B[1], p), w = lerp(A[2], B[2], p), h = lerp(A[3], B[3], p);
      css(d, "left", x.toFixed(1) + "px"); css(d, "top", y.toFixed(1) + "px");
      css(d, "width", w.toFixed(1) + "px"); css(d, "height", h.toFixed(1) + "px");
      const vis_ = inFrom ? 1 : eOut(q);
      setO(d, vis_ * eOut(seg(t, steps[0].at, 0.8)));
      const fs = Math.max(0, Math.min(72, h * 0.34));
      css(n, "font", `${fs.toFixed(0)}px 'Slab'`);
      css(n, "top", ((h - fs * 1.3) / 2).toFixed(1) + "px");
      setO(n, w > 150 ? 1 : 0);
    });
    const st = steps[cur];
    const ct = (st.count != null ? st.count : String(st.n));
    if (count._s !== ct) { count.textContent = ct; count._s = ct; }
    setO(count, eOut(seg(t, st.at, 0.5)));
    const nt = st.label || "";
    if (note._s !== nt) { note.textContent = nt; note._s = nt; }
    setO(note, eOut(seg(t, st.at + 0.2, 0.6)));
  };
};

/* ------------------------------------------------------------------ index page */
SCENES.gzindex = async (s, root) => {
  gzPaper(root);
  const head = gzHead(root, s);
  const X0 = s.x0 || 330, X1 = s.x1 || 1600, Y0 = s.y0 || 300, RH = s.rowH || 96;
  const rows = (s.rows || []).map((r, i) => {
    const y = Y0 + i * RH;
    const bar = r.hi ? el("div", "abs", root, { left: X0 - 40 + "px", top: y - 12 + "px", width: X1 - X0 + 120 + "px",
      height: RH - 16 + "px", background: "rgba(190,138,44,.22)", opacity: 0 }) : null;
    const lab = el("div", "abs", root, { left: X0 + "px", top: y + "px", font: `${r.size || 46}px 'Engr'`, letterSpacing: ".08em",
      color: r.hi ? GZ.oxblood : GZ.ink, textTransform: "uppercase", whiteSpace: "nowrap" }, esc(r.label || ""));
    const sub = r.sub ? el("div", "abs", root, { left: X0 + "px", top: y + 52 + "px", font: "26px 'Pencil'", color: GZ.sub,
      whiteSpace: "nowrap" }, esc(r.sub)) : null;
    const lead = el("div", "abs", root, { left: 0, top: y + 40 + "px", width: "0", height: "0",
      borderTop: `2px dotted rgba(30,40,50,${r.hi ? ".5" : ".32"})` });
    const val = el("div", "abs", root, { left: X1 - 300 + "px", width: "300px", textAlign: "right", top: y - 6 + "px",
      font: `${r.vsize || 58}px 'Slab'`, color: r.hi ? GZ.oxblood : GZ.ink }, "");
    return { r, bar, lab, sub, lead, val, at: r.at != null ? r.at : 0.9 + i * 0.95 };
  });
  const foot = s.foot ? el("div", "abs", root, { left: 0, width: W + "px", textAlign: "center",
    top: Math.min(995, Y0 + rows.length * RH + 36) + "px", font: "42px 'Pencil'", color: GZ.oxblood }, esc(s.foot)) : null;
  return t => {
    head(t);
    rows.forEach(o => {
      const a = eOut(seg(t, o.at, 0.6));
      if (o.bar) setO(o.bar, a);
      setO(o.lab, a); setT(o.lab, (1 - a) * -16, 0);
      if (o.sub) setO(o.sub, eOut(seg(t, o.at + 0.3, 0.6)));
      const lx = X0 + o.lab.offsetWidth + 24, lw = Math.max(40, X1 - 320 - lx);
      css(o.lead, "left", lx + "px");
      css(o.lead, "width", (lw * eInOut(seg(t, o.at + 0.15, 0.7))).toFixed(1) + "px");
      const p = eOut(seg(t, o.at + 0.3, s.countFor || 0.9));
      const txt = o.r.count === false ? String(o.r.value) : countText(o.r.value, p);
      if (o.val._s !== txt) { o.val.textContent = txt; o.val._s = txt; }
      setO(o.val, cl(p * 3, 0, 1));
    });
    if (foot) { const v = eOut(seg(t, s.footAt != null ? s.footAt : rows.length * 0.95 + 1.2, 0.9)); setO(foot, v); setT(foot, 0, (1 - v) * 10); }
  };
};

/* ------------------------------------------------------------------ a decade of change */
SCENES.gzdelta = async (s, root) => {
  gzPaper(root);
  const head = gzHead(root, s);
  const items = s.items || [];
  const panels = items.map((it, i) => {
    const cx = items.length > 1 ? (i ? (s.rx || 1400) : (s.lx || 520)) : W / 2;
    const y = s.y || 360;
    const lab = el("div", "abs", root, { left: cx - 380 + "px", width: "760px", textAlign: "center", top: y + "px",
      font: "30px 'Oswald'", letterSpacing: ".26em", color: GZ.sub, textTransform: "uppercase" }, esc(it.label || ""));
    const a = el("div", "abs", root, { left: cx - 360 + "px", width: "300px", textAlign: "center", top: y + 70 + "px",
      font: `${it.size || 96}px 'Slab'`, color: GZ.ink }, "");
    const b = el("div", "abs", root, { left: cx + 60 + "px", width: "300px", textAlign: "center", top: y + 70 + "px",
      font: `${it.size || 96}px 'Slab'`, color: it.color || GZ.oxblood }, "");
    const ya = el("div", "abs", root, { left: cx - 360 + "px", width: "300px", textAlign: "center", top: y + 190 + "px",
      font: "30px 'Pencil'", color: GZ.sub }, esc(s.from || "2015"));
    const yb = el("div", "abs", root, { left: cx + 60 + "px", width: "300px", textAlign: "center", top: y + 190 + "px",
      font: "30px 'Pencil'", color: GZ.sub }, esc(s.to || "2025"));
    /* the arrow between them */
    const arrow = el("div", "abs", root, { left: cx - 44 + "px", top: y + 128 + "px", width: "0", height: "0",
      borderTop: `3px solid ${it.color || GZ.ochre}` });
    const headp = el("div", "abs", root, { left: cx + 40 + "px", top: y + 118 + "px", width: "0", height: "0",
      borderLeft: `18px solid ${it.color || GZ.ochre}`, borderTop: "11px solid transparent", borderBottom: "11px solid transparent", opacity: 0 });
    const box = plate(root, it.delta || "", { size: 36, bg: it.color || GZ.oxblood, pad: "12px 26px 13px" });
    box.style.left = cx - 150 + "px"; box.style.top = y + 250 + "px"; box.style.width = "300px"; box.style.textAlign = "center";
    setO(box, 0);
    const note = it.note ? el("div", "abs", root, { left: cx - 380 + "px", width: "760px", textAlign: "center", top: y + 340 + "px",
      font: "34px 'Pencil'", color: GZ.sub, lineHeight: "1.25" }, esc(it.note)) : null;
    return { it, lab, a, b, ya, yb, arrow, headp, box, note, at: it.at != null ? it.at : 0.9 + i * 2.6 };
  });
  const divider = items.length > 1 ? el("div", "abs", root, { left: W / 2 + "px", top: (s.y || 360) + "px", width: "0", height: "0",
    borderLeft: "1px dashed rgba(30,40,50,.35)" }) : null;
  const foot = s.foot ? el("div", "abs", root, { left: "200px", width: W - 400 + "px", textAlign: "center", top: (s.footY || 800) + "px",
    font: "44px 'Pencil'", color: GZ.oxblood, lineHeight: "1.25" }, esc(s.foot)) : null;
  const CF = s.countFor || 1.0;
  return t => {
    head(t);
    if (divider) css(divider, "height", (eInOut(seg(t, 0.8, 1.0)) * 420).toFixed(1) + "px");
    panels.forEach(o => {
      const q = eOut(seg(t, o.at, 0.7));
      setO(o.lab, q); setO(o.ya, eOut(seg(t, o.at + 0.2, 0.6))); setO(o.yb, eOut(seg(t, o.at + 0.9, 0.6)));
      const p0 = eOut(seg(t, o.at + 0.1, CF)), p1 = eOut(seg(t, o.at + 0.8, CF));
      [[o.a, o.it.from, p0], [o.b, o.it.to, p1]].forEach(([d, v, p]) => {
        const txt = countText(v, p);
        if (d._s !== txt) { d.textContent = txt; d._s = txt; }
        setO(d, cl(p * 3, 0, 1));
      });
      css(o.arrow, "width", (eInOut(seg(t, o.at + 0.6, 0.6)) * 84).toFixed(1) + "px");
      setO(o.headp, eOut(seg(t, o.at + 1.1, 0.4)));
      const bq = eOut(seg(t, o.at + CF + 0.7, 0.6));
      setO(o.box, bq); o.box.style.transform = `scale(${(1.12 - 0.12 * bq).toFixed(3)})`;
      if (o.note) setO(o.note, eOut(seg(t, o.at + CF + 1.1, 0.8)));
    });
    if (foot) { const v = eOut(seg(t, s.footAt != null ? s.footAt : panels.length * 2.6 + 1.4, 1.0)); setO(foot, v); setT(foot, 0, (1 - v) * 10); }
  };
};
