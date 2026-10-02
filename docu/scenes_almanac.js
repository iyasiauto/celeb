/* scenes_almanac.js - the "almanac" template: a farmer's almanac / heritage field guide.

   Calm and slow like the documentary template, but its own look: slab-serif type, stitched
   (dashed) rules and quilt frames, a seed-packet tag for places, charts drawn on cream paper,
   barn red / field green / wheat / denim. Motion is gentle and only used on the key points.

   Overlays (any scene, clips included):
   almhead    Chapter heading laid over moving footage: a stitched badge with the chapter
              number, a small kicker, a big slab title that rises out of a mask, a stitched rule.
              Animated, so on a clip it renders as a moving alpha layer.
   almtag     Place / date tag: a cream seed-packet label with an ink keyline and a punched hole.

   Scenes:
   almcard    Key-point card: a quilt frame (stitched border, corner diamonds) over a dimmed photo.
   almstat    One big number that counts up between two stitched rules.
   almgrowth  A line drawn across years on cream paper, points labelled as the line reaches them,
              an optional dashed projection.
   almsplit   A field seen from above that fences itself into equal strips ("80 acres, 5 sons").
   almdots    Generations as rows of dots that double (1 dot = 1,000 people).
   almshare   One bar split into shares that grow in turn ("fewer than 1 in 3 still farm").
   almbars    Columns that rise to their values on paper (land prices).
   almdistrict  A ring of houses around a church district, with its ministry as tags.
*/
"use strict";

/* every colour comes from the theme palette, so a later edition of this template (theme
   "almanac2") renders the same charts in its own ink and paper */
const ALM = {
  ink: PAL.ink || "#23211C", cream: PAL.cream || "#F2EBDA", tag: PAL.tagc || "#F4EEDF", sub: PAL.subc || "#4A443A",
  wheat: PAL.wheat || "#D4A85A", barn: PAL.barn || "#9E3A2B", field: PAL.field || "#5E7A44", denim: PAL.denim || "#4E6E8A",
};
const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"];

/* cream paper ground with a soft warm edge */
function almPaper(root, tone) {
  paperGround(root, "paper");
  el("div", "full", root, { background: `rgba(${PAL.paperWash || "246,240,226"},${tone != null ? tone : 0.55})` });
  el("div", "full", root, { background: `radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 55%, ${PAL.paperEdge || "rgba(70,50,25,.22)"} 100%)` });
}
/* a photo under a warm dark wash */
function almPhoto(root, s, dim) {
  const L = s.img ? photoLayer(root, Object.assign({ move: s.move || "in", zoom: s.zoom || 1.08 }, s)) : null;
  if (!L) paperGround(root, "dark");
  el("div", "full", root, { background: `rgba(22,17,11,${dim})` });
  vignette(root, 0.5);
  return L;
}
/* a dashed "stitched" rule; returns a setter for 0..1 */
function stitch(parent, x, y, w, color, thick) {
  const d = el("div", "abs", parent, { left: x + "px", top: y + "px", width: "0", height: "0", borderTop: `${thick || 3}px dashed ${color || ALM.wheat}` });
  return p => css(d, "width", (w * p).toFixed(1) + "px");
}
/* a round stitched badge with a numeral */
function badge(parent, size, text, color) {
  const b = el("div", "abs", parent, { left: 0, top: 0, width: size + "px", height: size + "px", borderRadius: "50%",
    border: `3px solid ${color || ALM.wheat}`, boxSizing: "border-box" });
  el("div", "abs", b, { left: "7px", top: "7px", right: "7px", bottom: "7px", borderRadius: "50%", border: `2px dashed ${color || ALM.wheat}` });
  el("div", "abs", b, { left: 0, top: 0, width: size - 6 + "px", height: size - 6 + "px", display: "flex", alignItems: "center", justifyContent: "center",
    font: `${Math.round(size * 0.36)}px 'Slab'`, color: color || ALM.wheat, letterSpacing: ".02em" }, esc(text));
  return b;
}
function source(root, s, x, y, color) {
  return s.source ? el("div", "abs", root, { left: (x || 120) + "px", top: (y || 1000) + "px", font: "19px 'Barlow'", letterSpacing: ".16em",
    color: color || "rgba(242,235,218,.62)", textTransform: "uppercase" }, esc(s.source)) : null;
}

