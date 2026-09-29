/* scenes_doc.js - the calm documentary scenes. Nothing slams, nothing shakes: text fades in
   over slowly moving pictures, lines draw themselves, numbers count up gently.

   doctitle   Chapter card: a small kicker, a serif title and a thin rule over a dimmed,
              slowly pushing photograph.
   textcard   One or two lines of text over a darkened photo (a fact, a question, a quote).
   bars       Horizontal bars that grow to their values - a calm comparison chart.
   ledgerlist A household ledger: rows of items with amounts that add up to a total.

   Overlays (any scene, clips included):
   place      Location / date caption bottom-left: small caps over a short gold rule.
   doclower   Name and role, left-aligned, a thin rule - fades in and out.
*/
"use strict";

OVERLAYS.place = (o, root) => {
  const x = o.x != null ? o.x : 96, y = o.y != null ? o.y : 930;
  const wrap = el("div", "abs", root, { left: x + "px", top: y + "px" });
  const rule = el("div", "abs", wrap, { left: 0, top: 0, width: "0", height: "2px", background: PAL.gold });
  const t = el("div", "abs", wrap, { left: 0, top: "14px", font: `${o.size || 30}px 'Barlow'`, letterSpacing: ".18em", color: "#F3EEE4",
    whiteSpace: "nowrap", textTransform: "uppercase", textShadow: "0 2px 12px rgba(0,0,0,.85)" }, esc(o.text || ""));
  const sub = o.sub ? el("div", "abs", wrap, { left: 0, top: `${(o.size || 30) + 26}px`, font: `${(o.size || 30) * 0.8}px 'GaramondI'`,
    color: "#E6E0D4", whiteSpace: "nowrap", textShadow: "0 2px 12px rgba(0,0,0,.85)" }, esc(o.sub)) : null;
  const at = o.at != null ? o.at : 0.6;
  return tt => {
    const a = eOut(seg(tt, at, 0.9));
    css(rule, "width", (a * 80).toFixed(1) + "px");
    const b = eOut(seg(tt, at + 0.3, 1.0));
    setO(t, b); setT(t, 0, (1 - b) * 8);
    if (sub) setO(sub, eOut(seg(tt, at + 0.6, 1.0)));
    if (o.out != null) setO(wrap, 1 - seg(tt, o.out, 0.8));
  };
};

OVERLAYS.doclower = (o, root) => {
  const x = o.x != null ? o.x : 96, y = o.y != null ? o.y : 850;
  const wrap = el("div", "abs", root, { left: x + "px", top: y + "px" });
  const nm = el("div", "abs", wrap, { left: 0, top: 0, font: `${o.size || 52}px 'DMSerif'`, color: "#F3EEE4", whiteSpace: "nowrap",
    textShadow: "0 4px 24px rgba(0,0,0,.8)" }, esc(o.name || ""));
  const rule = el("div", "abs", wrap, { left: 0, top: `${(o.size || 52) * 1.3 + 6}px`, width: "0", height: "2px", background: PAL.gold });
  const rl = el("div", "abs", wrap, { left: 0, top: `${(o.size || 52) * 1.3 + 20}px`, font: "24px 'Barlow'", letterSpacing: ".14em",
    color: "#E6E0D4", whiteSpace: "nowrap", textTransform: "uppercase", textShadow: "0 2px 12px rgba(0,0,0,.85)" }, esc(o.role || ""));
  const at = o.at != null ? o.at : 0.6;
  return t => {
    const a = eOut(seg(t, at, 1.0)); setO(nm, a); setT(nm, 0, (1 - a) * 10);
    css(rule, "width", (eOut(seg(t, at + 0.3, 0.9)) * 120).toFixed(1) + "px");
    setO(rl, eOut(seg(t, at + 0.5, 1.0)));
    if (o.out != null) setO(wrap, 1 - seg(t, o.out, 0.8));
  };
};

