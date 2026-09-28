/* scenes_lab.js - the forensic / lab-report scenes.

   filter   The confirmation filter: three columns - observed, claimed, confirmed -
            and evidence cards that drop into them. The confirmed column can stay
            empty and say so.
   gauge    A ring gauge that fills to a value and can drain to a second one
            (100% certainty -> 0% confirmed).
   network  One source, many echoes: a centre node and the outlets repeating it.
   valley   Cross-section of a deep valley with the formation at the bottom and a
            flood line that rises above the peaks.
   cells    Petrification: wood cells replaced by mineral one by one.
   (collage item) scan - a scanning line sweeping a region, for x-ray shots.
*/
"use strict";

SCENES.filter = async (s, root) => {
  paperGround(root, s.bg || "cork");
  const heads = s.heads || ["OBSERVED", "CLAIMED", "CONFIRMED"];
  const cols = [PAL.cyan, PAL.mustard, PAL.green];
  const X = [360, 960, 1560], CW = 520;
  const colEls = heads.map((h, i) => {
    const box = el("div", "abs", root, {
      left: X[i] - CW / 2 + "px", top: "190px", width: CW + "px", height: "820px",
      border: `3px dashed ${cols[i]}55`, borderRadius: "14px", background: "rgba(255,255,255,.03)",
    });
    const hd = el("div", "abs", root, {
      left: X[i] - CW / 2 + "px", top: "96px", width: CW + "px", textAlign: "center",
      font: "58px 'Anton'", letterSpacing: ".08em", color: cols[i],
    }, esc(h));
    const bar = el("div", "abs", root, { left: X[i] - CW / 2 + "px", top: "172px", height: "5px", width: "0", background: cols[i] });
    return { box, hd, bar };
  });
  const stacks = [0, 0, 0];
  const cards = (s.items || []).map((it, k) => {
    const c = el("div", "abs", root, {
      left: 0, top: 0, width: CW - 60 + "px", background: PAL.cream, color: PAL.ink, padding: "18px 22px",
      font: `${it.size || 34}px 'Elite'`, lineHeight: "1.2", borderLeft: `10px solid ${cols[it.col]}`,
      boxShadow: "0 14px 30px rgba(0,0,0,.45)", boxSizing: "border-box", transformOrigin: "50% 50%",
    }, esc(it.text));
    const slot = stacks[it.col]++;
    return { c, it, slot, rot: [-2, 1.5, -1, 2][k % 4] };
  });
  let zero = null;
  if (s.zeroAt != null) {
    zero = el("div", "abs", root, { left: X[2] - 200 + "px", top: "420px", width: "400px", textAlign: "center" });
    el("div", "", zero, { font: "260px 'Garamond'", color: cols[2], lineHeight: "1" }, "0");
    el("div", "", zero, { font: "34px 'Elite'", color: PAL.cream, marginTop: "10px" }, esc(s.zeroText || "nothing confirmed yet"));
  }
  vignette(root, 0.5);
  const D = s.duration;
  return t => {
    colEls.forEach((o, i) => {
      const h0 = s.headAt ? s.headAt[i] : 0.05 + i * 0.12;
      const a = eOut(seg(t, h0, 0.5));
      setO(o.box, a); setO(o.hd, a);
      if (s.headAt) setT(o.hd, 0, (1 - a) * 30, lerp(1.25, 1, a));
      css(o.bar, "width", (eOut(seg(t, h0 + 0.2, 0.5)) * CW).toFixed(0) + "px");
      if (s.focus != null) {
        const f = eInOut(seg(t, s.focusAt || 0, 0.5));
        const k = i === s.focus ? 1 : lerp(1, 0.3, f);
        setO(o.hd, a * k); setO(o.box, a * k);
      }
    });
    let y0 = [230, 230, 230];
    cards.forEach(({ c, it, slot, rot }) => {
      const at = it.at || 0;
      if (t < at) { vis(c, false); return; }
      vis(c, true);
      const p = eBack(seg(t, at, 0.55), 1.2);
      const h = c.offsetHeight;
      const x = X[it.col] - (CW - 60) / 2;
      const y = y0[it.col];
      y0[it.col] += h + 24;
      setT(c, x, lerp(-260, y, p), 1, rot * p);
      setO(c, cl((t - at) * 6, 0, 1) * (s.focus != null && it.col !== s.focus ? lerp(1, 0.3, eInOut(seg(t, s.focusAt || 0, 0.5))) : 1));
    });
    if (zero) {
      const z = spring(t - s.zeroAt, 2.2, 0.45);
      setO(zero, cl((t - s.zeroAt) * 4, 0, 1)); setT(zero, 0, 0, t >= s.zeroAt ? 0.6 + 0.4 * z : 0.6);
    }
  };
};