/* ------------------------------------------------------------------ overlays */
OVERLAYS.almhead = (o, root) => {
  const at = o.at != null ? o.at : 0.4;
  const shade = el("div", "full", root, { background: "linear-gradient(90deg, rgba(18,14,9,.66) 0%, rgba(18,14,9,.38) 42%, rgba(18,14,9,0) 72%)," +
    "linear-gradient(0deg, rgba(18,14,9,.5) 0%, rgba(18,14,9,0) 45%)", opacity: 0 });
  const box = el("div", "abs", root, { left: (o.x || 130) + "px", bottom: (o.bottom || 150) + "px", width: (o.w || 1300) + "px" });
  const row = el("div", "", box, { position: "relative", height: "112px", marginBottom: "22px" });
  const b = o.n != null ? badge(row, 112, ROMAN[o.n] || String(o.n), ALM.wheat) : null;
  if (!b) row.style.height = "60px";
  const kick = el("div", "abs", row, { left: b ? "140px" : "2px", top: b ? "40px" : "14px", font: "28px 'BarlowB'", letterSpacing: ".34em", color: ALM.wheat,
    textTransform: "uppercase", whiteSpace: "nowrap" }, esc(o.kicker || ""));
  const mask = el("div", "", box, { overflow: "hidden", paddingBottom: "8px" });
  const title = el("div", "", mask, { font: `${o.size || 104}px 'Slab'`, lineHeight: "1.02", color: ALM.cream, textShadow: "0 6px 30px rgba(0,0,0,.45)" },
    esc(o.title || ""));
  const ruleBox = el("div", "", box, { position: "relative", height: "26px", marginTop: "14px" });
  const rule = stitch(ruleBox, 2, 10, o.rule || 420, ALM.wheat, 3);
  const sub = o.sub ? el("div", "", box, { font: "34px 'BaskI'", color: "#EDE5D2", marginTop: "6px", textShadow: "0 3px 16px rgba(0,0,0,.6)" }, esc(o.sub)) : null;
  return t => {
    const D = (typeof SCENE !== "undefined" && SCENE.duration) || 8;
    const out = o.out != null ? o.out : D - 1.0;
    const fo = 1 - eInOut(seg(t, out, 0.9));
    setO(shade, eOut(seg(t, at - 0.2, 1.0)) * fo);
    const a = eOut(seg(t, at, 0.8));
    if (b) { setO(b, a * fo); b.style.transform = `rotate(${((1 - a) * -40).toFixed(2)}deg) scale(${(0.85 + 0.15 * a).toFixed(3)})`; }
    setO(kick, eOut(seg(t, at + 0.3, 0.8)) * fo); setT(kick, (1 - eOut(seg(t, at + 0.3, 0.8))) * -16, 0);
    const r = eOut5(seg(t, at + 0.55, 1.1));
    setT(title, 0, (1 - r) * 130); setO(title, fo);
    rule(eInOut(seg(t, at + 1.1, 1.2)) * fo);
    if (sub) { const q = eOut(seg(t, at + 1.5, 1.0)); setO(sub, q * fo); setT(sub, 0, (1 - q) * 10); }
  };
};

OVERLAYS.almtag = (o, root) => {
  const at = o.at != null ? o.at : 0.6;
  const wrap = el("div", "abs", root, { left: (o.x != null ? o.x : 96) + "px", top: (o.y != null ? o.y : 880) + "px" });
  const tag = el("div", "", wrap, { position: "relative", background: ALM.tag, border: `2px solid ${ALM.ink}`, padding: "13px 28px 13px 58px",
    boxShadow: "0 10px 28px rgba(0,0,0,.35)", whiteSpace: "nowrap" });
  el("div", "abs", tag, { left: "20px", top: "50%", marginTop: "-9px", width: "14px", height: "14px", borderRadius: "50%",
    border: `2px solid ${ALM.ink}`, background: "#CFC3A6" });
  el("div", "abs", tag, { left: "4px", top: "4px", right: "4px", bottom: "4px", border: "1px dashed rgba(35,33,28,.35)", pointerEvents: "none" });
  el("div", "", tag, { font: `${o.size || 27}px 'BarlowB'`, letterSpacing: ".16em", color: ALM.ink, textTransform: "uppercase" }, esc(o.text || ""));
  if (o.sub) el("div", "", tag, { font: `${Math.round((o.size || 27) * 0.82)}px 'BaskI'`, color: ALM.sub, marginTop: "3px" }, esc(o.sub));
  return t => {
    const a = eOut(seg(t, at, 0.8));
    setO(wrap, a * (o.out != null ? 1 - seg(t, o.out, 0.6) : 1)); setT(wrap, (1 - a) * -26, 0, 1, (1 - a) * -2);
  };
};

