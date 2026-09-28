/* scenes_data.js - numbers, words and diagrams.

   title      The opening title over a photograph.
   stat       A hero number that counts up, with kicker, note and source (Lotus style).
   quote      A line of speech revealed word by word over a darkened photo, with a
              marker behind the words that matter and an attribution.
   words      Kinetic type: big words slammed onto the frame one after another.
   ledger     Arithmetic on old paper, written line by line, total circled in red.
   timeline   Dated events along a rule; the camera travels to each one in turn.
   measure    Two bars measured against each other (cubits vs. the formation).
   checklist  A list of findings, each ticked, questioned or crossed as it lands.
*/
"use strict";

function darkPhoto(root, s, dimAlpha) {
  if (!s.img) { paperGround(root, s.ground || "dark"); return null; }
  const L = photoLayer(root, Object.assign({ move: s.move || "in", zoom: s.zoom || 1.1 }, s));
  el("div", "full", root, { background: `rgba(6,6,7,${dimAlpha})` });
  return L;
}

SCENES.title = async (s, root) => {
  const L = photoLayer(root, Object.assign({ move: "in", zoom: 1.15 }, s));
  el("div", "full", root, { background: "linear-gradient(180deg, rgba(0,0,0,.25) 0%, rgba(0,0,0,.15) 40%, rgba(0,0,0,.8) 100%)" });
  vignette(root, 0.65);
  const k = el("div", "abs", root, { left: 0, width: W + "px", top: "300px", textAlign: "center", font: "34px 'Barlow'", letterSpacing: ".5em", color: PAL.mustard }, esc(s.kicker || ""));
  const t1 = el("div", "abs", root, { left: 0, width: W + "px", top: "350px", textAlign: "center", font: "210px 'Anton'", color: "#F4EFE4", letterSpacing: ".02em", textShadow: "0 20px 60px rgba(0,0,0,.6)" }, esc(s.title || ""));
  const t2 = el("div", "abs", root, { left: 0, width: W + "px", top: "610px", textAlign: "center", font: "64px 'DMSerif'", color: "#F4EFE4", textShadow: "0 8px 30px rgba(0,0,0,.8)" }, esc(s.subtitle || ""));
  const rule = el("div", "abs", root, { left: W / 2 + "px", top: "720px", height: "3px", width: "0", background: PAL.mustard });
  const t3 = el("div", "abs", root, { left: 0, width: W + "px", top: "750px", textAlign: "center", font: "30px 'Barlow'", letterSpacing: ".4em", color: "#E9E2D2" }, esc(s.tagline || ""));
  const D = s.duration;
  return t => {
    L.draw(drift(cl(t / D, 0, 1)));
    setO(k, eOut(seg(t, 0.3, 0.8)));
    const a = eOut5(seg(t, 0.5, 1.0));
    setO(t1, a); setT(t1, 0, 0, lerp(1.12, 1, a));
    t1.style.letterSpacing = lerp(0.2, 0.02, a).toFixed(3) + "em";
    const b = eOut(seg(t, 1.2, 0.8)); setO(t2, b); setT(t2, 0, (1 - b) * 20);
    const w = eInOut(seg(t, 1.6, 0.8)) * 600; css(rule, "width", w.toFixed(0) + "px"); css(rule, "left", (W / 2 - w / 2).toFixed(0) + "px");
    setO(t3, eOut(seg(t, 2.0, 0.8)));
    if (s.out != null) { const o = 1 - seg(t, s.out, 0.6); [k, t1, t2, rule, t3].forEach(e => setO(e, Math.min(+e._o || 1, o))); }
  };
};