SCENES.doctitle = async (s, root) => {
  const L = s.img ? photoLayer(root, Object.assign({ move: "in", zoom: 1.08 }, s)) : null;
  if (!L) paperGround(root, "cork");
  el("div", "full", root, { background: `rgba(10,10,12,${s.dim != null ? s.dim : 0.55})` });
  vignette(root, 0.6);
  const k = el("div", "abs", root, { left: 0, width: W + "px", top: "400px", textAlign: "center", font: "28px 'Barlow'",
    letterSpacing: ".4em", color: PAL.gold, textTransform: "uppercase" }, esc(s.kicker || ""));
  const tt = el("div", "abs", root, { left: "160px", width: W - 320 + "px", top: "450px", textAlign: "center",
    font: `${s.size || 96}px 'DMSerif'`, color: "#F3EEE4", lineHeight: "1.12", textShadow: "0 10px 40px rgba(0,0,0,.6)" }, esc(s.title || ""));
  const rule = el("div", "abs", root, { left: W / 2 + "px", top: "0", height: "2px", width: "0", background: PAL.gold });
  const sub = s.sub ? el("div", "abs", root, { left: 0, width: W + "px", top: "0", textAlign: "center", font: "34px 'GaramondI'",
    color: "#E6E0D4" }, esc(s.sub)) : null;
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(k, eOut(seg(t, 0.3, 1.0)));
    const a = eOut(seg(t, 0.6, 1.3)); setO(tt, a); setT(tt, 0, (1 - a) * 14);
    const ry = tt.offsetTop + tt.offsetHeight + 26;
    const w = eInOut(seg(t, 1.1, 1.2)) * 260;
    css(rule, "top", ry + "px"); css(rule, "width", w.toFixed(0) + "px"); css(rule, "left", (W / 2 - w / 2).toFixed(0) + "px");
    if (sub) { css(sub, "top", ry + 30 + "px"); setO(sub, eOut(seg(t, 1.5, 1.2))); }
    if (s.fadeOut !== false) setO(root.firstChild, 1);
  };
};

SCENES.textcard = async (s, root) => {
  const L = s.img ? photoLayer(root, Object.assign({ move: "in", zoom: 1.08 }, s)) : null;
  if (!L) paperGround(root, "cork");
  el("div", "full", root, { background: `rgba(10,10,12,${s.dim != null ? s.dim : 0.62})` });
  vignette(root, 0.55);
  const lines = (s.lines || []).map((ln, i) => {
    const d = el("div", "abs", root, { left: "200px", width: W - 400 + "px", top: 0, textAlign: s.align || "center",
      font: `${ln.size || 64}px '${ln.font || "DMSerif"}'`, color: ln.color || "#F3EEE4", lineHeight: "1.2",
      textShadow: "0 8px 32px rgba(0,0,0,.6)" }, esc(ln.text));
    return { d, ln };
  });
  const D = s.duration;
  let laid = false;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    if (!laid) {
      const gap = s.gap || 28, total = lines.reduce((a, o) => a + o.d.offsetHeight, 0) + gap * (lines.length - 1);
      let y = (H - total) / 2 + (s.dy || 0);
      lines.forEach(o => { o.d.style.top = y + "px"; y += o.d.offsetHeight + gap; });
      laid = true;
    }
    lines.forEach(({ d, ln }, i) => {
      const at = ln.at != null ? ln.at : 0.4 + i * 0.9;
      const a = eOut(seg(t, at, 1.1)); setO(d, a); setT(d, 0, (1 - a) * 12);
    });
  };
};

