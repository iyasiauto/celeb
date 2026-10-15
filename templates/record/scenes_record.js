/* scenes_record.js - "The Record": investigative documentary about closed communities, institutions and silence.

   The look of a case being assembled from the record itself: blue-black ink ground, bone-white paper, steel-grey
   labels and ONE signal colour (sodium amber) for the thing that matters - a highlighted line, the number that
   gives it away. A muted red is kept for the stamp / the verdict. Statements in a book serif (Crimson Pro), labels
   in condensed caps (Roboto Condensed), anything from a file or a court in a code mono (Kode Mono), Hebrew in
   Frank Ruhl Libre. Every claim is shown as part of the record - a transcript line, a ledger row, a sourced exhibit.

   Scenes
   docket      chapter heading: FILE 03 / 08 - kicker, title, docket line; the record's index
   transcript  a page of statement / ruling with line numbers; lines arrive as spoken, the key words get marked
   lexicon     a term: the Hebrew word, transliteration, pronunciation, numbered meanings
   tally       a ledger of numbers as bars that count up row by row; a row can be struck / stamped
   counts      a sentence board: big counts (59 COUNTS · 103 YEARS) and what happened after (CUT ON APPEAL)
   chain       a mechanism: nodes joined by arrows that light up in turn; a gate and a delay clock can sit between
   redacted    a list of entries whose names are blacked out one by one; a stamp lands at the end
   wall        posters pasted one by one on a night wall; the last carries one word, stamped
   docketline  a time axis (centuries or months): the marker travels, events land on their words
   ripple      a person at the centre with the rings of a life around them; the rings are cut away in turn
   ballot      a field of votes that turns as one bloc
   Overlays
   casebox     a clip / photo shown inside an evidence viewer: frame, exhibit number, timecode, source (render "inset")
   source      a citation tag on footage: SOURCE - publication, year
   place       where we are: place name + a coordinates line, lower left
*/
"use strict";

const RC = {
  ink: PAL.ink || "#0E1217", slate: "#18202A", bone: PAL.cream || "#E9E4D8", steel: PAL.ash || "#8A96A3",
  amber: PAL.gold || "#E2A33B", red: PAL.red || "#B3352E", line: "rgba(233,228,216,.10)", paper: "#ECE7DB",
  paperInk: "#1C2128",
};

/* the ground every graphic sits on: blue-black, a faint ledger grid, a soft pool of light */
function rcGround(root, img, dim) {
  if (img) {
    pic(img.replace(/\.jpg$/, "_blur.jpg"), root, { left: "-40px", top: "-40px", width: (W + 80) + "px", height: (H + 80) + "px", objectFit: "cover" });
    el("div", "full", root, { background: `rgba(10,13,17,${dim != null ? dim : 0.82})` });
  } else {
    el("div", "full", root, { background: "radial-gradient(ellipse at 50% 38%, #1B2430 0%, #10151C 55%, #0A0D11 100%)" });
  }
  el("div", "full", root, { backgroundImage: "linear-gradient(rgba(233,228,216,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(233,228,216,.035) 1px, transparent 1px)",
    backgroundSize: "60px 60px" });
  vignette(root, 0.6);
}
/* a slow, small camera drift for a whole graphic (never more than ~3 %) */
function rcCam(node, t, D, amt) {
  const p = drift(cl(t / Math.max(0.1, D), 0, 1));
  node.style.transformOrigin = "50% 50%";
  node.style.transform = `scale(${(1 + (amt || 0.03) * p).toFixed(4)})`;
}
function rcLabel(parent, x, y, text, color, size) {
  return el("div", "abs", parent, { left: x + "px", top: y + "px", font: `${size || 26}px 'LabelB'`, letterSpacing: ".34em",
    color: color || RC.steel, whiteSpace: "nowrap" }, esc(text));
}
function rcRule(parent, x, y, w, color, thick) {
  const d = el("div", "abs", parent, { left: x + "px", top: y + "px", width: "0", borderTop: `${thick || 2}px solid ${color || RC.amber}` });
  return p => css(d, "width", (w * p).toFixed(1) + "px");
}
function rcWipe(node, p) { css(node, "clipPath", `inset(-20% ${((1 - p) * 100).toFixed(2)}% -20% 0)`); }
/* text with [[marked]] words: returns html with spans the marker can sweep across */
function rcMarked(text) {
  return esc(text).replace(/\[\[(.+?)\]\]/g, (m, w) => `<span class="rcm" style="position:relative;white-space:nowrap"><span class="rcbg" style="position:absolute;left:-4px;right:-4px;top:12%;bottom:6%;background:${RC.amber};opacity:.9;transform-origin:0 50%;transform:scaleX(0);z-index:-1"></span>${w}</span>`);
}
function rcSweep(root, p) { root.querySelectorAll(".rcbg").forEach(b => { b.style.transform = `scaleX(${p.toFixed(3)})`; }); }
/* a rubber stamp that lands: scale 1.6 -> 1, slight rotation */
function rcStamp(parent, x, y, text, color, size, rot, onPaper) {
  const s = el("div", "abs", parent, { left: x + "px", top: y + "px", font: `${size || 64}px 'Stamp'`, color: color || RC.red,
    border: `6px solid ${color || RC.red}`, padding: "6px 26px 2px", letterSpacing: ".12em", whiteSpace: "nowrap", opacity: 0,
    mixBlendMode: onPaper ? "multiply" : "screen", background: onPaper ? "rgba(236,231,219,.55)" : "none", transformOrigin: "50% 50%" }, esc(text));
  return p => { setO(s, cl(p * 1.6, 0, 0.92)); s.style.transform = `rotate(${rot != null ? rot : -6}deg) scale(${(1.6 - 0.6 * eOut5(p)).toFixed(3)})`; };
}