SCENES.stat = async (s, root) => {
  const L = darkPhoto(root, s, s.dim != null ? s.dim : 0.62);
  vignette(root, 0.6);
  const left = s.align !== "center";
  const x = left ? 150 : 0, wd = left ? 1400 : W;
  const box = el("div", "abs", root, { left: x + "px", top: (s.y || 330) + "px", width: wd + "px", textAlign: left ? "left" : "center" });
  const k = el("div", "", box, { font: "30px 'BarlowB'", letterSpacing: ".3em", color: PAL.mustard, height: "44px" }, esc(s.kicker || ""));
  const v = el("div", "", box, { font: `${s.size || 230}px '${s.font || "Garamond"}'`, lineHeight: "1.02", color: "#F6F1E6", textShadow: "0 12px 50px rgba(0,0,0,.6)", whiteSpace: "nowrap" }, esc(s.value));
  const n = el("div", "", box, { font: "46px 'GaramondI'", color: "#E8E0CF", marginTop: "6px" }, esc(s.note || ""));
  const src = s.source ? el("div", "abs", root, { left: x + 4 + "px", top: "900px", font: "20px 'Barlow'", letterSpacing: ".25em", color: "rgba(233,226,210,.65)", width: wd + "px", textAlign: left ? "left" : "center" }, esc(s.source)) : null;
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(k, eOut(seg(t, 0.2, 0.5)));
    const a = eOut(seg(t, 0.35, 0.6)); setO(v, a); setT(v, 0, (1 - a) * 30);
    const p = s.count === false ? 1 : eOut5(seg(t, 0.35, s.countFor || 1.6));
    const txt = countText(s.value, p);
    if (v._s !== txt) { v.textContent = txt; v._s = txt; }
    const b = eOut(seg(t, (s.noteAt || 1.4), 0.7)); setO(n, b); setT(n, 0, (1 - b) * 16);
    if (src) setO(src, seg(t, 1.8, 0.6));
  };
};

SCENES.quote = async (s, root) => {
  const L = darkPhoto(root, s, s.dim != null ? s.dim : 0.66);
  vignette(root, 0.6);
  const wrap = el("div", "abs", root, { left: "200px", top: "0", width: "1520px" });
  const q = el("div", "", wrap, { font: `${s.size || 78}px '${s.font || "DMSerif"}'`, lineHeight: "1.18", color: "#F4EFE4", textShadow: "0 8px 40px rgba(0,0,0,.6)" });
  const hot = (s.highlight || []).map(h => h.toLowerCase());
  const words = (s.text || "").split(/\s+/);
  const spans = words.map(w => {
    const sp = el("span", "", q, { position: "relative", display: "inline-block", marginRight: ".26em" });
    const clean = w.toLowerCase().replace(/[^a-z0-9%']/g, "");
    const isHot = hot.some(h => h.split(/\s+/).includes(clean));
    let mk = null;
    if (isHot) mk = el("span", "abs", sp, { left: "-4px", right: "-4px", top: "58%", height: "34%", background: PAL.red, opacity: 0.85, transformOrigin: "0 50%", transform: "scaleX(0)" });
    el("span", "", sp, { position: "relative" }, esc(w));
    return { sp, mk };
  });
  const who = el("div", "", wrap, { marginTop: "34px", font: "30px 'Barlow'", letterSpacing: ".25em", color: PAL.mustard }, s.who ? "— " + esc(s.who) : "");
  const D = s.duration, rate = s.rate || Math.max(3.2, words.length / Math.max(1, (D - 1.6) * 0.8));
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    if (!wrap._y) { wrap.style.top = ((H - wrap.offsetHeight) / 2 - 20) + "px"; wrap._y = 1; }
    spans.forEach((o, i) => {
      const at = 0.3 + i / rate;
      const a = eOut(seg(t, at, 0.45));
      setO(o.sp, a); setT(o.sp, 0, (1 - a) * 18);
      if (o.mk) o.mk.style.transform = `scaleX(${eOut(seg(t, at + 0.35, 0.35)).toFixed(3)})`;
    });
    setO(who, eOut(seg(t, 0.3 + words.length / rate + 0.2, 0.6)));
  };
};

SCENES.words = async (s, root) => {
  const L = s.img ? darkPhoto(root, s, s.dim != null ? s.dim : 0.7) : (paperGround(root, s.ground || "dark"), null);
  vignette(root, 0.6);
  const items = (s.items || []).map(it => {
    const d = el("div", "abs", root, {
      left: 0, top: 0, font: `${it.size || 150}px '${it.font || "Anton"}'`, color: it.color || "#F4EFE4", whiteSpace: "nowrap",
      letterSpacing: ".01em", textShadow: "0 16px 50px rgba(0,0,0,.6)", transformOrigin: "50% 50%",
    }, esc(it.text));
    if (it.strike) el("div", "abs", d, { left: "-2%", top: "52%", height: "10%", width: "0", background: PAL.red });
    return { d, it };
  });
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    items.forEach(({ d, it }) => {
      const e = entrance(it.from || "slam", t, it.at || 0, it.rot || 0, 5);
      if (!e) { vis(d, false); return; }
      vis(d, true);
      const w = d.offsetWidth, h = d.offsetHeight;
      const x = it.x != null ? it.x : W / 2, y = it.y != null ? it.y : H / 2;
      setT(d, x - w / 2 + e[0], y - h / 2 + e[1], e[3], e[2]);
      setO(d, e[4] * (it.out != null ? 1 - seg(t, it.out, 0.25) : 1) * (it.dimAt != null ? lerp(1, 0.28, seg(t, it.dimAt, 0.3)) : 1));
      if (it.strike) css(d.firstElementChild, "width", (eOut(seg(t, it.strike, 0.35)) * 104).toFixed(1) + "%");
    });
  };
};