/* ------------------------------------------------------------------ cards */
function quiltFrame(root, w, h, x, y, color) {
  const f = el("div", "abs", root, { left: x + "px", top: y + "px", width: w + "px", height: h + "px", border: `3px dashed ${color}`, boxSizing: "border-box" });
  el("div", "abs", f, { left: "10px", top: "10px", right: "10px", bottom: "10px", border: "1px solid rgba(242,235,218,.32)" });
  [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(([cx, cy]) => el("div", "abs", f, { left: (cx ? w - 3 : -3) - 11 + "px", top: (cy ? h - 3 : -3) - 11 + "px",
    width: "16px", height: "16px", background: color, transform: "rotate(45deg)" }));
  return f;
}

SCENES.almcard = async (s, root) => {
  const L = almPhoto(root, s, s.dim != null ? s.dim : 0.62);
  const w = s.w || 1240;
  const box = el("div", "abs", root, { left: (W - w) / 2 + "px", top: 0, width: w + "px", textAlign: "center" });
  const kick = s.kicker ? el("div", "", box, { font: "27px 'BarlowB'", letterSpacing: ".34em", color: ALM.wheat, textTransform: "uppercase", marginBottom: "26px" }, esc(s.kicker)) : null;
  const lines = (s.lines || []).map(ln => ({ ln, d: el("div", "", box, { font: `${ln.size || 74}px '${ln.font || "Slab"}'`, color: ln.color || ALM.cream,
    lineHeight: "1.14", marginTop: (ln.gap != null ? ln.gap : 18) + "px", textShadow: "0 6px 26px rgba(0,0,0,.45)" }, esc(ln.text)) }));
  let frame = null, laid = false;
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    if (!laid) {
      const h = box.offsetHeight, y = (H - h) / 2 - 10;
      box.style.top = y + "px";
      if (s.frame !== false) frame = quiltFrame(root, w + 180, h + 150, (W - w) / 2 - 90, y - 75, ALM.wheat);
      laid = true;
    }
    if (frame) { const f = eOut(seg(t, 0.15, 1.0)); setO(frame, f); frame.style.transform = `scale(${(0.97 + 0.03 * f).toFixed(4)})`; }
    if (kick) setO(kick, eOut(seg(t, 0.35, 0.8)));
    lines.forEach(({ ln, d }, i) => { const a = eOut(seg(t, ln.at != null ? ln.at : 0.6 + i * 0.9, 1.0)); setO(d, a); setT(d, 0, (1 - a) * 14); });
  };
};

SCENES.almstat = async (s, root) => {
  const L = almPhoto(root, s, s.dim != null ? s.dim : 0.7);
  const kick = el("div", "abs", root, { left: 0, width: W + "px", top: "250px", textAlign: "center", font: "28px 'BarlowB'", letterSpacing: ".34em",
    color: ALM.cream, textTransform: "uppercase" }, esc(s.kicker || ""));
  const r1 = stitch(root, W / 2 - 300, 312, 600, ALM.wheat, 3);
  const num = el("div", "abs", root, { left: 0, width: W + "px", top: "330px", textAlign: "center", font: `${s.size || 230}px 'Slab'`, color: ALM.wheat,
    lineHeight: "1.0", textShadow: "0 10px 40px rgba(0,0,0,.45)" }, "");
  const r2 = stitch(root, W / 2 - 300, 590, 600, ALM.wheat, 3);
  const note = el("div", "abs", root, { left: "260px", width: W - 520 + "px", top: "620px", textAlign: "center", font: "42px 'BaskI'", color: ALM.cream,
    lineHeight: "1.3" }, esc(s.note || ""));
  const src = source(root, s, 120, 990);
  const D = s.duration, A = s.at != null ? s.at : 0.5, CF = s.countFor || 1.4;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(kick, eOut(seg(t, A - 0.2, 0.8)));
    r1(eInOut(seg(t, A, 0.9))); r2(eInOut(seg(t, A + 0.2, 0.9)));
    const p = s.count === false ? 1 : eOut(seg(t, A + 0.2, CF));
    const txt = s.count === false ? String(s.value) : countText(s.value, p);
    if (num._s !== txt) { num.textContent = txt; num._s = txt; }
    setO(num, eOut(seg(t, A + 0.1, 0.6)));
    const q = eOut(seg(t, A + CF * 0.7, 1.0)); setO(note, q); setT(note, 0, (1 - q) * 10);
    if (src) setO(src, eOut(seg(t, A + 1.0, 1.0)));
  };
};