/* ------------------------------------------------------------------ docket (chapter heading) */
SCENES.docket = async (s, root) => {
  rcGround(root, s.img, 0.86);
  const cam = el("div", "full", root, {});
  const at = s.at != null ? s.at : 0.3;
  const x = 200;
  const file = el("div", "abs", cam, { left: x + "px", top: "300px", font: "30px 'Code'", color: RC.steel, letterSpacing: ".18em" },
    esc(`FILE ${String(s.n || 1).padStart(2, "0")}${s.of ? " / " + String(s.of).padStart(2, "0") : ""}`));
  const kick = s.kicker ? el("div", "abs", cam, { left: x + "px", top: "360px", font: "30px 'LabelB'", letterSpacing: ".42em", color: RC.amber }, esc(s.kicker)) : null;
  const r = rcRule(cam, x, 412, 640, RC.amber, 2);
  const title = el("div", "abs", cam, { left: (x - 4) + "px", top: "430px", width: (W - 2 * x) + "px", font: `${s.size || 128}px 'Rec'`, color: RC.bone,
    lineHeight: "1.02", textShadow: "0 10px 50px rgba(0,0,0,.6)" }, esc(s.title || ""));
  const line = s.line ? el("div", "abs", cam, { left: x + "px", top: (440 + (s.size || 128) * (s.lines || 1) + 40) + "px", font: "30px 'Code'",
    color: RC.steel, letterSpacing: ".08em" }, "") : null;
  /* the index of all files down the right edge, this one lit */
  const idx = (s.files || []).map((f, i) => el("div", "abs", cam, { right: "120px", top: (300 + i * 46) + "px", font: "24px 'LabelB'", letterSpacing: ".24em",
    color: i + 1 === s.n ? RC.amber : "rgba(138,150,163,.45)", textAlign: "right", opacity: 0 }, esc(`${String(i + 1).padStart(2, "0")}  ${f}`)));
  const D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.025);
    setO(file, eOut(seg(t, at - 0.2, 0.5)));
    if (kick) setO(kick, eOut(seg(t, at, 0.6)));
    r(eInOut(seg(t, at + 0.1, 0.9)));
    const q = eOut(seg(t, at + 0.25, 0.9)); rcWipe(title, q); setT(title, (1 - q) * -14, 0);
    if (line) typeOn(line, s.line, t, at + 1.1, 34, false);
    idx.forEach((n, i) => setO(n, eOut(seg(t, at + 0.4 + i * 0.07, 0.5))));
  };
};

/* ------------------------------------------------------------------ transcript */
SCENES.transcript = async (s, root) => {
  rcGround(root, s.img, 0.9);
  const lines = s.lines || [];
  const pw = s.pw || 1260, lh = 66, ph = Math.min(960, 210 + lines.length * lh + 70), px = (W - pw) / 2, py = (H - ph) / 2 + 10;
  const page = el("div", "abs", root, { left: px + "px", top: py + "px", width: pw + "px", height: ph + "px", background: RC.paper,
    boxShadow: "0 50px 120px rgba(0,0,0,.6)", transformOrigin: "50% 40%" });
  el("div", "abs", page, { left: "96px", top: 0, bottom: 0, width: "2px", background: "rgba(179,53,46,.35)" });
  const head = el("div", "abs", page, { left: "130px", top: "52px", right: "70px", font: "24px 'LabelB'", letterSpacing: ".3em", color: "#5B6570" }, esc(s.header || "STATEMENT"));
  const src = s.source ? el("div", "abs", page, { left: "130px", top: "90px", right: "70px", font: "26px 'Code'", color: "#3A424C" }, esc(s.source)) : null;
  el("div", "abs", page, { left: "130px", top: "140px", right: "70px", borderTop: "1px solid rgba(28,33,40,.25)" });
  const rows = lines.map((ln, i) => {
    const y = 170 + i * lh;
    el("div", "abs", page, { left: "30px", width: "48px", textAlign: "right", top: (y + 6) + "px", font: "24px 'Code'", color: "rgba(28,33,40,.4)" }, String(i + 1));
    const tx = el("div", "abs", page, { left: "130px", right: "70px", top: y + "px", font: `${s.size || 40}px 'Rec'`, color: RC.paperInk, lineHeight: "1.3",
      opacity: 0, isolation: "isolate" }, rcMarked(ln));
    return tx;
  });
  const at = s.at != null ? s.at : 0.3;
  const when = lines.map((_, i) => (s.lineAt && s.lineAt[i] != null) ? s.lineAt[i] : at + 0.5 + i * (s.every || 0.9));
  const hiAt = s.hiAt != null ? s.hiAt : when[when.length - 1] + 0.6;
  const D = s.duration;
  return t => {
    const a = eOut(seg(t, 0, 0.8));
    setO(page, a);
    page.style.transform = `translateY(${((1 - a) * 30).toFixed(1)}px) scale(${(1 + 0.035 * drift(cl(t / D, 0, 1))).toFixed(4)}) rotate(${s.tilt != null ? s.tilt : -0.6}deg)`;
    setO(head, eOut(seg(t, at - 0.1, 0.6))); if (src) setO(src, eOut(seg(t, at, 0.6)));
    rows.forEach((r, i) => { const q = eOut(seg(t, when[i], 0.6)); setO(r, q); setT(r, (1 - q) * -10, 0); });
    rcSweep(page, eInOut(seg(t, hiAt, 0.7)));
  };
};