SCENES.ledger = async (s, root) => {
  const board = el("div", "full", root, { transformOrigin: "50% 50%" });
  pic("parchment.jpg", board, { width: W + "px", height: H + "px" });
  const lines = (s.lines || []).map((ln, i) => {
    const d = el("div", "abs", board, {
      left: (ln.x || 360) + "px", top: (ln.y != null ? ln.y : 200 + i * 110) + "px", font: `${ln.size || 64}px '${ln.font || "GaramondI"}'`,
      color: ln.color || "#2a1f14", whiteSpace: "nowrap",
    }, esc(ln.text));
    return { d, ln };
  });
  const rule = s.ruleY ? el("div", "abs", board, { left: "340px", top: s.ruleY + "px", height: "4px", width: "0", background: "#2a1f14" }) : null;
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  Object.assign(svg.style, { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px", overflow: "visible" });
  board.appendChild(svg);
  let ring = null, len = 0;
  if (s.circle) {
    const c = s.circle, r = rng(3), pts = [];
    for (let i = 0; i <= 64; i++) { const a = -Math.PI / 2 + i / 64 * Math.PI * 2.1, k = 1 + (r() - 0.5) * 0.05; pts.push([c.x + Math.cos(a) * c.rx * k, c.y + Math.sin(a) * c.ry * k]); }
    ring = document.createElementNS(svgNS, "path");
    ring.setAttribute("d", pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" "));
    ring.setAttribute("fill", "none"); ring.setAttribute("stroke", PAL.red); ring.setAttribute("stroke-width", 8); ring.setAttribute("stroke-linecap", "round");
    svg.appendChild(ring);
    len = Math.PI * 2.1 * (c.rx + c.ry) / 2 * 1.03;
    ring.setAttribute("stroke-dasharray", len.toFixed(1));
  }
  vignette(root, 0.5, 45);
  const D = s.duration;
  return t => {
    const p = drift(cl(t / D, 0, 1));
    const z = lerp(1.0, 1.06, p);
    const [fx, fy] = s.focus || [0.5, 0.5];
    setT(board, (0.5 - fx) * W * (z - 1) + W / 2 * (1 - z) * 0, (0.5 - fy) * H * (z - 1), z);
    lines.forEach(({ d, ln }) => {
      const q = seg(t, ln.at || 0, ln.d || 0.9);
      css(d, "clipPath", `inset(-20% ${((1 - q) * 100).toFixed(1)}% -20% 0)`);
      vis(d, q > 0);
    });
    if (rule) css(rule, "width", (eOut(seg(t, s.ruleAt || 0, 0.5)) * (s.ruleW || 1100)).toFixed(0) + "px");
    if (ring) {
      const q = eInOut(seg(t, s.circle.at || 0, 0.6));
      ring.setAttribute("stroke-dashoffset", (len * (1 - q)).toFixed(1));
      ring.style.opacity = q > 0 ? 1 : 0;
    }
  };
};

SCENES.timeline = async (s, root) => {
  const L = darkPhoto(root, s, s.dim != null ? s.dim : 0.72);
  vignette(root, 0.55);
  const ev = s.events || [];
  const gap = s.gap || 520;
  const track = el("div", "abs", root, { left: 0, top: 0, width: (ev.length * gap + W) + "px", height: H + "px" });
  const line = el("div", "abs", track, { left: "0", top: "560px", height: "3px", width: (ev.length * gap + W) + "px", background: "rgba(240,232,214,.35)" });
  const nodes = ev.map((e, i) => {
    const x = W / 2 + i * gap;
    const dot = el("div", "abs", track, { left: x - 13 + "px", top: "548px", width: "26px", height: "26px", borderRadius: "50%", background: PAL.cream, boxShadow: "0 0 0 6px rgba(217,164,65,0)" });
    const yr = el("div", "abs", track, { left: x - 250 + "px", width: "500px", top: "380px", textAlign: "center", font: "140px 'Garamond'", color: "#F6F1E6" }, esc(e.year));
    const lb = el("div", "abs", track, { left: x - 240 + "px", width: "480px", top: "610px", textAlign: "center", font: "40px 'GaramondI'", color: "#E8E0CF", lineHeight: "1.2" }, esc(e.label));
    return { dot, yr, lb };
  });
  const D = s.duration;
  const stops = s.stops || ev.map((e, i) => ({ i, at: 0.2 + i * (D - 0.6) / Math.max(1, ev.length) }));
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    let pos = stops[0].i;
    for (let k = 1; k < stops.length; k++) {
      const a = eInOut(seg(t, stops[k].at - 0.35, 0.7));
      pos = lerp(pos, stops[k].i, a);
    }
    setT(track, -pos * gap, 0);
    nodes.forEach((n, i) => {
      const d = Math.abs(i - pos);
      const on = cl(1 - d, 0, 1);
      setO(n.yr, lerp(0.22, 1, on)); setO(n.lb, lerp(0.0, 1, on));
      setT(n.yr, 0, 0, lerp(0.7, 1, on));
      n.dot.style.background = on > 0.5 ? PAL.mustard : PAL.cream;
      n.dot.style.boxShadow = `0 0 0 ${(on * 10).toFixed(1)}px rgba(217,164,65,${(0.35 * on).toFixed(2)})`;
    });
    setO(track, eOut(seg(t, 0, 0.5)));
  };
};