SCENES.gauge = async (s, root) => {
  const L = s.img ? darkPhoto(root, s, s.dim != null ? s.dim : 0.8) : (paperGround(root, "cork"), null);
  vignette(root, 0.6);
  const cv = el("canvas", "full", root); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const cx = s.x || W / 2, cy = 520, R = 300;
  const kick = el("div", "abs", root, { left: 0, width: W + "px", top: "120px", textAlign: "center", font: "34px 'BarlowB'", letterSpacing: ".3em", color: PAL.mustard }, esc(s.kicker || ""));
  const num = el("div", "abs", root, { left: cx - 300 + "px", width: "600px", top: cy - 110 + "px", textAlign: "center", font: "200px 'Garamond'", lineHeight: "1", color: "#F6F4EE" }, "");
  const lab = el("div", "abs", root, { left: cx - 400 + "px", width: "800px", top: cy + 110 + "px", textAlign: "center", font: "40px 'Elite'", color: "#DDE3E3" }, esc(s.label || ""));
  const lab2 = s.label2 ? el("div", "abs", root, { left: cx - 400 + "px", width: "800px", top: cy + 110 + "px", textAlign: "center", font: "40px 'Elite'", color: PAL.red }, esc(s.label2)) : null;
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    let v = lerp(s.from || 0, s.to, eInOut(seg(t, s.at || 0.3, s.d || 1.4)));
    let col = s.color || PAL.mustard;
    if (s.to2 != null) {
      const q = eInOut(seg(t, s.at2, s.d2 || 1.2));
      v = lerp(v, s.to2, q);
      if (q > 0.5) col = s.color2 || PAL.red;
      if (lab2) { setO(lab, 1 - q); setO(lab2, q); }
    }
    c.clearRect(0, 0, W, H);
    c.lineCap = "round";
    c.lineWidth = 34; c.strokeStyle = "rgba(255,255,255,.10)";
    c.beginPath(); c.arc(cx, cy, R, Math.PI * 0.75, Math.PI * 2.25); c.stroke();
    for (let i = 0; i <= 20; i++) {
      const a = Math.PI * 0.75 + i / 20 * Math.PI * 1.5;
      c.lineWidth = i % 5 ? 2 : 4; c.strokeStyle = "rgba(255,255,255,.35)";
      c.beginPath(); c.moveTo(cx + Math.cos(a) * (R + 30), cy + Math.sin(a) * (R + 30));
      c.lineTo(cx + Math.cos(a) * (R + (i % 5 ? 44 : 56)), cy + Math.sin(a) * (R + (i % 5 ? 44 : 56))); c.stroke();
    }
    if (v > 0.2) {
      c.lineWidth = 34; c.strokeStyle = col; c.shadowColor = col; c.shadowBlur = 30;
      c.beginPath(); c.arc(cx, cy, R, Math.PI * 0.75, Math.PI * 0.75 + Math.PI * 1.5 * v / 100); c.stroke();
      c.shadowBlur = 0;
    }
    const txt = Math.round(v) + "%";
    if (num._s !== txt) { num.textContent = txt; num._s = txt; }
    setO(kick, eOut(seg(t, 0.1, 0.5)));
    if (!lab2) setO(lab, eOut(seg(t, (s.at || 0.3) + 0.6, 0.5)));
    else if (s.to2 == null || t < s.at2) setO(lab, eOut(seg(t, (s.at || 0.3) + 0.6, 0.5)));
  };
};