/* ------------------------------------------------------------------ lexicon */
SCENES.lexicon = async (s, root) => {
  rcGround(root, s.img, 0.88);
  const cam = el("div", "full", root, {});
  const at = s.at != null ? s.at : 0.3;
  const heb = el("div", "abs", cam, { right: "170px", top: "250px", font: `${s.hsize || 250}px 'Heb'`, color: RC.bone, direction: "rtl",
    lineHeight: "1", textShadow: "0 12px 60px rgba(0,0,0,.6)", opacity: 0 }, esc(s.hebrew || ""));
  const word = el("div", "abs", cam, { left: "200px", top: "270px", font: `${s.size || 140}px 'RecI'`, color: RC.bone, whiteSpace: "nowrap" }, esc(s.word || ""));
  const pron = s.pron ? el("div", "abs", cam, { left: "206px", top: (290 + (s.size || 140)) + "px", font: "34px 'Code'", color: RC.steel }, esc(s.pron)) : null;
  const pos = s.pos ? el("div", "abs", cam, { left: "206px", top: (346 + (s.size || 140)) + "px", font: "26px 'LabelB'", letterSpacing: ".34em", color: RC.amber }, esc(s.pos)) : null;
  const r = rcRule(cam, 206, 410 + (s.size || 140), W - 412, "rgba(233,228,216,.25)", 1);
  const defs = (s.defs || []).map((d, i) => {
    const g = el("div", "abs", cam, { left: "206px", top: (450 + (s.size || 140) + i * 92) + "px", width: (W - 520) + "px", opacity: 0, isolation: "isolate" });
    el("span", "", g, { font: "34px 'Code'", color: RC.amber, marginRight: "22px" }, `${i + 1}.`);
    el("span", "", g, { font: "44px 'Rec'", color: RC.bone }, rcMarked(d));
    return g;
  });
  const when = defs.map((_, i) => (s.defAt && s.defAt[i] != null) ? s.defAt[i] : at + 1.4 + i * 1.1);
  const D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.03);
    const q = eOut(seg(t, at, 0.9)); rcWipe(word, q);
    setO(heb, eOut(seg(t, s.hebAt != null ? s.hebAt : at + 0.4, 1.2)) * 0.95);
    if (pron) setO(pron, eOut(seg(t, at + 0.6, 0.6))); if (pos) setO(pos, eOut(seg(t, at + 0.8, 0.6)));
    r(eInOut(seg(t, at + 0.8, 1.0)));
    defs.forEach((g, i) => { const p = eOut(seg(t, when[i], 0.7)); setO(g, p); setT(g, 0, (1 - p) * 14); });
    if (s.hiAt != null) rcSweep(cam, eInOut(seg(t, s.hiAt, 0.7)));
  };
};

/* ------------------------------------------------------------------ tally (a ledger of numbers) */
SCENES.tally = async (s, root) => {
  rcGround(root, null);
  const cam = el("div", "full", root, {});
  const rows = s.rows || [];
  const top = s.title ? 300 : 230, rh = Math.min(118, 560 / Math.max(1, rows.length)), x0 = 200, lw = 560, bx = x0 + lw + 30, bw = W - bx - 330;
  const kick = s.kicker ? rcLabel(cam, x0, 150, s.kicker, RC.amber, 28) : null;
  const title = s.title ? el("div", "abs", cam, { left: x0 + "px", top: "196px", font: "64px 'Rec'", color: RC.bone, whiteSpace: "nowrap" }, esc(s.title)) : null;
  const max = Math.max(...rows.map(r => Number(r.value) || 0), 1);
  const R = rows.map((r, i) => {
    const y = top + i * rh;
    const lab = el("div", "abs", cam, { left: x0 + "px", top: (y + 8) + "px", width: lw + "px", font: "36px 'Label'", color: RC.bone, opacity: 0, lineHeight: "1.1" }, esc(r.label));
    const bar = el("div", "abs", cam, { left: bx + "px", top: (y + 10) + "px", height: (rh * 0.46) + "px", width: "0", background: r.hi ? RC.amber : "rgba(233,228,216,.82)" });
    const num = el("div", "abs", cam, { left: bx + "px", top: (y - 6) + "px", font: `${Math.min(68, rh * 0.62)}px 'Num'`, color: r.hi ? RC.amber : RC.bone, opacity: 0, whiteSpace: "nowrap" }, "0");
    const note = r.note ? el("div", "abs", cam, { left: (x0) + "px", top: (y + 52) + "px", font: "24px 'Code'", color: RC.steel, opacity: 0, whiteSpace: "nowrap" }, esc(r.note)) : null;
    const strike = r.strikeAt != null ? el("div", "abs", cam, { left: (bx - 10) + "px", top: (y + rh * 0.23 + 8) + "px", height: "6px", width: "0", background: RC.red }) : null;
    return { r, lab, bar, num, note, strike, w: bw * (Number(r.value) || 0) / max };
  });
  const st = s.stamp ? rcStamp(cam, s.stampX || 1260, s.stampY || 860, s.stamp, RC.red, 60, -7) : null;
  const src = s.source ? el("div", "abs", cam, { left: x0 + "px", top: "990px", font: "22px 'Code'", color: RC.steel, letterSpacing: ".06em" }, esc("SOURCE · " + s.source)) : null;
  const at = s.at != null ? s.at : 0.3, D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.02);
    if (kick) setO(kick, eOut(seg(t, at - 0.2, 0.6))); if (title) { const q = eOut(seg(t, at, 0.8)); rcWipe(title, q); }
    R.forEach((o, i) => {
      const ra = o.r.at != null ? o.r.at : at + 0.6 + i * 0.9;
      setO(o.lab, eOut(seg(t, ra, 0.5)));
      const p = eOut(seg(t, ra + 0.15, 1.1));
      css(o.bar, "width", (o.w * p).toFixed(1) + "px");
      setO(o.num, eOut(seg(t, ra + 0.15, 0.4))); css(o.num, "left", (bx + o.w * p + 24).toFixed(1) + "px");
      o.num.textContent = countText(o.r.text || String(o.r.value), p);
      if (o.note) setO(o.note, eOut(seg(t, ra + 0.6, 0.6)));
      if (o.strike) css(o.strike, "width", ((o.w + 20) * eInOut(seg(t, o.r.strikeAt, 0.5))).toFixed(1) + "px");
    });
    if (st) st(seg(t, s.stampAt != null ? s.stampAt : 99, 0.35));
    if (src) setO(src, eOut(seg(t, at + 0.4, 0.8)));
  };
};