SCENES.measure = async (s, root) => {
  paperGround(root, "paper");
  vignette(root, 0.4, 50);
  const scale = s.pxPerFt || 2.6, x0 = 230;
  const hdr = el("div", "abs", root, { left: x0 + "px", top: "90px", font: "76px 'Anton'", color: PAL.ink }, esc(s.title || ""));
  const rows = (s.bars || []).map((b, i) => {
    const y = 260 + i * (s.rowGap || 190);
    const lab = el("div", "abs", root, { left: x0 + "px", top: y + "px", font: "38px 'OswaldB'", letterSpacing: ".04em", color: "#2a2520", whiteSpace: "nowrap" }, esc(b.label));
    const bar = el("div", "abs", root, { left: x0 + "px", top: y + 58 + "px", height: "64px", width: "0", background: b.color || PAL.ink, boxShadow: "0 10px 20px rgba(0,0,0,.25)" });
    const val = el("div", "abs", root, { left: x0 + "px", top: y + 60 + "px", font: "54px 'Anton'", color: b.valColor || b.color || PAL.ink, whiteSpace: "nowrap" }, esc(b.value));
    return { b, lab, bar, val, y };
  });
  const stamp = s.stamp ? el("div", "abs", root, {
    left: (s.stamp.x || 1300) + "px", top: (s.stamp.y || 820) + "px", font: "92px 'Anton'", color: PAL.red, border: `8px solid ${PAL.red}`,
    padding: "2px 26px 0", transformOrigin: "50% 50%", webkitMaskImage: `url('${asset("grunge.png")}')`, webkitMaskSize: "600px 300px", opacity: 0,
  }, esc(s.stamp.text)) : null;
  return t => {
    rows.forEach(r => {
      const a = eOut(seg(t, r.b.at || 0, 0.4));
      setO(r.lab, a);
      const g = eInOut(seg(t, (r.b.at || 0) + 0.2, r.b.grow || 1.0));
      const w = r.b.ft * scale * g;
      css(r.bar, "width", w.toFixed(0) + "px");
      setT(r.val, w + 26, 0); setO(r.val, seg(t, (r.b.at || 0) + 0.2 + (r.b.grow || 1.0) * 0.7, 0.3));
    });
    if (stamp) {
      const p = eOut5(seg(t, s.stamp.at, 0.22));
      setO(stamp, p * 0.95);
      stamp.style.transform = `rotate(-8deg) scale(${lerp(2.2, 1, p).toFixed(3)})`;
    }
    setO(hdr, eOut(seg(t, 0, 0.5)));
  };
};