/* ------------------------------------------------------------------ paper charts */
function paperTitle(root, s, x) {
  const tt = el("div", "abs", root, { left: (x || 150) + "px", top: "96px", font: "62px 'Slab'", color: ALM.ink }, esc(s.title || ""));
  const nt = s.note ? el("div", "abs", root, { left: (x || 150) + "px", top: "176px", font: "30px 'BaskI'", color: ALM.sub }, esc(s.note)) : null;
  const rule = stitch(root, (x || 150) + 2, nt ? 232 : 182, 360, ALM.barn, 3);
  const src = source(root, s, x || 150, 1004, "rgba(35,33,28,.55)");
  return t => {
    const a = eOut(seg(t, 0.15, 0.8)); setO(tt, a); setT(tt, 0, (1 - a) * 10);
    if (nt) setO(nt, eOut(seg(t, 0.45, 0.8)));
    rule(eInOut(seg(t, 0.5, 1.0)));
    if (src) setO(src, eOut(seg(t, 1.2, 1.0)));
  };
}

SCENES.almgrowth = async (s, root) => {
  almPaper(root);
  const head = paperTitle(root, s);
  const X0 = 210, X1 = 1700, Y0 = 880, Y1 = 330;
  const pts = s.points || [];
  const xmin = s.xmin != null ? s.xmin : pts[0].x, xmax = s.xmax != null ? s.xmax : pts[pts.length - 1].x;
  const ymax = s.ymax || Math.max(...pts.map(p => p.y)) * 1.1;
  const X = x => X0 + (x - xmin) / (xmax - xmin) * (X1 - X0), Y = y => Y0 - y / ymax * (Y0 - Y1);
  el("div", "abs", root, { left: X0 + "px", top: Y0 + "px", width: X1 - X0 + "px", height: "0", borderTop: `2px solid ${ALM.ink}` });
  (s.grid || []).forEach(g => {
    el("div", "abs", root, { left: X0 + "px", top: Y(g.y) + "px", width: X1 - X0 + "px", height: "0", borderTop: "1px dashed rgba(35,33,28,.18)" });
    el("div", "abs", root, { left: X0 - 150 + "px", width: "136px", textAlign: "right", top: Y(g.y) - 16 + "px", font: "24px 'Barlow'", color: ALM.sub }, esc(g.label));
  });
  (s.ticks || pts.map(p => p.x)).forEach(x => el("div", "abs", root, { left: X(x) - 60 + "px", width: "120px", textAlign: "center", top: Y0 + 16 + "px",
    font: "26px 'Barlow'", letterSpacing: ".06em", color: ALM.sub }, esc(String(x))));
  const cv = el("canvas", "full", root); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  /* a smooth path through the points, sampled */
  const P = pts.map(p => [X(p.x), Y(p.y)]);
  const samp = [];
  for (let i = 0; i < P.length - 1; i++) {
    const [x0, y0] = P[i], [x1, y1] = P[i + 1];
    const m0 = i > 0 ? (P[i + 1][1] - P[i - 1][1]) / (P[i + 1][0] - P[i - 1][0]) : (y1 - y0) / (x1 - x0);
    const m1 = i + 2 < P.length ? (P[i + 2][1] - P[i][1]) / (P[i + 2][0] - P[i][0]) : (y1 - y0) / (x1 - x0);
    for (let k = 0; k < 40; k++) {
      const u = k / 40, h = x1 - x0, u2 = u * u, u3 = u2 * u;
      const y = (2 * u3 - 3 * u2 + 1) * y0 + (u3 - 2 * u2 + u) * h * m0 + (-2 * u3 + 3 * u2) * y1 + (u3 - u2) * h * m1;
      samp.push([x0 + u * h, Math.min(Y0, y), i]);
    }
  }
  samp.push([P[P.length - 1][0], P[P.length - 1][1], P.length - 1]);
  const labels = pts.map((p, i) => {
    const g = el("div", "abs", root, { left: 0, top: 0 });
    el("div", "abs", g, { left: "-11px", top: "-11px", width: "22px", height: "22px", borderRadius: "50%", background: p.color || ALM.barn,
      boxShadow: `0 0 0 5px rgba(246,240,226,.95)` });
    const lab = el("div", "abs", g, { left: (p.dx != null ? p.dx : -100) + "px", width: "200px", textAlign: "center", top: (p.dy != null ? p.dy : -96) + "px" });
    el("div", "", lab, { font: `${p.size || 46}px 'Slab'`, color: p.color || ALM.barn, whiteSpace: "nowrap" }, esc(p.label || ""));
    if (p.sub) el("div", "", lab, { font: "22px 'Barlow'", color: ALM.sub, letterSpacing: ".1em", textTransform: "uppercase", whiteSpace: "nowrap" }, esc(p.sub));
    setT(g, P[i][0], P[i][1]);
    return g;
  });
  const D = s.duration, A = s.at != null ? s.at : 1.0, DR = s.draw || Math.max(2.5, D * 0.45), PF = s.projectFrom != null ? s.projectFrom : 99;
  return t => {
    head(t);
    let n;
    if (pts.every(q => q.at != null)) {
      /* each point is reached at its own time (synced to the words) */
      let f = 0;
      for (let i = 0; i < pts.length - 1; i++) {
        const a0 = pts[i].at, a1 = pts[i + 1].at;
        if (t >= a1) f = i + 1; else if (t > a0) { f = i + eInOut((t - a0) / (a1 - a0)); break; } else break;
      }
      n = Math.max(1, Math.round(f * 40));
    } else n = Math.max(1, Math.floor(eInOut(seg(t, A, DR)) * (samp.length - 1)));
    c.clearRect(0, 0, W, H);
    /* soft fill under the drawn part */
    c.beginPath(); c.moveTo(samp[0][0], Y0);
    for (let i = 0; i <= n; i++) c.lineTo(samp[i][0], samp[i][1]);
    c.lineTo(samp[n][0], Y0); c.closePath(); c.fillStyle = "rgba(94,122,68,.16)"; c.fill();
    c.lineWidth = 6; c.lineJoin = "round"; c.lineCap = "round";
    [[false, ALM.field], [true, ALM.field]].forEach(([dash]) => {
      c.beginPath(); let started = false;
      for (let i = 0; i <= n; i++) {
        const proj_ = samp[i][2] >= PF;
        if (proj_ !== dash) { started = false; continue; }
        if (!started) { c.moveTo(samp[Math.max(0, i - 1)][0], samp[Math.max(0, i - 1)][1]); started = true; }
        c.lineTo(samp[i][0], samp[i][1]);
      }
      c.setLineDash(dash ? [16, 12] : []); c.strokeStyle = dash ? ALM.barn : ALM.field; c.stroke(); c.setLineDash([]);
    });
    labels.forEach((g, i) => {
      const reach = samp.findIndex(q => q[2] >= i) / (samp.length - 1);
      const a = eOut(seg(t, pts[i].at != null ? pts[i].at : A + reach * DR, 0.6));
      setO(g, a); g.style.transform = `translate(${P[i][0].toFixed(1)}px,${(P[i][1] + (1 - a) * 10).toFixed(1)}px)`;
    });
  };
};