/* ------------------------------------------------------------------ counts (a sentence board) */
SCENES.counts = async (s, root) => {
  rcGround(root, s.img, 0.88);
  const cam = el("div", "full", root, {});
  const items = s.items || [];
  const cw = s.cw || 640, gap = 60, x0 = (W - (items.length * cw + (items.length - 1) * gap)) / 2;
  const kick = s.kicker ? el("div", "abs", cam, { left: 0, width: W + "px", top: "220px", textAlign: "center", font: "30px 'LabelB'", letterSpacing: ".42em", color: RC.steel }, esc(s.kicker)) : null;
  const I = items.map((it, i) => {
    const x = x0 + i * (cw + gap);
    const num = el("div", "abs", cam, { left: x + "px", width: cw + "px", top: "330px", textAlign: "center", font: `${s.numSize || 250}px 'Num'`, color: RC.bone, lineHeight: "1" }, "0");
    const lab = el("div", "abs", cam, { left: x + "px", width: cw + "px", top: "600px", textAlign: "center", font: "40px 'LabelB'", letterSpacing: ".36em", color: it.hi ? RC.amber : RC.steel, opacity: 0 }, esc(it.label));
    const strike = it.strikeAt != null ? el("div", "abs", cam, { left: (x + 60) + "px", top: "460px", height: "10px", width: "0", background: RC.red, transform: "rotate(-8deg)" }) : null;
    return { it, num, lab, strike };
  });
  const after = s.after ? el("div", "abs", cam, { left: 0, width: W + "px", top: "760px", textAlign: "center", font: "52px 'RecI'", color: RC.bone, opacity: 0 }, esc(s.after)) : null;
  const st = s.stamp ? rcStamp(cam, s.stampX || 1260, s.stampY || 700, s.stamp, RC.red, 54, -8) : null;
  const at = s.at != null ? s.at : 0.3, D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.025);
    if (kick) setO(kick, eOut(seg(t, at - 0.2, 0.6)));
    I.forEach((o, i) => {
      const a = o.it.at != null ? o.it.at : at + i * 1.2;
      const p = eOut(seg(t, a, 1.3));
      o.num.textContent = countText(String(o.it.value), p); setO(o.num, cl(seg(t, a, 0.2), 0, 1));
      setO(o.lab, eOut(seg(t, a + 0.7, 0.6)));
      if (o.strike) css(o.strike, "width", ((cw - 120) * eInOut(seg(t, o.it.strikeAt, 0.5))).toFixed(1) + "px");
    });
    if (after) setO(after, eOut(seg(t, s.afterAt != null ? s.afterAt : 99, 0.8)));
    if (st) st(seg(t, s.stampAt != null ? s.stampAt : 99, 0.35));
  };
};

/* ------------------------------------------------------------------ chain (a mechanism) */
SCENES.chain = async (s, root) => {
  rcGround(root, null);
  const cam = el("div", "full", root, {});
  const nodes = s.nodes || [];
  const n = nodes.length, nw = 330, y = s.y || 470, span = W - 360, gapx = (span - n * nw) / Math.max(1, n - 1);
  const X = i => 180 + i * (nw + gapx);
  const kick = s.kicker ? rcLabel(cam, 180, 190, s.kicker, RC.amber, 28) : null;
  const title = s.title ? el("div", "abs", cam, { left: "180px", top: "236px", font: "60px 'Rec'", color: RC.bone, whiteSpace: "nowrap" }, esc(s.title)) : null;
  const N = nodes.map((nd, i) => {
    const b = el("div", "abs", cam, { left: X(i) + "px", top: y + "px", width: nw + "px", height: "190px", border: `2px solid ${nd.gate ? RC.amber : "rgba(233,228,216,.55)"}`,
      background: nd.gate ? "rgba(226,163,59,.08)" : "rgba(233,228,216,.04)", opacity: 0 });
    el("div", "abs", b, { left: "22px", top: "20px", font: "22px 'Code'", color: RC.steel }, String(i + 1).padStart(2, "0"));
    el("div", "abs", b, { left: "22px", right: "18px", top: "62px", font: "46px 'LabelB'", letterSpacing: ".06em", color: nd.gate ? RC.amber : RC.bone, lineHeight: "1.05" }, esc(nd.label));
    if (nd.sub) el("div", "abs", b, { left: "22px", right: "18px", top: "128px", font: "26px 'RecI'", color: RC.steel, lineHeight: "1.15" }, esc(nd.sub));
    return b;
  });
  const A = nodes.slice(1).map((_, i) => {
    const x = X(i) + nw + 12, w = gapx - 24;
    const ln = el("div", "abs", cam, { left: x + "px", top: (y + 94) + "px", height: "3px", width: "0", background: RC.bone });
    const hd = el("div", "abs", cam, { left: (x + w - 18) + "px", top: (y + 84) + "px", width: 0, height: 0, borderTop: "12px solid transparent", borderBottom: "12px solid transparent",
      borderLeft: `20px solid ${RC.bone}`, opacity: 0 });
    return { ln, hd, w };
  });
  /* the delay clock between two nodes */
  let clock = null;
  if (s.delay != null) {
    const i = s.delay, cx = X(i) + nw + gapx / 2;
    const c = el("div", "abs", cam, { left: (cx - 70) + "px", top: (y + 250) + "px", width: "140px", height: "140px", borderRadius: "50%", border: `3px solid ${RC.amber}`, opacity: 0 });
    const hand = el("div", "abs", c, { left: "68px", top: "14px", width: "4px", height: "56px", background: RC.amber, transformOrigin: "2px 56px" });
    const lab = el("div", "abs", cam, { left: (cx - 200) + "px", width: "400px", top: (y + 410) + "px", textAlign: "center", font: "30px 'LabelB'", letterSpacing: ".34em", color: RC.amber, opacity: 0 }, esc(s.delayLabel || "DELAY"));
    clock = { c, hand, lab };
  }
  const cross = s.blockAt != null ? el("div", "abs", cam, { left: (X(n - 2) + nw + gapx / 2 - 60) + "px", top: (y + 34) + "px", font: "120px 'Num'", color: RC.red, opacity: 0 }, "×") : null;
  const at = s.at != null ? s.at : 0.3, D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.02);
    if (kick) setO(kick, eOut(seg(t, at - 0.2, 0.6))); if (title) rcWipe(title, eOut(seg(t, at, 0.8)));
    N.forEach((b, i) => { const a = nodes[i].at != null ? nodes[i].at : at + 0.6 + i * 1.0; const q = eOut(seg(t, a, 0.6)); setO(b, q); setT(b, 0, (1 - q) * 18); });
    A.forEach((o, i) => { const a = (nodes[i + 1].at != null ? nodes[i + 1].at : at + 0.6 + (i + 1) * 1.0) - 0.45; const p = eInOut(seg(t, a, 0.5));
      css(o.ln, "width", ((o.w - 16) * p).toFixed(1) + "px"); setO(o.hd, seg(t, a + 0.4, 0.15)); });
    if (clock) { const a = s.delayAt != null ? s.delayAt : at + 2; setO(clock.c, eOut(seg(t, a, 0.6))); setO(clock.lab, eOut(seg(t, a + 0.3, 0.6)));
      clock.hand.style.transform = `rotate(${(Math.max(0, t - a) * 140).toFixed(1)}deg)`; }
    if (cross) { const p = seg(t, s.blockAt, 0.3); setO(cross, p); cross.style.transform = `scale(${(1.6 - 0.6 * eOut5(p)).toFixed(3)})`; }
  };
};