SCENES.checklist = async (s, root) => {
  const L = darkPhoto(root, s, s.dim != null ? s.dim : 0.74);
  vignette(root, 0.6);
  const hdr = el("div", "abs", root, { left: "200px", top: "150px", font: "34px 'BarlowB'", letterSpacing: ".3em", color: PAL.mustard }, esc(s.kicker || ""));
  const marks = { yes: ["✓", "#6FBF73"], maybe: ["?", PAL.mustard], no: ["✕", PAL.red], dot: ["•", PAL.cream] };
  const rows = (s.items || []).map((it, i) => {
    const y = (s.y0 || 240) + i * (s.gap || 118);
    const m = marks[it.mark || "yes"];
    const box = el("div", "abs", root, { left: "200px", top: y + "px", width: "76px", height: "76px", border: `4px solid ${m[1]}`, borderRadius: "8px", font: "58px 'InterB'", color: m[1], textAlign: "center", lineHeight: "72px" }, "");
    const tx = el("div", "abs", root, { left: "310px", top: y + 4 + "px", font: `${s.size || 60}px 'DMSerif'`, color: "#F4EFE4", whiteSpace: "nowrap" }, esc(it.text));
    return { it, box, tx, m };
  });
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(hdr, eOut(seg(t, 0.1, 0.5)));
    rows.forEach(r => {
      const a = eOut(seg(t, r.it.at, 0.45));
      setO(r.box, a); setO(r.tx, a); setT(r.tx, (1 - a) * 40, 0);
      const c = spring(t - r.it.at - 0.3, 2.6, 0.45);
      const g = r.box.textContent;
      if (t >= r.it.at + 0.3) { if (g !== r.m[0]) r.box.textContent = r.m[0]; }
      else if (g) r.box.textContent = "";
      r.box.style.transform = `scale(${t >= r.it.at + 0.3 ? (0.6 + 0.4 * c).toFixed(3) : 1})`;
      if (s.focus != null) setO(r.tx, a * (s.focus === rows.indexOf(r) ? 1 : 0.35));
    });
  };
};

/* geo - animated geology cross-sections on paper, drawn on canvas.

   variant "syncline": sediment settles into a basin layer by layer, sideways pressure
   folds it into a trough, and a plan view shows why a fold tilted at both ends
   ("doubly plunging") crops out as a boat-shaped lens that a landslide flows around.
   variant "slump": a limestone block slides down a slope on weak clay, then
   dissolution hollows cavities inside it (karst).
   Times for each beat come from the scene spec (s.beats), so they land on the words. */