SCENES.almsplit = async (s, root) => {
  almPaper(root);
  const head = paperTitle(root, s);
  const n = s.n || 5, FW = s.fw || 1260, FH = s.fh || 560, FX = (W - FW) / 2, FY = s.fy || 300;
  const field = el("div", "abs", root, { left: FX + "px", top: FY + "px", width: FW + "px", height: FH + "px", overflow: "hidden",
    background: "repeating-linear-gradient(90deg, #6F8B4F 0 16px, #5E7A44 16px 32px)", border: `3px solid ${ALM.ink}`, boxShadow: "0 18px 40px rgba(60,45,25,.25)" });
  const shade = el("div", "full", field, { background: "linear-gradient(180deg, rgba(255,255,255,.08), rgba(0,0,0,.12))" });
  const big = el("div", "abs", field, { left: 0, width: FW + "px", top: FH / 2 - 70 + "px", textAlign: "center", font: "120px 'Slab'", color: ALM.cream,
    textShadow: "0 6px 24px rgba(0,0,0,.4)" }, esc(s.label || "80 acres"));
  const fences = [], strips = [];
  for (let i = 1; i < n; i++) fences.push(el("div", "abs", field, { left: (FW / n) * i - 2 + "px", top: 0, width: "0", height: "0",
    borderLeft: `5px dashed ${ALM.cream}` }));
  for (let i = 0; i < n; i++) {
    const st = el("div", "abs", field, { left: (FW / n) * i + "px", top: 0, width: FW / n + "px", height: FH + "px", background: i % 2 ? "rgba(212,168,90,.0)" : "rgba(0,0,0,0)" });
    const lab = el("div", "abs", st, { left: 0, width: FW / n + "px", top: FH / 2 - 40 + "px", textAlign: "center", font: `${s.eachSize || 46}px 'Slab'`,
      color: ALM.cream, textShadow: "0 4px 16px rgba(0,0,0,.45)" }, esc(s.each || ""));
    const who = s.who ? el("div", "abs", st, { left: 0, width: FW / n + "px", top: FH / 2 + 22 + "px", textAlign: "center", font: "24px 'BarlowB'",
      letterSpacing: ".2em", color: ALM.tag, textTransform: "uppercase" }, esc(s.who.replace("{n}", i + 1))) : null;
    strips.push({ st, lab, who });
  }
  const verdict = s.verdict ? el("div", "abs", root, { left: 0, width: W + "px", top: FY + FH + 52 + "px", textAlign: "center", font: "44px 'BaskI'",
    color: ALM.barn }, esc(s.verdict)) : null;
  const A = s.at != null ? s.at : 0.6, SA = s.splitAt != null ? s.splitAt : A + 1.6, VA = s.verdictAt != null ? s.verdictAt : SA + n * 0.35 + 1.0;
  return t => {
    head(t);
    const a = eOut(seg(t, A, 1.0)); setO(field, a); field.style.transform = `scale(${(0.97 + 0.03 * a).toFixed(4)})`;
    setO(big, (1 - seg(t, SA, 0.6)) * eOut(seg(t, A + 0.3, 0.8)));
    fences.forEach((f, i) => css(f, "height", (eInOut(seg(t, SA + i * 0.35, 0.8)) * FH).toFixed(1) + "px"));
    strips.forEach(({ st, lab, who }, i) => {
      const q = eOut(seg(t, SA + (n - 1) * 0.35 + 0.4 + i * 0.12, 0.7));
      setO(lab, q); if (who) setO(who, q);
      css(st, "background", i % 2 ? `rgba(212,168,90,${(0.22 * q).toFixed(3)})` : "rgba(0,0,0,0)");
    });
    if (verdict) { const v = eOut(seg(t, VA, 1.0)); setO(verdict, v); setT(verdict, 0, (1 - v) * 10); }
  };
};