/* ------------------------------------------------------------------ redacted */
SCENES.redacted = async (s, root) => {
  rcGround(root, null);
  const rows = s.rows || 8;
  const pw = 1180, ph = 200 + rows * 74 + 150, px = (W - pw) / 2, py = (H - ph) / 2;
  const page = el("div", "abs", root, { left: px + "px", top: py + "px", width: pw + "px", height: ph + "px", background: RC.paper, boxShadow: "0 50px 120px rgba(0,0,0,.6)" });
  el("div", "abs", page, { left: "70px", top: "50px", font: "24px 'LabelB'", letterSpacing: ".3em", color: "#5B6570" }, esc(s.header || "DEFENDANTS"));
  if (s.source) el("div", "abs", page, { left: "70px", top: "88px", font: "26px 'Code'", color: "#3A424C" }, esc(s.source));
  el("div", "abs", page, { left: "70px", right: "70px", top: "138px", borderTop: "1px solid rgba(28,33,40,.25)" });
  const R = rng(s.seed || 5);
  const items = [];
  for (let i = 0; i < rows; i++) {
    const y = 170 + i * 74;
    const lab = el("div", "abs", page, { left: "70px", top: y + "px", font: "28px 'Code'", color: "#3A424C", opacity: 0 }, esc((s.labels && s.labels[i % s.labels.length]) || `CASE ${String(i + 1).padStart(3, "0")}`));
    const bw = 240 + R() * 260;
    const bar = el("div", "abs", page, { left: "430px", top: (y - 2) + "px", height: "40px", width: "0", background: "#111418" });
    const tail = el("div", "abs", page, { left: (450 + bw) + "px", top: y + "px", font: "28px 'Code'", color: "#3A424C", opacity: 0 }, esc((s.tails && s.tails[i % s.tails.length]) || ""));
    items.push({ lab, bar, tail, bw });
  }
  const st = rcStamp(page, pw - 640, ph - 120, s.stamp || "NAMES WITHHELD", RC.red, 54, -5, true);
  const at = s.at != null ? s.at : 0.3, every = s.every || 0.35, D = s.duration;
  return t => {
    const a = eOut(seg(t, 0, 0.8)); setO(page, a);
    page.style.transform = `translateY(${((1 - a) * 24).toFixed(1)}px) scale(${(1 + 0.03 * drift(cl(t / D, 0, 1))).toFixed(4)}) rotate(0.5deg)`;
    items.forEach((o, i) => { const w = at + i * every;
      setO(o.lab, eOut(seg(t, w, 0.4))); setO(o.tail, eOut(seg(t, w + 0.3, 0.4)));
      css(o.bar, "width", (o.bw * eInOut(seg(t, w + 0.15, 0.4))).toFixed(1) + "px"); });
    st(seg(t, s.stampAt != null ? s.stampAt : at + rows * every + 0.4, 0.35));
  };
};