SCENES.network = async (s, root) => {
  paperGround(root, "cork");
  vignette(root, 0.55);
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  Object.assign(svg.style, { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px" });
  root.appendChild(svg);
  const cx = W / 2, cy = H / 2 - 20;
  const nodes = (s.nodes || []).map((n, i, arr) => {
    const a = -Math.PI / 2 + (i / arr.length) * Math.PI * 2 + (s.rot || 0.3);
    const rx = n.r || 600, ry = (n.r || 600) * 0.56;
    const x = cx + Math.cos(a) * rx, y = cy + Math.sin(a) * ry;
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", cx); line.setAttribute("y1", cy); line.setAttribute("x2", cx); line.setAttribute("y2", cy);
    line.setAttribute("stroke", n.dashed ? "rgba(255,255,255,.35)" : PAL.cyan); line.setAttribute("stroke-width", 3);
    if (n.dashed) line.setAttribute("stroke-dasharray", "12 10");
    svg.appendChild(line);
    const dot = document.createElementNS(svgNS, "circle");
    dot.setAttribute("r", 7); dot.setAttribute("fill", PAL.cyan); svg.appendChild(dot);
    const box = el("div", "abs", root, {
      left: 0, top: 0, padding: "14px 24px", background: n.dashed ? "transparent" : PAL.cream, color: n.dashed ? "#DDE3E3" : PAL.ink,
      border: n.dashed ? "3px dashed rgba(255,255,255,.5)" : "none", font: "30px 'Elite'", whiteSpace: "nowrap",
      boxShadow: n.dashed ? "none" : "0 12px 26px rgba(0,0,0,.45)",
    }, esc(n.label));
    return { n, x, y, line, dot, box };
  });
  const hub = el("div", "abs", root, {
    left: 0, top: 0, padding: "26px 40px", background: PAL.mustard, color: PAL.ink, font: "54px 'Anton'",
    letterSpacing: ".04em", whiteSpace: "nowrap", boxShadow: "0 0 0 10px rgba(242,177,52,.18), 0 20px 50px rgba(0,0,0,.55)",
  }, esc(s.center || ""));
  const st = s.stamp ? ITEMS.stamp(root, Object.assign({ x: W / 2, y: 1010, rot: -4, size: 70 }, s.stamp)) : null;
  return t => {
    const hp = spring(t - 0.1, 2.0, 0.5);
    setT(hub, cx - hub.offsetWidth / 2, cy - hub.offsetHeight / 2, 0.6 + 0.4 * hp);
    setO(hub, cl(t * 5, 0, 1));
    nodes.forEach(o => {
      const at = o.n.at || 0;
      const p = eOut(seg(t, at, 0.6));
      o.line.setAttribute("x2", lerp(cx, o.x, p)); o.line.setAttribute("y2", lerp(cy, o.y, p));
      o.line.style.opacity = p > 0 ? 1 : 0;
      /* a pulse runs from the source out to the echo, again and again */
      const u = ((t - at) * 0.7) % 1;
      o.dot.setAttribute("cx", lerp(cx, o.x, u)); o.dot.setAttribute("cy", lerp(cy, o.y, u));
      o.dot.style.opacity = (t > at + 0.6 && !o.n.dashed) ? 1 : 0;
      const b = eBack(seg(t, at + 0.4, 0.5), 1.3);
      vis(o.box, t >= at + 0.4);
      setT(o.box, o.x - o.box.offsetWidth / 2, o.y - o.box.offsetHeight / 2, 0.5 + 0.5 * b);
    });
    if (st) st(t);
  };
};

SCENES.valley = async (s, root) => {
  paperGround(root, "paper");
  const cv = el("canvas", "full", root); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const labels = (s.labels || []).map(it => ITEMS.strip(root, Object.assign({ from: "fade" }, it)));
  vignette(root, 0.3, 55);
  const B = Object.assign({ draw: 0.1, measure: 1.5, water: 3.0, boat: 1.0 }, s.beats || {});
  /* terrain profile: Ararat on the left, the valley, ridges on the right */
  const P = [[0, 900], [120, 760], [330, 300], [420, 180], [520, 290], [700, 560], [820, 700], [900, 810],
             [960, 860], [1020, 812], [1120, 690], [1280, 540], [1420, 470], [1560, 520], [1700, 430], [1920, 520]];
  function yAt(x) {
    for (let i = 1; i < P.length; i++) if (x <= P[i][0]) {
      const [x0, y0] = P[i - 1], [x1, y1] = P[i]; return lerp(y0, y1, (x - x0) / (x1 - x0));
    }
    return P[P.length - 1][1];
  }
  return t => {
    c.clearRect(0, 0, W, H);
    const d = eInOut(seg(t, B.draw, 1.2));
    const xEnd = W * d;
    c.beginPath(); c.moveTo(0, H);
    for (let x = 0; x <= xEnd; x += 8) c.lineTo(x, yAt(x));
    c.lineTo(xEnd, H); c.closePath();
    const g = c.createLinearGradient(0, 150, 0, H);
    g.addColorStop(0, "#9AA3A6"); g.addColorStop(1, "#4E585C");
    c.fillStyle = g; c.fill();
    c.lineWidth = 4; c.strokeStyle = PAL.ink;
    c.beginPath(); for (let x = 0; x <= xEnd; x += 8) (x ? c.lineTo(x, yAt(x)) : c.moveTo(x, yAt(x))); c.stroke();
    /* snow cap on the big peak */
    if (d > 0.3) { c.fillStyle = "#F4F6F6"; c.beginPath(); c.moveTo(365, 240); c.lineTo(420, 180); c.lineTo(478, 250); c.lineTo(440, 236); c.lineTo(405, 252); c.closePath(); c.fill(); }
    /* the flood line rising above every peak */
    const w = eInOut(seg(t, B.water, 2.6));
    if (w > 0) {
      const wy = lerp(900, 140, w);
      c.save(); c.globalAlpha = 0.55; c.fillStyle = "#3C7FA8";
      c.fillRect(0, wy, W, H - wy); c.restore();
      c.lineWidth = 4; c.strokeStyle = "#2B6A91"; c.setLineDash([18, 10]);
      c.beginPath(); c.moveTo(0, wy); c.lineTo(W, wy); c.stroke(); c.setLineDash([]);
    }
    /* the formation at the valley floor */
    const bp = eOut(seg(t, B.boat, 0.6));
    if (bp > 0) {
      c.save(); c.translate(960, 850); c.scale(bp, bp);
      c.fillStyle = PAL.mustard; c.strokeStyle = PAL.ink; c.lineWidth = 3;
      c.beginPath(); c.moveTo(-70, 0); c.quadraticCurveTo(0, -26, 80, -4); c.quadraticCurveTo(10, 14, -70, 0); c.closePath(); c.fill(); c.stroke();
      c.restore();
    }
    /* the depth of the valley, measured */
    const m = eOut(seg(t, B.measure, 0.8));
    if (m > 0) {
      const x = 1180, top = 540, bot = 860;
      c.strokeStyle = PAL.red; c.fillStyle = PAL.red; c.lineWidth = 6;
      c.beginPath(); c.moveTo(x, top); c.lineTo(x, lerp(top, bot, m)); c.stroke();
      c.beginPath(); c.moveTo(x - 18, top); c.lineTo(x + 18, top); c.stroke();
      if (m >= 1) { c.beginPath(); c.moveTo(x - 18, bot); c.lineTo(x + 18, bot); c.stroke(); }
    }
    labels.forEach(u => u(t));
  };
};

SCENES.cells = async (s, root) => {
  paperGround(root, "cork");
  const cv = el("canvas", "full", root); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const labels = (s.labels || []).map(it => ITEMS.strip(root, Object.assign({ from: "fade" }, it)));
  vignette(root, 0.55);
  const r = rng(21), cells = [];
  const x0 = 360, y0 = 200, cw = 60, ch = 44, cols = 20, rows = 14;
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const ring = (j % 7 === 0) ? 0.55 : 1;            /* growth rings: rows of smaller cells */
    cells.push({ x: x0 + i * cw + (j % 2) * 8, y: y0 + j * ch, w: (cw - 8) * (0.8 + r() * 0.2), h: (ch - 8) * ring, k: r() });
  }
  const B = Object.assign({ show: 0.1, replace: 1.5, dur: 3.0 }, s.beats || {});
  return t => {
    c.clearRect(0, 0, W, H);
    const a = eOut(seg(t, B.show, 0.8));
    cells.forEach(o => {
      const q = cl((t - B.replace - o.k * B.dur) / 0.35, 0, 1);
      const wood = [150, 104, 62], stone = [120, 168, 176];
      const col = wood.map((v, i) => Math.round(lerp(v, stone[i], q)));
      c.globalAlpha = a;
      c.fillStyle = `rgb(${col[0]},${col[1]},${col[2]})`;
      c.strokeStyle = q > 0.5 ? "#DDF3F5" : "#E8C9A0"; c.lineWidth = 3;
      c.beginPath(); c.roundRect(o.x, o.y, o.w, o.h, 8); c.fill(); c.stroke();
    });
    c.globalAlpha = 1;
    labels.forEach(u => u(t));
  };
};

/* a scanning line sweeping a region - for x-ray and radar shots in collages */
ITEMS.scan = (board, it) => {
  const line = el("div", "abs", board, {
    left: it.x + "px", top: it.y + "px", width: it.w + "px", height: "4px", background: PAL.cyan,
    boxShadow: `0 0 24px 8px ${PAL.cyan}88`, opacity: 0,
  });
  return t => {
    if (t < (it.at || 0)) { setO(line, 0); return; }
    const u = (((t - (it.at || 0)) / (it.period || 2.2)) % 1);
    setT(line, 0, u * it.h);
    setO(line, 0.9 * Math.sin(Math.PI * u));
  };
};