SCENES.almdots = async (s, root) => {
  almPaper(root);
  const head = paperTitle(root, s);
  const per = s.perLine || 40, DS = 24, GAP = 6, X0 = 520;
  let y = s.y0 || 300;
  const rows = (s.rows || []).map((r, ri) => {
    const lines = Math.ceil(r.n / per);
    const lab = el("div", "abs", root, { left: "150px", top: y - 6 + "px", width: "330px", font: "38px 'Slab'", color: ALM.ink, whiteSpace: "nowrap" }, esc(r.label));
    const val = el("div", "abs", root, { left: X0 + per * (DS + GAP) + 26 + "px", top: y - 8 + "px", font: "46px 'Slab'", color: r.color || ALM.barn, whiteSpace: "nowrap" }, esc(r.value));
    const dots = [];
    for (let k = 0; k < r.n; k++) {
      dots.push(el("div", "abs", root, { left: X0 + (k % per) * (DS + GAP) + "px", top: y + Math.floor(k / per) * (DS + GAP) + "px", width: DS + "px",
        height: DS + "px", borderRadius: "50%", background: r.color || ALM.field, opacity: 0 }));
    }
    const o = { r, lab, val, dots, at: r.at != null ? r.at : 0.8 + ri * 1.4 };
    y += lines * (DS + GAP) + (s.rowGap || 46);
    return o;
  });
  const leg = el("div", "abs", root, { left: X0 + "px", top: Math.min(960, y + 6) + "px", font: "24px 'Barlow'", color: ALM.sub, letterSpacing: ".08em" },
    `<span style="display:inline-block;width:18px;height:18px;border-radius:50%;background:${ALM.field};vertical-align:-2px;margin-right:10px"></span>${esc(s.unit || "= 1,000 people")}`);
  return t => {
    head(t);
    setO(leg, eOut(seg(t, 0.8, 0.8)));
    rows.forEach(o => {
      setO(o.lab, eOut(seg(t, o.at, 0.6)));
      const fill = s.fill || 1.0;
      o.dots.forEach((d, k) => { const q = eOut(seg(t, o.at + 0.2 + (k / Math.max(1, o.dots.length)) * fill, 0.35)); setO(d, q); d.style.transform = `scale(${(0.4 + 0.6 * q).toFixed(3)})`; });
      setO(o.val, eOut(seg(t, o.at + 0.2 + fill, 0.6)));
    });
  };
};