/* ------------------------------------------------------------------ wall (posters pasted at night) */
SCENES.wall = async (s, root) => {
  el("div", "full", root, { background: "#14110F" });
  /* bricks */
  el("div", "full", root, { backgroundImage: "linear-gradient(rgba(0,0,0,.55) 3px, transparent 3px), linear-gradient(90deg, rgba(0,0,0,.5) 3px, transparent 3px)",
    backgroundSize: "120px 52px", backgroundColor: "#2A2320", opacity: 0.9 });
  el("div", "full", root, { backgroundImage: "linear-gradient(90deg, rgba(0,0,0,.5) 3px, transparent 3px)", backgroundSize: "120px 104px", backgroundPosition: "60px 52px", opacity: 0.9 });
  el("div", "full", root, { background: "radial-gradient(ellipse at 50% 30%, rgba(255,190,110,.22) 0%, rgba(0,0,0,0) 55%)", mixBlendMode: "screen" });
  const cam = el("div", "full", root, {});
  const R = rng(s.seed || 3);
  const heads = s.heads || ["הודעה", "אזהרה", "קול קורא", "מחאה", "הודעה רבה"];
  const n = s.count || 7;
  const P = [];
  for (let i = 0; i < n; i++) {
    const w = 300 + R() * 90, h = w * 1.38;
    const x = 120 + (i % 4) * 430 + R() * 60, y = 80 + Math.floor(i / 4) * 470 + R() * 40;
    const p = el("div", "abs", cam, { left: x + "px", top: y + "px", width: w + "px", height: h + "px", background: i % 3 ? "#E4DECF" : "#D9D2BF",
      boxShadow: "0 18px 40px rgba(0,0,0,.55)", opacity: 0, transformOrigin: "50% 0" });
    el("div", "abs", p, { left: 0, right: 0, top: "30px", textAlign: "center", font: `${w * 0.17}px 'Heb'`, color: "#15181C", direction: "rtl" }, esc(heads[i % heads.length]));
    for (let k = 0; k < 9; k++) el("div", "abs", p, { left: (24 + R() * 10) + "px", right: (24 + R() * 40) + "px", top: (w * 0.32 + 26 + k * 30) + "px", height: "10px", background: "rgba(21,24,28,.55)" });
    P.push({ p, rot: (R() - 0.5) * 5 });
  }
  /* the one that matters */
  const big = el("div", "abs", cam, { left: (W / 2 - 290) + "px", top: "150px", width: "580px", height: "780px", background: "#EDE7D6", boxShadow: "0 30px 80px rgba(0,0,0,.7)", opacity: 0, transformOrigin: "50% 0" });
  el("div", "abs", big, { left: 0, right: 0, top: "40px", textAlign: "center", font: "56px 'Heb'", color: "#15181C", direction: "rtl" }, esc(s.bigHead || "אזהרה"));
  for (let k = 0; k < 4; k++) el("div", "abs", big, { left: "60px", right: (60 + k * 30) + "px", top: (150 + k * 34) + "px", height: "12px", background: "rgba(21,24,28,.5)" });
  const word = el("div", "abs", big, { left: 0, right: 0, top: "300px", textAlign: "center", font: "190px 'Heb'", color: RC.red, direction: "rtl", opacity: 0 }, esc(s.word || "מוסר"));
  const gloss = el("div", "abs", big, { left: 0, right: 0, top: "540px", textAlign: "center", font: "38px 'LabelB'", letterSpacing: ".32em", color: "#15181C", opacity: 0 }, esc(s.gloss || "MOSER · INFORMER"));
  for (let k = 0; k < 3; k++) el("div", "abs", big, { left: "60px", right: (90 + k * 50) + "px", top: (630 + k * 34) + "px", height: "12px", background: "rgba(21,24,28,.5)" });
  const at = s.at != null ? s.at : 0.2, every = s.every || 0.4, D = s.duration;
  return t => {
    cam.style.transformOrigin = "50% 45%"; cam.style.transform = `scale(${(1 + 0.05 * drift(cl(t / D, 0, 1))).toFixed(4)})`;
    P.forEach((o, i) => { const q = seg(t, at + i * every, 0.3); setO(o.p, q > 0 ? 1 : 0);
      o.p.style.transform = `rotate(${o.rot.toFixed(2)}deg) scale(${(1.06 - 0.06 * eOut(q)).toFixed(3)})`; });
    const bAt = s.bigAt != null ? s.bigAt : at + n * every + 0.3;
    const q = seg(t, bAt, 0.35); setO(big, q > 0 ? 1 : 0); big.style.transform = `rotate(-1.2deg) scale(${(1.08 - 0.08 * eOut(q)).toFixed(3)})`;
    const w = seg(t, s.wordAt != null ? s.wordAt : bAt + 0.7, 0.3); setO(word, w); word.style.transform = `scale(${(1.5 - 0.5 * eOut5(w)).toFixed(3)})`;
    setO(gloss, eOut(seg(t, (s.wordAt != null ? s.wordAt : bAt + 0.7) + 0.5, 0.6)));
  };
};

/* ------------------------------------------------------------------ docketline (a time axis) */
SCENES.docketline = async (s, root) => {
  rcGround(root, s.img, 0.88);
  const cam = el("div", "full", root, {});
  const a0 = Number(s.from), a1 = Number(s.to), x0 = 200, x1 = W - 200, y = s.y || 640;
  const X = v => x0 + (x1 - x0) * cl((v - a0) / Math.max(1, a1 - a0), 0, 1);
  const kick = s.kicker ? rcLabel(cam, x0, 190, s.kicker, RC.amber, 28) : null;
  const title = s.title ? el("div", "abs", cam, { left: x0 + "px", top: "236px", font: "60px 'Rec'", color: RC.bone, whiteSpace: "nowrap" }, esc(s.title)) : null;
  const base = el("div", "abs", cam, { left: x0 + "px", top: y + "px", height: "2px", width: "0", background: "rgba(233,228,216,.6)" });
  const ticks = (s.ticks || []).map(v => {
    const tk = el("div", "abs", cam, { left: (X(v) - 1) + "px", top: (y - 10) + "px", width: "2px", height: "22px", background: "rgba(233,228,216,.5)", opacity: 0 });
    const lb = el("div", "abs", cam, { left: (X(v) - 80) + "px", width: "160px", textAlign: "center", top: (y + 26) + "px", font: "26px 'Code'", color: RC.steel, opacity: 0 }, esc(String(v)));
    return { tk, lb };
  });
  const mark = el("div", "abs", cam, { left: (x0 - 9) + "px", top: (y - 9) + "px", width: "20px", height: "20px", borderRadius: "50%", background: RC.amber, boxShadow: `0 0 24px ${RC.amber}` });
  const E = (s.events || []).map((e, i) => {
    const up = e.up != null ? e.up : i % 2 === 0, x = X(Number(e.year));
    const stem = el("div", "abs", cam, { left: x + "px", top: (up ? y - 120 : y + 2) + "px", width: "2px", height: "0", background: e.hi ? RC.amber : RC.bone });
    const g = el("div", "abs", cam, { left: (x - 190) + "px", width: "380px", top: (up ? y - 250 : y + 140) + "px", textAlign: "center", opacity: 0 });
    el("div", "", g, { font: "44px 'Num'", color: e.hi ? RC.amber : RC.bone }, esc(e.when || String(e.year)));
    el("div", "", g, { font: "32px 'Rec'", color: RC.bone, lineHeight: "1.2", marginTop: "6px" }, esc(e.label || ""));
    return { e, stem, g, up };
  });
  const at = s.at != null ? s.at : 0.3, D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.02);
    if (kick) setO(kick, eOut(seg(t, at - 0.2, 0.6))); if (title) rcWipe(title, eOut(seg(t, at, 0.8)));
    css(base, "width", ((x1 - x0) * eInOut(seg(t, at, 1.2))).toFixed(1) + "px");
    ticks.forEach((k, i) => { const q = eOut(seg(t, at + 0.3 + i * 0.08, 0.4)); setO(k.tk, q); setO(k.lb, q); });
    let mx = x0;
    E.forEach(o => { const a = o.e.at != null ? o.e.at : at + 1; const q = eOut(seg(t, a, 0.7));
      if (t >= a) mx = Math.max(mx, X(Number(o.e.year)));
      css(o.stem, "height", (118 * q).toFixed(1) + "px"); setO(o.g, q); setT(o.g, 0, (1 - q) * (o.up ? 14 : -14)); });
    const cur = parseFloat(mark.style.left) + 9;
    const nx = cur + (mx - cur) * 0.18;
    css(mark, "left", (nx - 9).toFixed(1) + "px");
  };
};