SCENES.bars = async (s, root) => {
  const L = s.img ? darkPhoto(root, s, s.dim != null ? s.dim : 0.78) : (paperGround(root, "cork"), null);
  vignette(root, 0.5);
  const x0 = 260, maxW = s.maxW || 1100;
  const title = el("div", "abs", root, { left: x0 + "px", top: "150px", font: "54px 'DMSerif'", color: "#F3EEE4" }, esc(s.title || ""));
  const note = s.note ? el("div", "abs", root, { left: x0 + "px", top: "230px", font: "28px 'GaramondI'", color: "#CFC8BA" }, esc(s.note)) : null;
  const vmax = s.max || Math.max(...(s.bars || []).map(b => b.value));
  const rows = (s.bars || []).map((b, i) => {
    const y = (s.y0 || 330) + i * (s.gap || 130);
    const lab = el("div", "abs", root, { left: x0 + "px", top: y + "px", font: "28px 'Barlow'", letterSpacing: ".08em", color: "#E6E0D4",
      textTransform: "uppercase", whiteSpace: "nowrap" }, esc(b.label));
    const bar = el("div", "abs", root, { left: x0 + "px", top: y + 44 + "px", height: "40px", width: "0", background: b.color || PAL.gold, opacity: 0.92 });
    const val = el("div", "abs", root, { left: x0 + "px", top: y + 40 + "px", font: "40px 'DMSerif'", color: "#F3EEE4", whiteSpace: "nowrap" }, "");
    return { b, lab, bar, val };
  });
  const src = s.source ? el("div", "abs", root, { left: x0 + "px", top: "990px", font: "20px 'Barlow'", letterSpacing: ".14em",
    color: "rgba(243,238,228,.6)", textTransform: "uppercase" }, esc(s.source)) : null;
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(title, eOut(seg(t, 0.2, 0.9))); if (note) setO(note, eOut(seg(t, 0.6, 0.9)));
    rows.forEach(({ b, lab, bar, val }, i) => {
      const at = b.at != null ? b.at : 0.8 + i * 0.6;
      setO(lab, eOut(seg(t, at, 0.7)));
      const g = eInOut(seg(t, at + 0.2, 1.4));
      const w = (b.value / vmax) * maxW * g;
      css(bar, "width", w.toFixed(0) + "px");
      const txt = countText(b.text || String(b.value), g);
      if (val._s !== txt) { val.textContent = txt; val._s = txt; }
      setT(val, w + 22, 0); setO(val, cl(g * 3, 0, 1));
    });
    if (src) setO(src, eOut(seg(t, 1.5, 1.0)));
  };
};

SCENES.ledgerlist = async (s, root) => {
  const L = s.img ? darkPhoto(root, s, s.dim != null ? s.dim : 0.8) : (paperGround(root, "cork"), null);
  vignette(root, 0.5);
  const X = 420, WD = 1080;
  const title = el("div", "abs", root, { left: X + "px", top: "140px", width: WD + "px", font: "50px 'DMSerif'", color: "#F3EEE4" }, esc(s.title || ""));
  const rows = (s.items || []).map((it, i) => {
    const y = (s.y0 || 270) + i * (s.gap || 86);
    const r = el("div", "abs", root, { left: X + "px", top: y + "px", width: WD + "px", display: "flex", justifyContent: "space-between",
      font: "36px 'Elite'", color: "#E6E0D4", borderBottom: "1px solid rgba(243,238,228,.18)", paddingBottom: "12px" });
    el("span", "", r, {}, esc(it.label));
    el("span", "", r, { font: "38px 'DMSerif'", color: it.color || "#F3EEE4" }, esc(it.value || ""));
    return { r, it };
  });
  const tot = s.total ? el("div", "abs", root, { left: X + "px", top: (s.y0 || 270) + rows.length * (s.gap || 86) + 24 + "px", width: WD + "px",
    display: "flex", justifyContent: "space-between", font: "40px 'DMSerif'", color: PAL.gold, borderTop: `2px solid ${PAL.gold}`, paddingTop: "16px" },
    `<span>${esc(s.total.label)}</span><span>${esc(s.total.value)}</span>`) : null;
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(title, eOut(seg(t, 0.2, 0.9)));
    rows.forEach(({ r, it }, i) => { const a = eOut(seg(t, it.at != null ? it.at : 0.8 + i * 0.5, 0.9)); setO(r, a); setT(r, (1 - a) * 20, 0); });
    if (tot) setO(tot, eOut(seg(t, s.total.at != null ? s.total.at : 0.8 + rows.length * 0.5 + 0.4, 1.0)));
  };
};

/* sizechart - household size on the x axis, a column per size for a threshold that rises
   with every person, and one fixed dashed line for an income. Columns that climb past the
   income line turn gold: "the same income qualifies once the family is big enough".
   Heights are relative (illustrative) unless the spec gives real values. */