SCENES.almshare = async (s, root) => {
  almPaper(root);
  const head = paperTitle(root, s);
  const BX = 200, BW = W - 400, BY = s.y || 470, BH = 150;
  el("div", "abs", root, { left: BX + "px", top: BY + "px", width: BW + "px", height: BH + "px", border: `3px solid ${ALM.ink}`, boxSizing: "border-box" });
  let x = BX;
  const segs = (s.parts || []).map((p, i) => {
    const w = BW * p.frac;
    const bar = el("div", "abs", root, { left: x + "px", top: BY + "px", width: "0", height: BH + "px", background: p.color || ALM.field,
      borderRight: i < s.parts.length - 1 ? `4px dashed ${ALM.cream}` : "none", boxSizing: "border-box" });
    const big = el("div", "abs", root, { left: x + "px", width: w + "px", top: BY + BH / 2 - 44 + "px", textAlign: "center", font: "70px 'Slab'", color: ALM.cream }, esc(p.big || ""));
    const lab = el("div", "abs", root, { left: x + 6 + "px", width: w - 12 + "px", top: BY + BH + 26 + "px", textAlign: "center", font: "40px 'Slab'",
      color: p.color || ALM.field, lineHeight: "1.1" }, esc(p.label || ""));
    const sub = p.sub ? el("div", "abs", root, { left: x + 6 + "px", width: w - 12 + "px", top: BY + BH + 80 + "px", textAlign: "center", font: "26px 'BaskI'",
      color: ALM.sub, lineHeight: "1.3" }, esc(p.sub)) : null;
    const o = { p, bar, big, lab, sub, w, at: p.at != null ? p.at : 0.9 + i * 1.3 };
    x += w;
    return o;
  });
  return t => {
    head(t);
    segs.forEach(o => {
      const g = eInOut(seg(t, o.at, 1.1));
      css(o.bar, "width", (o.w * g).toFixed(1) + "px");
      setO(o.big, eOut(seg(t, o.at + 0.7, 0.6)));
      const q = eOut(seg(t, o.at + 0.6, 0.8)); setO(o.lab, q); if (o.sub) setO(o.sub, eOut(seg(t, o.at + 0.9, 0.8)));
    });
  };
};

SCENES.almbars = async (s, root) => {
  almPaper(root);
  const head = paperTitle(root, s);
  const bars = s.bars || [];
  const X0 = s.x0 || 260, X1 = 1680, Y0 = 860, HT = s.ht || 470;
  const gaps = bars.filter(b => b.gapBefore).length;
  const slot = (X1 - X0) / (bars.length + gaps * 0.6);
  const vmax = s.max || Math.max(...bars.map(b => b.value));
  el("div", "abs", root, { left: X0 - 20 + "px", top: Y0 + "px", width: X1 - X0 + 40 + "px", height: "0", borderTop: `2px solid ${ALM.ink}` });
  let x = X0;
  const cols = bars.map((b, i) => {
    if (b.gapBefore) {
      x += slot * 0.6;
      el("div", "abs", root, { left: x - slot * 0.3 + "px", top: Y0 - HT - 30 + "px", width: "0", height: HT + 60 + "px", borderLeft: "2px dashed rgba(35,33,28,.3)" });
    }
    const bw = slot * 0.56, bx = x + (slot - bw) / 2;
    const col = el("div", "abs", root, { left: bx + "px", top: Y0 + "px", width: bw + "px", height: "0", background: b.color || ALM.wheat,
      boxShadow: "inset 0 0 0 2px rgba(35,33,28,.25)" });
    const val = el("div", "abs", root, { left: bx - 60 + "px", width: bw + 120 + "px", textAlign: "center", top: Y0 + "px", font: `${s.valSize || 46}px 'Slab'`,
      color: b.color === ALM.field ? ALM.field : ALM.ink, whiteSpace: "nowrap" }, "");
    const lab = el("div", "abs", root, { left: bx - 70 + "px", width: bw + 140 + "px", textAlign: "center", top: Y0 + 18 + "px", font: "25px 'Barlow'",
      letterSpacing: ".06em", color: ALM.sub, lineHeight: "1.25" }, esc(b.label || ""));
    const o = { b, col, val, lab, at: b.at != null ? b.at : 0.9 + i * 0.8 };
    x += slot;
    return o;
  });
  (s.groups || []).forEach(g => el("div", "abs", root, { left: X0 + g.x + "px", top: Y0 + 96 + "px", font: "28px 'BarlowB'", letterSpacing: ".24em",
    color: g.color || ALM.barn, textTransform: "uppercase" }, esc(g.text)));
  return t => {
    head(t);
    cols.forEach(o => {
      const g = eInOut(seg(t, o.at, 1.2));
      const h = (o.b.value / vmax) * HT * g;
      css(o.col, "height", h.toFixed(1) + "px"); css(o.col, "top", (Y0 - h).toFixed(1) + "px");
      const txt = countText(o.b.text || String(o.b.value), g);
      if (o.val._s !== txt) { o.val.textContent = txt; o.val._s = txt; }
      css(o.val, "top", (Y0 - h - 62).toFixed(1) + "px"); setO(o.val, cl(g * 3, 0, 1));
      setO(o.lab, eOut(seg(t, o.at - 0.2, 0.6)));
    });
  };
};