/* ------------------------------------------------------------------ ripple (a life and its rings) */
SCENES.ripple = async (s, root) => {
  rcGround(root, null);
  const cam = el("div", "full", root, {});
  const cx = W / 2, cy = H / 2 + 20;
  const rings = s.rings || [];
  const core = el("div", "abs", cam, { left: (cx - 20) + "px", top: (cy - 20) + "px", width: "40px", height: "40px", borderRadius: "50%", background: RC.bone, opacity: 0 });
  const coreLab = el("div", "abs", cam, { left: (cx - 150) + "px", width: "300px", textAlign: "center", top: (cy + 30) + "px", font: "26px 'LabelB'", letterSpacing: ".34em", color: RC.bone, opacity: 0 }, esc(s.center || "YOU"));
  const G = rings.map((r, i) => {
    const rad = 110 + i * 78;
    const c = el("div", "abs", cam, { left: (cx - rad) + "px", top: (cy - rad) + "px", width: (2 * rad) + "px", height: (2 * rad) + "px", borderRadius: "50%",
      border: "3px solid rgba(233,228,216,.6)", opacity: 0 });
    const ang = -100 + i * (300 / Math.max(1, rings.length)), rx = cx + Math.cos(ang * Math.PI / 180) * rad, ry = cy + Math.sin(ang * Math.PI / 180) * rad;
    const lab = el("div", "abs", cam, { left: (rx + (Math.cos(ang * Math.PI / 180) < -0.2 ? -200 : 16)) + "px", top: (ry - 18) + "px", font: "30px 'LabelB'", letterSpacing: ".26em", color: RC.bone, opacity: 0, whiteSpace: "nowrap",
      background: "rgba(14,18,23,.85)", padding: "2px 10px" }, esc(r.label));
    return { r, c, lab, rad };
  });
  const at = s.at != null ? s.at : 0.2, D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.03);
    setO(core, eOut(seg(t, at, 0.5))); setO(coreLab, eOut(seg(t, at + 0.2, 0.6)));
    G.forEach((g, i) => {
      const a = g.r.at != null ? g.r.at : at + 0.5 + i * 0.6;
      const q = eOut(seg(t, a, 0.6));
      const cut = g.r.cutAt != null ? eInOut(seg(t, g.r.cutAt, 0.8)) : 0;
      setO(g.c, q * (1 - 0.75 * cut)); setO(g.lab, q * (1 - 0.6 * cut));
      g.c.style.borderColor = cut > 0 ? `rgba(179,53,46,${(0.6 + 0.4 * cut).toFixed(2)})` : "rgba(233,228,216,.6)";
      g.c.style.borderStyle = cut > 0.05 ? "dashed" : "solid";
      g.c.style.transform = `scale(${(1 + 0.18 * cut).toFixed(3)})`;
      g.lab.style.textDecoration = cut > 0.3 ? "line-through" : "none";
    });
    if (s.aloneAt != null) { const p = eOut(seg(t, s.aloneAt, 1)); core.style.background = p > 0 ? RC.red : RC.bone; }
  };
};

/* ------------------------------------------------------------------ ballot (a bloc) */
SCENES.ballot = async (s, root) => {
  rcGround(root, null);
  const cam = el("div", "full", root, {});
  const cols = s.cols || 40, rows = s.rows || 16, sz = 22, gap = 10;
  const gw = cols * (sz + gap), gh = rows * (sz + gap), gx = (W - gw) / 2, gy = 300;
  const kick = s.kicker ? el("div", "abs", cam, { left: gx + "px", top: "170px", font: "28px 'LabelB'", letterSpacing: ".34em", color: RC.amber }, esc(s.kicker)) : null;
  const title = s.title ? el("div", "abs", cam, { left: gx + "px", top: "212px", font: "54px 'Rec'", color: RC.bone, whiteSpace: "nowrap" }, esc(s.title)) : null;
  const R = rng(s.seed || 9);
  const dots = [];
  const bloc = s.bloc || 0.7;
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const d = el("div", "abs", cam, { left: (gx + c * (sz + gap)) + "px", top: (gy + r * (sz + gap)) + "px", width: sz + "px", height: sz + "px", borderRadius: "50%",
      background: "rgba(233,228,216,.28)" });
    const inBloc = (c / cols) < bloc + (R() - 0.5) * 0.04;
    dots.push({ d, inBloc, k: R() });
  }
  const note = s.note ? el("div", "abs", cam, { left: gx + "px", top: (gy + gh + 30) + "px", font: "30px 'Code'", color: RC.steel, opacity: 0 }, esc(s.note)) : null;
  const at = s.at != null ? s.at : 0.3, blocAt = s.blocAt != null ? s.blocAt : at + 1.6, D = s.duration;
  return t => {
    rcCam(cam, t, D, 0.02);
    if (kick) setO(kick, eOut(seg(t, at - 0.2, 0.6))); if (title) rcWipe(title, eOut(seg(t, at, 0.8)));
    dots.forEach(o => {
      setO(o.d, eOut(seg(t, at + o.k * 0.8, 0.3)));
      const p = o.inBloc ? eOut(seg(t, blocAt, 0.45)) : 0;
      o.d.style.background = p > 0.5 ? RC.amber : "rgba(233,228,216,.28)";
      o.d.style.transform = `scale(${(1 + 0.25 * Math.sin(Math.PI * p)).toFixed(3)})`;
    });
    if (note) setO(note, eOut(seg(t, blocAt + 0.6, 0.6)));
  };
};