SCENES.sizechart = async (s, root) => {
  const L = s.img ? darkPhoto(root, s, s.dim != null ? s.dim : 0.82) : (paperGround(root, "cork"), null);
  vignette(root, 0.5);
  const sizes = s.sizes || [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  const base = s.base || 1, step = s.step || 0.34;          /* threshold(size) = base + step * (size - 2) */
  const vals = sizes.map((n, i) => s.values ? s.values[i] : base + step * (n - sizes[0]));
  const vmax = Math.max(...vals, s.income || 0) * 1.08;
  const X0 = 300, X1 = 1640, Y0 = 880, HT = 560;
  const cw = (X1 - X0) / sizes.length;
  const title = el("div", "abs", root, { left: X0 + "px", top: "120px", font: "52px 'DMSerif'", color: "#F3EEE4" }, esc(s.title || ""));
  const note = s.note ? el("div", "abs", root, { left: X0 + "px", top: "196px", font: "28px 'GaramondI'", color: "#CFC8BA" }, esc(s.note)) : null;
  el("div", "abs", root, { left: X0 + "px", top: Y0 + "px", width: X1 - X0 + "px", height: "2px", background: "rgba(243,238,228,.4)" });
  const cols = sizes.map((n, i) => {
    const x = X0 + i * cw + cw * 0.18;
    const bar = el("div", "abs", root, { left: x + "px", top: Y0 + "px", width: cw * 0.64 + "px", height: "0", background: "rgba(243,238,228,.35)" });
    const lab = el("div", "abs", root, { left: x - 10 + "px", top: Y0 + 14 + "px", width: cw * 0.64 + 20 + "px", textAlign: "center",
      font: "28px 'Barlow'", color: "#E6E0D4" }, String(n));
    return { bar, lab, v: vals[i], i };
  });
  const xl = el("div", "abs", root, { left: X0 + "px", top: Y0 + 56 + "px", width: X1 - X0 + "px", textAlign: "center", font: "24px 'Barlow'",
    letterSpacing: ".16em", color: "#CFC8BA", textTransform: "uppercase" }, esc(s.xlabel || "people in the household"));
  const yInc = s.income != null ? Y0 - (s.income / vmax) * HT : null;
  const inc = yInc != null ? el("div", "abs", root, { left: X0 + "px", top: yInc + "px", width: "0", height: "0", borderTop: `4px dashed ${PAL.red}` }) : null;
  const incLab = yInc != null ? el("div", "abs", root, { left: X1 - 460 + "px", top: yInc - 52 + "px", width: "460px", textAlign: "right",
    font: "32px 'DMSerif'", color: PAL.red }, esc(s.incomeLabel || "same income")) : null;
  const legend = el("div", "abs", root, { left: X0 + "px", top: "260px", font: "26px 'Barlow'", color: "#E6E0D4" },
    `<span style="display:inline-block;width:22px;height:22px;background:rgba(243,238,228,.35);vertical-align:-3px;margin-right:10px"></span>${esc(s.barLabel || "eligibility limit")}`);
  const src = s.source ? el("div", "abs", root, { left: X0 + "px", top: "1000px", font: "20px 'Barlow'", letterSpacing: ".14em",
    color: "rgba(243,238,228,.55)", textTransform: "uppercase" }, esc(s.source)) : null;
  const D = s.duration, A = s.at != null ? s.at : 0.8, per = s.per || 0.35, IA = s.incomeAt != null ? s.incomeAt : A + sizes.length * per + 0.3;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(title, eOut(seg(t, 0.2, 0.9))); if (note) setO(note, eOut(seg(t, 0.5, 0.9))); setO(legend, eOut(seg(t, 0.6, 0.9)));
    setO(xl, eOut(seg(t, 0.6, 0.9)));
    cols.forEach(c => {
      const g = eOut(seg(t, A + c.i * per, 0.9));
      const h = (c.v / vmax) * HT * g;
      css(c.bar, "height", h.toFixed(1) + "px"); css(c.bar, "top", (Y0 - h).toFixed(1) + "px");
      const over = yInc != null && t >= IA + 0.4 && (Y0 - (c.v / vmax) * HT) < yInc;
      css(c.bar, "background", over ? PAL.gold : "rgba(243,238,228,.35)");
      css(c.lab, "color", over ? PAL.gold : "#E6E0D4");
    });
    if (inc) { css(inc, "width", (eInOut(seg(t, IA, 1.2)) * (X1 - X0)).toFixed(0) + "px"); setO(incLab, eOut(seg(t, IA + 0.6, 0.8))); }
    if (src) setO(src, eOut(seg(t, 1.2, 1.0)));
  };
};