SCENES.almdistrict = async (s, root) => {
  almPaper(root);
  const head = paperTitle(root, s);
  const CX = W / 2, CY = s.cy || 545, R = s.r || 270, N = s.houses || 30;
  const ring = el("div", "abs", root, { left: CX - R + "px", top: CY - R + "px", width: 2 * R + "px", height: 2 * R + "px", borderRadius: "50%",
    border: "2px dashed rgba(35,33,28,.35)" });
  const centre = el("div", "abs", root, { left: CX - 150 + "px", top: CY - 150 + "px", width: "300px", height: "300px", borderRadius: "50%",
    background: ALM.tag, border: `3px solid ${ALM.ink}`, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center",
    flexDirection: "column", boxShadow: "0 14px 34px rgba(60,45,25,.2)" });
  el("div", "", centre, { font: "44px 'Slab'", color: ALM.ink, lineHeight: "1.05" }, esc(s.centre || "Church district"));
  el("div", "", centre, { font: "24px 'BaskI'", color: ALM.sub, marginTop: "8px" }, esc(s.centreSub || ""));
  const houses = [];
  for (let i = 0; i < N; i++) {
    const a = -Math.PI / 2 + (i / N) * 2 * Math.PI;
    const h = el("div", "abs", root, { left: CX + R * Math.cos(a) - 17 + "px", top: CY + R * Math.sin(a) - 17 + "px", width: "34px", height: "34px",
      background: i % 3 === 0 ? ALM.barn : ALM.field, clipPath: "polygon(50% 0, 100% 42%, 100% 100%, 0 100%, 0 42%)", opacity: 0 });
    houses.push(h);
  }
  const roles = (s.roles || []).map((r, i) => {
    const d = el("div", "abs", root, { left: 0, top: 0, background: ALM.ink, color: ALM.tag, padding: "10px 22px 9px", font: "26px 'BarlowB'",
      letterSpacing: ".18em", textTransform: "uppercase", whiteSpace: "nowrap" }, esc(r.text));
    return { r, d };
  });
  const cnt = s.count ? el("div", "abs", root, { left: 0, width: W + "px", textAlign: "center", top: CY + R + 112 + "px", font: "34px 'BaskI'", color: ALM.barn }, esc(s.count)) : null;
  let laid = false;
  return t => {
    head(t);
    if (!laid) {
      const total = roles.reduce((a, o) => a + o.d.offsetWidth, 0) + 26 * (roles.length - 1);
      let x = CX - total / 2;
      roles.forEach(o => { o.d.style.left = x + "px"; o.d.style.top = (s.rolesY || CY + R + 36) + "px"; x += o.d.offsetWidth + 26; });
      laid = true;
    }
    setO(ring, eOut(seg(t, 0.5, 1.0)));
    const c = eOut(seg(t, 0.6, 0.9)); setO(centre, c); centre.style.transform = `scale(${(0.9 + 0.1 * c).toFixed(3)})`;
    const HA = s.housesAt != null ? s.housesAt : 1.2;
    houses.forEach((h, i) => { const q = eOut(seg(t, HA + i * (s.step || 0.06), 0.5)); setO(h, q); h.style.transform = `translateY(${((1 - q) * -12).toFixed(1)}px)`; });
    roles.forEach((o, i) => { const q = eOut(seg(t, o.r.at != null ? o.r.at : HA + N * 0.06 + 0.4 + i * 0.5, 0.6)); setO(o.d, q); setT(o.d, 0, (1 - q) * 10); });
    if (cnt) setO(cnt, eOut(seg(t, s.countAt != null ? s.countAt : HA + N * 0.06, 0.8)));
  };
};