/* ------------------------------------------------------------------ overlays */
/* the evidence viewer around a clip rendered with inset=[x, y, w, h] */
OVERLAYS.casebox = (o, root) => {
  const [x, y, w, h] = o.box || [250, 110, 1420, 799];
  const g = "#0B0F14";
  el("div", "abs", root, { left: 0, top: 0, width: W + "px", height: y + "px", background: g });
  el("div", "abs", root, { left: 0, top: (y + h) + "px", width: W + "px", height: (H - y - h) + "px", background: g });
  el("div", "abs", root, { left: 0, top: y + "px", width: x + "px", height: h + "px", background: g });
  el("div", "abs", root, { left: (x + w) + "px", top: y + "px", width: (W - x - w) + "px", height: h + "px", background: g });
  el("div", "abs", root, { left: 0, top: 0, width: W + "px", height: H + "px", backgroundImage: "linear-gradient(rgba(233,228,216,.03) 1px, transparent 1px), linear-gradient(90deg, rgba(233,228,216,.03) 1px, transparent 1px)", backgroundSize: "60px 60px", pointerEvents: "none" });
  el("div", "abs", root, { left: (x - 2) + "px", top: (y - 2) + "px", width: (w + 4) + "px", height: (h + 4) + "px", border: "2px solid rgba(233,228,216,.32)", boxShadow: "inset 0 0 80px rgba(0,0,0,.5)" });
  /* corner brackets */
  for (const [cx, cy, bl, bt] of [[x - 14, y - 14, 1, 1], [x + w - 34, y - 14, 0, 1], [x - 14, y + h - 34, 1, 0], [x + w - 34, y + h - 34, 0, 0]])
    el("div", "abs", root, { left: cx + "px", top: cy + "px", width: "48px", height: "48px", borderLeft: bl ? `4px solid ${RC.amber}` : "none", borderRight: bl ? "none" : `4px solid ${RC.amber}`,
      borderTop: bt ? `4px solid ${RC.amber}` : "none", borderBottom: bt ? "none" : `4px solid ${RC.amber}` });
  const tag = el("div", "abs", root, { left: x + "px", top: (y - 56) + "px", font: "26px 'LabelB'", letterSpacing: ".3em", color: RC.amber, whiteSpace: "nowrap" }, esc(o.exhibit || "EXHIBIT"));
  const cap = o.caption ? el("div", "abs", root, { left: x + "px", top: (y + h + 22) + "px", font: "26px 'Code'", color: RC.bone, whiteSpace: "nowrap" }, esc(o.caption)) : null;
  const tc = el("div", "abs", root, { left: (x + w - 360) + "px", width: "360px", textAlign: "right", top: (y - 52) + "px", font: "24px 'Code'", color: RC.steel }, "");
  const rec = el("div", "abs", root, { left: (x + w - 380) + "px", top: (y - 46) + "px", width: "12px", height: "12px", borderRadius: "50%", background: RC.red });
  const src = o.source ? el("div", "abs", root, { left: (x + w - 700) + "px", width: "700px", textAlign: "right", top: (y + h + 24) + "px", font: "22px 'Code'", color: RC.steel, whiteSpace: "nowrap" }, esc("SOURCE · " + o.source)) : null;
  const t0 = o.tc0 || 0;
  return t => {
    const s = t0 + t, hh = Math.floor(s / 3600), mm = Math.floor(s / 60) % 60, ss = Math.floor(s) % 60, ff = Math.floor((s % 1) * 30);
    tc.textContent = `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}:${String(ff).padStart(2, "0")}`;
    setO(rec, Math.sin(t * 3.2) > 0 ? 1 : 0.25);
    setO(tag, eOut(seg(t, 0.1, 0.5))); if (cap) setO(cap, eOut(seg(t, 0.3, 0.6))); if (src) setO(src, eOut(seg(t, 0.5, 0.6)));
  };
};
OVERLAYS.source = (o, root) => {
  const at = o.at != null ? o.at : 0.4;
  const box = el("div", "abs", root, { right: "80px", top: "70px", background: "rgba(10,13,17,.82)", borderLeft: `4px solid ${RC.amber}`, padding: "12px 22px 10px", opacity: 0 });
  el("div", "", box, { font: "20px 'LabelB'", letterSpacing: ".3em", color: RC.amber }, "SOURCE");
  const tx = el("div", "", box, { font: "28px 'Code'", color: RC.bone, whiteSpace: "nowrap", marginTop: "2px" }, "");
  return t => { setO(box, eOut(seg(t, at, 0.4))); typeOn(tx, o.text || "", t, at + 0.2, 40, false); };
};
OVERLAYS.place = (o, root) => {
  const at = o.at != null ? o.at : 0.4;
  const sh = el("div", "full", root, { background: "linear-gradient(0deg, rgba(8,10,13,.7) 0%, rgba(8,10,13,0) 32%)", opacity: 0 });
  const box = el("div", "abs", root, { left: "110px", bottom: "96px" });
  const rule = el("div", "", box, { width: "0", borderTop: `2px solid ${RC.amber}`, marginBottom: "14px" });
  const nm = el("div", "", box, { font: `${o.size || 64}px 'Rec'`, color: RC.bone, whiteSpace: "nowrap", textShadow: "0 4px 24px rgba(0,0,0,.7)" }, esc(o.name || ""));
  const sub = o.sub ? el("div", "", box, { font: "26px 'Code'", color: RC.steel, whiteSpace: "nowrap", marginTop: "6px" }, "") : null;
  return t => {
    setO(sh, eOut(seg(t, at - 0.2, 0.7)));
    css(rule, "width", (240 * eInOut(seg(t, at, 0.8))).toFixed(1) + "px");
    rcWipe(nm, eOut(seg(t, at + 0.15, 0.8)));
    if (sub) typeOn(sub, o.sub, t, at + 0.7, 36, false);
  };
};