SCENES.geo = async (s, root) => {
  paperGround(root, "paper");
  const cv = el("canvas", "full", root); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const labels = (s.labels || []).map(it => ITEMS.strip(root, Object.assign({ from: "fade" }, it)));
  vignette(root, 0.35, 55);
  const B = Object.assign({ deposit: 0.2, fold: 3.0, plan: 6.5, slide: 9.5, cav: 12 }, s.beats || {});
  const COLS = ["#B89A6A", "#8E7B5E", "#C9B58C", "#7D6A50", "#A8906A", "#D6C49C"];
  const ink = "#2a241c";

  function arrow(x0, y0, x1, y1, col, w, p) {
    if (p <= 0) return;
    const x = lerp(x0, x1, p), y = lerp(y0, y1, p);
    c.strokeStyle = col; c.fillStyle = col; c.lineWidth = w; c.lineCap = "round";
    c.beginPath(); c.moveTo(x0, y0); c.lineTo(x, y); c.stroke();
    const a = Math.atan2(y1 - y0, x1 - x0);
    c.beginPath(); c.moveTo(x + Math.cos(a) * 6, y + Math.sin(a) * 6);
    c.lineTo(x - Math.cos(a - 0.5) * 30, y - Math.sin(a - 0.5) * 30);
    c.lineTo(x - Math.cos(a + 0.5) * 30, y - Math.sin(a + 0.5) * 30); c.closePath(); c.fill();
  }

  function syncline(t) {
    const x0 = 260, x1 = 1660, xc = (x0 + x1) / 2, L = x1 - x0, th = 58, base = 840, n = 6;
    const fold = eInOut(seg(t, B.fold, 2.2)), F = 190 * fold, squeeze = 1 - 0.14 * fold;
    const planP = eInOut(seg(t, B.plan, 0.9));
    /* the section shrinks into the upper half when the plan view arrives */
    c.save();
    const ks = lerp(1, 0.55, planP);
    c.translate(lerp(0, -380, planP), lerp(0, -170, planP));
    c.translate(xc, 540); c.scale(ks, ks); c.translate(-xc, -540);
    for (let i = 0; i < n; i++) {
      const d = eOut(seg(t, B.deposit + i * 0.35, 0.5));
      if (d <= 0) continue;
      const y = u => { const q = (u - xc) / (L / 2); return F * (0.45 - q * q); };
      const bot = base - i * th, top = base - (i + d) * th;
      c.beginPath();
      for (let k = 0; k <= 80; k++) { const u = x0 + L * k / 80; const x = xc + (u - xc) * squeeze; c.lineTo(x, top + y(u)); }
      for (let k = 80; k >= 0; k--) { const u = x0 + L * k / 80; const x = xc + (u - xc) * squeeze; c.lineTo(x, bot + y(u)); }
      c.closePath(); c.fillStyle = COLS[i % COLS.length]; c.fill();
      c.lineWidth = 2; c.strokeStyle = "rgba(42,36,28,.55)"; c.stroke();
    }
    c.restore();
    /* sideways pressure */
    const ap = seg(t, B.fold - 0.4, 0.8) * (1 - seg(t, B.plan - 0.3, 0.4));
    if (ap > 0) {
      arrow(90, 640, 230, 640, PAL.red, 12, eOut(ap));
      arrow(1830, 640, 1690, 640, PAL.red, 12, eOut(ap));
    }
    /* plan view: a doubly plunging fold crops out as nested lenses - a boat outline */
    if (planP > 0) {
      const cx = 1330, cy = 760, rx = 400, ry = 140;
      c.save(); c.globalAlpha = planP;
      c.fillStyle = "rgba(243,238,226,.9)"; c.fillRect(cx - rx - 80, cy - ry - 100, 2 * rx + 160, 2 * ry + 200);
      c.strokeStyle = ink; c.lineWidth = 3; c.strokeRect(cx - rx - 80, cy - ry - 100, 2 * rx + 160, 2 * ry + 200);
      for (let i = n - 1; i >= 0; i--) {
        const k = (i + 1) / n, grow = eOut(seg(t, B.plan + 0.3 + (n - 1 - i) * 0.18, 0.5));
        c.beginPath();
        for (let a = 0; a <= 64; a++) {
          const th2 = a / 64 * Math.PI * 2, px = Math.cos(th2), py = Math.sin(th2);
          /* pointed at one end, rounded at the other */
          const sharp = px > 0 ? Math.pow(Math.abs(py), 0.8) * Math.sign(py) : py;
          c.lineTo(cx + px * rx * k * grow, cy + sharp * ry * k * grow);
        }
        c.closePath(); c.fillStyle = COLS[i % COLS.length]; c.fill(); c.lineWidth = 2; c.strokeStyle = "rgba(42,36,28,.6)"; c.stroke();
      }
      /* the landslide flowing around it */
      const lp = seg(t, B.slide, 1.4);
      if (lp > 0) {
        [[-1, 0], [1, 0]].forEach(([sgn], j) => {
          c.beginPath(); c.lineWidth = 10; c.strokeStyle = PAL.red; c.setLineDash([26, 16]);
          c.lineDashOffset = -t * 60;
          const pts = []; for (let a = 0; a <= 40 * eInOut(lp); a++) { const u = a / 40; pts.push([cx - rx - 60 + u * (2 * rx + 120), cy + sgn * (ry + 55) * Math.sin(Math.PI * (0.15 + 0.7 * u)) ]); }
          pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1]));
          c.stroke(); c.setLineDash([]);
        });
      }
      c.restore();
    }
  }

  function slump(t) {
    /* the slope, the weak clay along it, and the block that rides it down */
    const sx0 = 120, sy0 = 300, sx1 = 1800, sy1 = 940;
    const ang = Math.atan2(sy1 - sy0, sx1 - sx0);
    c.fillStyle = "#6E5A43";
    c.beginPath(); c.moveTo(sx0, sy0); c.lineTo(sx1, sy1); c.lineTo(sx1, H); c.lineTo(sx0 - 200, H); c.lineTo(sx0 - 200, sy0); c.closePath(); c.fill();
    const clayP = eOut(seg(t, B.deposit, 0.8));
    if (clayP > 0) {
      c.save(); c.globalAlpha = clayP; c.strokeStyle = "#9A9A96"; c.lineWidth = 34;
      c.beginPath(); c.moveTo(sx0, sy0 + 18); c.lineTo(sx0 + (sx1 - sx0) * clayP, sy0 + 18 + (sy1 - sy0) * clayP); c.stroke(); c.restore();
    }
    const sp = eInOut(seg(t, B.fold, 3.0));
    const dist = lerp(260, 980, sp);
    const bx = sx0 + Math.cos(ang) * dist, by = sy0 + Math.sin(ang) * dist;
    c.save(); c.translate(bx, by); c.rotate(ang + lerp(0, 0.06, sp));
    const bw = 520, bh = 250;
    c.fillStyle = "#D9CBA6"; c.fillRect(-bw / 2, -bh - 2, bw, bh);
    c.strokeStyle = "rgba(42,36,28,.5)"; c.lineWidth = 2;
    for (let i = 1; i < 6; i++) { c.beginPath(); c.moveTo(-bw / 2, -bh - 2 + i * bh / 6); c.lineTo(bw / 2, -bh - 2 + i * bh / 6); c.stroke(); }
    c.lineWidth = 4; c.strokeStyle = ink; c.strokeRect(-bw / 2, -bh - 2, bw, bh);
    /* karst: dissolution hollows open inside the block */
    const kp = seg(t, B.cav, 2.0);
    if (kp > 0) {
      const r = rng(11);
      for (let i = 0; i < 7; i++) {
        const cx = (r() - 0.5) * (bw - 120), cy = -bh / 2 - 2 + (r() - 0.5) * (bh - 90), rr = 18 + r() * 34;
        const g = eOut(seg(kp, i * 0.1, 0.4));
        c.beginPath(); c.ellipse(cx, cy, rr * 1.5 * g, rr * g, r() * 0.8, 0, Math.PI * 2);
        c.fillStyle = "#231d15"; c.fill();
      }
    }
    c.restore();
    if (sp > 0 && sp < 1) arrow(bx + 300, by - 40, bx + 300 + Math.cos(ang) * 160, by - 40 + Math.sin(ang) * 160, PAL.red, 12, 1);
  }

  return t => {
    c.clearRect(0, 0, W, H);
    if (s.variant === "slump") slump(t); else syncline(t);
    labels.forEach(u => u(t));
  };
};
