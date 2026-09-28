/* scenes_court.js - the expedition / courtroom scenes.

   scales      The scales of justice: a brass balance whose beam tips as evidence
               cards drop into either pan - the case for vs. the case against.
   scoreboard  A split-flap departures board: rows clatter through letters and settle
               on a tally ("1  FAILED DIG"), each row can take a stamp.
   verdict     Two-column verdict sheet (e.g. REALITY | MYTH - SO FAR): headers stamp
               in, items tick or cross off one by one, one side can be put in focus.
   (collage item) tag - a manila evidence tag on a string ("EXHIBIT A") that drops in
               and swings to rest.
*/
"use strict";

/* ---- evidence tag ------------------------------------------------------------ */
ITEMS.tag = (board, it) => {
  const w = it.w || 380;
  const wrap = el("div", "abs", board, { left: 0, top: 0, width: w + "px", transformOrigin: "34px 50%" });
  const body = el("div", "", wrap, {
    position: "relative", width: w + "px", boxSizing: "border-box", padding: "22px 26px 22px 78px",
    background: "linear-gradient(170deg, #E3C58C 0%, #D2AE6E 100%)", color: "#2A1E12",
    clipPath: "polygon(34px 0, 100% 0, 100% 100%, 34px 100%, 0 calc(100% - 34px), 0 34px)",
    boxShadow: "inset 0 0 40px rgba(120,80,30,.25)",
  });
  el("div", "", body, { font: `${it.size || 50}px 'Stamp'`, color: it.color || PAL.red, letterSpacing: ".04em", lineHeight: "1" }, esc(it.text));
  if (it.sub) {
    el("div", "", body, { height: "2px", background: "rgba(42,30,18,.45)", margin: "12px 0 10px" });
    el("div", "", body, { font: `${it.subSize || 26}px 'Elite'`, lineHeight: "1.2" }, esc(it.sub));
  }
  /* reinforced hole and the string */
  const ring = el("div", "abs", wrap, {
    left: "22px", top: "50%", width: "26px", height: "26px", marginTop: "-13px", borderRadius: "50%",
    background: "#2a2016", boxShadow: "0 0 0 7px #EBDDBE, 0 0 0 8px rgba(0,0,0,.2)",
  });
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  Object.assign(svg.style, { position: "absolute", left: "0", top: "0", width: "10px", height: "10px", overflow: "visible" });
  wrap.appendChild(svg);
  const str = document.createElementNS(svgNS, "path");
  str.setAttribute("fill", "none"); str.setAttribute("stroke", it.string || "#EFE6D2"); str.setAttribute("stroke-width", 3);
  svg.appendChild(str);
  wrap.style.filter = "drop-shadow(0 16px 18px rgba(0,0,0,.45))";
  const seed = (it.seed || 5) + Math.round((it.x || 0) + (it.y || 0));
  return t => {
    const e = entrance(it.from || "drop", t, it.at || 0, 0, seed);
    if (!e) { vis(wrap, false); return; }
    vis(wrap, true);
    const u = t - (it.at || 0) - 0.4;
    const swing = u > 0 ? 7 * Math.exp(-2.6 * u) * Math.sin(7.5 * u) : 0;
    const h = wrap.offsetHeight;
    const cy = h / 2;
    str.setAttribute("d", `M35 ${cy} C 10 ${cy - 60}, -40 ${cy - 90}, -70 ${cy - 170}`);
    setT(wrap, it.x - w / 2 + e[0], it.y - h / 2 + e[1], e[3], (it.rot || 0) + e[2] + swing);
    setO(wrap, e[4] * (it.out != null ? 1 - seg(t, it.out, 0.3) : 1));
  };
};

/* ---- the scales of justice ---------------------------------------------------- */
SCENES.scales = async (s, root) => {
  paperGround(root, s.bg || "cork");
  el("div", "full", root, { background: "radial-gradient(ellipse at 50% 40%, rgba(0,0,0,0) 0%, rgba(0,0,0,.45) 100%)" });
  const cv = el("canvas", "full", root); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const PX = W / 2, PY = s.pivotY || 250, L = s.half || 560, DROP = s.drop || 380, MAX = s.maxDeg || 11;
  const sides = [s.left || {}, s.right || {}];
  const cols = [sides[0].color || PAL.mustard, sides[1].color || PAL.cyan];
  const kick = s.title ? el("div", "abs", root, {
    left: 0, width: W + "px", top: "58px", textAlign: "center", font: "46px 'DMSerif'", letterSpacing: ".12em", color: PAL.cream,
    textShadow: "0 4px 18px rgba(0,0,0,.7)",
  }, esc(s.title)) : null;
  const heads = sides.map((sd, i) => el("div", "abs", root, {
    left: (i ? W / 2 + 40 : 0) + "px", width: (W / 2 - 40) + "px", top: "968px", textAlign: "center",
    font: "58px 'Anton'", letterSpacing: ".08em", color: cols[i], textShadow: "0 4px 18px rgba(0,0,0,.7)",
  }, esc(sd.title || "")));
  const cards = (s.items || []).map(it => {
    const d = el("div", "abs", root, {
      left: 0, top: 0, width: (s.cardW || 420) + "px", boxSizing: "border-box", padding: "12px 18px 10px",
      background: PAL.cream, color: PAL.ink, font: `${it.size || s.cardSize || 29}px 'Elite'`, lineHeight: "1.15",
      borderLeft: `9px solid ${cols[it.side]}`, boxShadow: "0 10px 20px rgba(0,0,0,.45)", transformOrigin: "50% 100%",
    }, esc(it.text));
    return { d, it };
  });
  /* the beam's target moves in steps (weights landing, or explicit tilts); each step is
     eased in by a damped spring so the beam overshoots and settles like real brass */
  const steps = [];
  if (s.tilts) {
    let prev = s.tilt0 || 0;
    s.tilts.forEach(k => { steps.push([k.at, k.v - prev]); prev = k.v; });
  } else {
    let wl = 0, wr = 0, prev = s.tilt0 || 0;
    [...(s.items || [])].sort((a, b) => a.at - b.at).forEach(it => {
      if (it.side) wr += it.w != null ? it.w : 1; else wl += it.w != null ? it.w : 1;
      const v = cl((wr - wl) / (s.norm || 3), -1, 1);
      steps.push([it.at + 0.45, v - prev]); prev = v;
    });
  }
  const brass = (x0, y0, x1, y1) => {
    const g = c.createLinearGradient(x0, y0, x1, y1);
    g.addColorStop(0, "#7A5A22"); g.addColorStop(0.35, "#E4C27A"); g.addColorStop(0.55, "#B98B3E"); g.addColorStop(1, "#5E4318");
    return g;
  };
  const D = s.duration;
  return t => {
    let tilt = s.tilt0 || 0;
    steps.forEach(([at, dv]) => { tilt += dv * spring(t - at, 1.1, 0.3); });
    const a = tilt * MAX * Math.PI / 180;
    const intro = eOut(seg(t, 0, 0.7));
    c.clearRect(0, 0, W, H);
    c.save();
    c.globalAlpha = intro;
    c.translate(0, (1 - intro) * 40);
    /* post and plinth */
    c.shadowColor = "rgba(0,0,0,.5)"; c.shadowBlur = 30; c.shadowOffsetY = 14;
    c.fillStyle = brass(PX - 16, 0, PX + 16, 0);
    c.fillRect(PX - 14, PY, 28, 690);
    c.fillStyle = brass(PX - 200, 0, PX + 200, 0);
    c.beginPath(); c.moveTo(PX - 70, PY + 660); c.lineTo(PX + 70, PY + 660); c.lineTo(PX + 190, PY + 720); c.lineTo(PX - 190, PY + 720); c.closePath(); c.fill();
    c.fillRect(PX - 210, PY + 718, 420, 22);
    c.shadowBlur = 0; c.shadowOffsetY = 0;
    /* hanging points */
    const ends = [-1, 1].map(k => [PX + k * L * Math.cos(a), PY + k * L * Math.sin(a)]);
    /* strings and pans */
    ends.forEach(([hx, hy], i) => {
      const py = hy + DROP;
      c.strokeStyle = "rgba(60,40,15,.9)"; c.lineWidth = 2.5;
      [-190, 0, 190].forEach(dx => { c.beginPath(); c.moveTo(hx, hy + 8); c.lineTo(hx + dx, py); c.stroke(); });
      c.fillStyle = brass(hx - 210, 0, hx + 210, 0);
      c.shadowColor = "rgba(0,0,0,.5)"; c.shadowBlur = 24; c.shadowOffsetY = 12;
      c.beginPath(); c.moveTo(hx - 215, py); c.quadraticCurveTo(hx, py + 110, hx + 215, py); c.closePath(); c.fill();
      c.shadowBlur = 0; c.shadowOffsetY = 0;
      c.fillStyle = "#F0D48E"; c.fillRect(hx - 215, py - 4, 430, 6);
      c.fillStyle = brass(hx - 12, 0, hx + 12, 0); c.beginPath(); c.arc(hx, hy + 6, 11, 0, Math.PI * 2); c.fill();
    });
    /* beam */
    c.save(); c.translate(PX, PY); c.rotate(a);
    c.shadowColor = "rgba(0,0,0,.5)"; c.shadowBlur = 20; c.shadowOffsetY = 10;
    c.fillStyle = brass(0, -12, 0, 12);
    c.beginPath(); c.moveTo(-L - 10, -6); c.lineTo(-40, -14); c.lineTo(40, -14); c.lineTo(L + 10, -6); c.lineTo(L + 10, 6); c.lineTo(40, 14); c.lineTo(-40, 14); c.lineTo(-L - 10, 6); c.closePath(); c.fill();
    c.restore();
    c.shadowBlur = 0; c.shadowOffsetY = 0;
    /* pivot finial and a pointer that reads the tilt */
    c.fillStyle = brass(PX - 30, 0, PX + 30, 0);
    c.beginPath(); c.arc(PX, PY, 28, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.moveTo(PX - 16, PY - 20); c.lineTo(PX, PY - 92); c.lineTo(PX + 16, PY - 20); c.closePath(); c.fill();
    c.fillStyle = "#3a2a12"; c.beginPath(); c.arc(PX, PY, 8, 0, Math.PI * 2); c.fill();
    c.restore();
    /* evidence cards ride in their pan, stacked from the bottom */
    const stack = [0, 0];
    cards.forEach(({ d, it }) => {
      const at = it.at || 0;
      if (t < at) { vis(d, false); return; }
      vis(d, true);
      const [hx, hy] = ends[it.side];
      const h = d.offsetHeight, cw = d.offsetWidth;
      const y = hy + DROP - 4 - stack[it.side] - h;
      stack[it.side] += h + 10;
      const p = eBack(seg(t, at, 0.5), 1.25);
      const rot = [-2.2, 1.6, -1.1, 2.4, -1.8][(stack[it.side] / 10 | 0) % 5];
      setT(d, hx - cw / 2, lerp(y - 520, y, p), 1, rot * p);
      setO(d, cl((t - at) * 6, 0, 1) * intro);
    });
    if (kick) setO(kick, eOut(seg(t, 0.2, 0.6)));
    heads.forEach((hd, i) => {
      const q = eOut(seg(t, (s.headAt ? s.headAt[i] : 0.3 + i * 0.2), 0.5));
      setO(hd, q); setT(hd, 0, (1 - q) * 24);
    });
  };
};

/* ---- split-flap scoreboard ----------------------------------------------------- */
SCENES.scoreboard = async (s, root) => {
  paperGround(root, s.bg || "cork");
  vignette(root, 0.55);
  const rows = s.rows || [];
  const cols = s.cols || Math.max(...rows.map(r => (r.text || "").length), 8);
  const nw = s.nw || 2;
  const CW = s.cell || 52, CH = Math.round(CW * 1.5), G = 6;
  const bw = (nw + cols) * (CW + G) + 60 + 80, bh = rows.length * (CH + 40) + 190;
  const bx = (W - bw) / 2, by = (H - bh) / 2 + 20;
  const board = el("div", "abs", root, {
    left: bx + "px", top: by + "px", width: bw + "px", height: bh + "px", background: "linear-gradient(180deg,#1f1b16,#15120f)",
    borderRadius: "16px", boxShadow: "0 0 0 10px #6B4F22, 0 0 0 13px #C8963E, 0 50px 90px rgba(0,0,0,.6)",
  });
  el("div", "abs", board, {
    left: 0, width: bw + "px", top: "34px", textAlign: "center", font: "42px 'DMSerif'", letterSpacing: ".16em", color: PAL.mustard,
  }, esc(s.title || ""));
  const CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  const mk = (x, y) => {
    const cell = el("div", "abs", board, {
      left: x + "px", top: y + "px", width: CW + "px", height: CH + "px", background: "linear-gradient(180deg,#2c2823 0%,#2c2823 49%,#221f1b 51%,#221f1b 100%)",
      borderRadius: "5px", overflow: "hidden", boxShadow: "inset 0 2px 3px rgba(255,255,255,.06), 0 3px 6px rgba(0,0,0,.5)",
    });
    const ch = el("div", "abs", cell, { left: 0, top: 0, width: CW + "px", height: CH + "px", textAlign: "center", font: `${Math.round(CH * 0.8)}px 'Anton'`, lineHeight: CH + "px", color: "#F1E6CF" }, "");
    const flap = el("div", "abs", cell, { left: 0, top: 0, width: CW + "px", height: CH / 2 + "px", background: "#35302a", transformOrigin: "50% 100%", opacity: 0 });
    el("div", "abs", cell, { left: 0, top: CH / 2 - 1 + "px", width: CW + "px", height: "2px", background: "#0c0a08" });
    return { cell, ch, flap };
  };
  const R = rows.map((r, i) => {
    const y = 120 + i * (CH + 40);
    const val = String(r.n != null ? r.n : "").padStart(nw, " ").slice(-nw);
    const txt = String(r.text || "").toUpperCase().padEnd(cols, " ").slice(0, cols);
    const cells = [];
    for (let j = 0; j < nw; j++) cells.push(Object.assign(mk(40 + j * (CW + G), y), { fin: val[j], col: r.color || PAL.mustard }));
    for (let j = 0; j < cols; j++) cells.push(Object.assign(mk(40 + (nw + j) * (CW + G) + 40, y), { fin: txt[j], col: "#F1E6CF" }));
    const rr = rng(97 + i * 13);
    cells.forEach((cc, j) => { cc.start = (r.at || 0) + j * 0.03; cc.settle = cc.start + 0.3 + rr() * 0.35; cc.seed = Math.floor(rr() * 1000); });
    const st = r.stamp ? ITEMS.stamp(root, Object.assign({ x: bx + bw - 190, y: by + y + CH / 2, rot: -7, size: 52 }, r.stamp)) : null;
    return { r, cells, st };
  });
  const D = s.duration;
  return t => {
    const z = lerp(1.0, 1.04, drift(cl(t / D, 0, 1)));
    setT(board, 0, 0, z);
    board.style.transformOrigin = "50% 50%";
    setO(board, eOut(seg(t, 0, 0.5)));
    R.forEach(({ cells, st }) => {
      cells.forEach(cc => {
        let g = " ", flapO = 0, flapS = 1;
        if (cc.fin !== " " && t >= cc.start) {
          if (t >= cc.settle) g = cc.fin;
          else {
            const k = Math.floor((t - cc.start) * 22);
            g = CHARS[(cc.seed + k * 7) % CHARS.length];
            const ph = ((t - cc.start) * 22) % 1;
            flapO = 1; flapS = 1 - ph;
          }
        }
        if (cc.ch._g !== g) { cc.ch.textContent = g; cc.ch._g = g; }
        css(cc.ch, "color", t >= cc.settle ? cc.col : "#F1E6CF");
        setO(cc.flap, flapO); css(cc.flap, "transform", `scaleY(${flapS.toFixed(2)})`);
      });
      if (st) st(t);
    });
  };
};

/* ---- the verdict sheet ------------------------------------------------------------ */
SCENES.verdict = async (s, root) => {
  const board = el("div", "full", root, { transformOrigin: "50% 50%" });
  paperGround(board, s.bg || "paper");
  const sides = [s.left || { title: "REALITY" }, s.right || { title: "MYTH" }];
  const cols = [sides[0].color || PAL.green, sides[1].color || PAL.red];
  const X = [560, 1400], CW = 760;
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  Object.assign(svg.style, { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px", overflow: "visible" });
  const heads = sides.map((sd, i) => {
    const h = el("div", "abs", board, {
      left: X[i] - CW / 2 + "px", width: CW + "px", top: "70px", textAlign: "center", font: `${s.hsize || 110}px 'Stamp'`, lineHeight: "1", color: cols[i],
      letterSpacing: ".04em", webkitMaskImage: `url('${asset("grunge.png")}')`, webkitMaskSize: "600px 300px", transformOrigin: "50% 50%",
    }, esc(sd.title));
    const sub = sd.sub ? el("div", "abs", board, {
      left: X[i] - CW / 2 + "px", width: CW + "px", top: 70 + (s.hsize || 110) + 22 + "px", textAlign: "center", font: "30px 'Elite'", color: PAL.ink,
    }, esc(sd.sub)) : null;
    return { h, sub };
  });
  const div = el("div", "abs", board, { left: W / 2 - 2 + "px", top: "80px", width: "4px", height: "0", background: PAL.ink, opacity: 0.7 });
  board.appendChild(svg);
  const y0 = [0, 0];
  const items = (s.items || []).map(it => {
    const x = X[it.side] - CW / 2 + 30;
    const y = (s.y0 || 300) + y0[it.side];
    y0[it.side] += s.gap || 128;
    const tx = el("div", "abs", board, {
      left: x + 90 + "px", top: y + "px", width: CW - 140 + "px", font: `${it.size || s.size || 40}px '${s.font || "Elite"}'`, color: PAL.ink, lineHeight: "1.15",
    }, esc(it.text));
    const mark = it.mark || (it.side ? "no" : "yes");
    const path = document.createElementNS(svgNS, "path");
    const mx = x + 30, my = y + 26;
    path.setAttribute("d", mark === "yes" ? `M${mx - 24} ${my} L${mx - 6} ${my + 20} L${mx + 28} ${my - 24}` :
      mark === "no" ? `M${mx - 22} ${my - 22} L${mx + 22} ${my + 22} M${mx + 22} ${my - 22} L${mx - 22} ${my + 22}` :
        `M${mx - 24} ${my} L${mx + 24} ${my}`);
    path.setAttribute("fill", "none"); path.setAttribute("stroke", mark === "yes" ? cols[0] : mark === "no" ? cols[1] : PAL.mustard);
    path.setAttribute("stroke-width", 10); path.setAttribute("stroke-linecap", "round"); path.setAttribute("stroke-linejoin", "round");
    path.setAttribute("stroke-dasharray", "130"); svg.appendChild(path);
    return { it, tx, path };
  });
  const st = s.stamp ? ITEMS.stamp(board, Object.assign({ x: W / 2, y: 960, rot: -5, size: 80 }, s.stamp)) : null;
  vignette(root, 0.4, 50);
  const D = s.duration;
  return t => {
    const z = lerp(1.0, 1.04, drift(cl(t / D, 0, 1)));
    setT(board, W / 2 * (1 - z), H / 2 * (1 - z), z);
    const f = s.focus != null ? eInOut(seg(t, s.focusAt || 0, 0.6)) : 0;
    const dimOf = side => s.focus != null && side !== s.focus ? lerp(1, 0.28, f) : 1;
    heads.forEach((o, i) => {
      const at = s.headAt ? s.headAt[i] : 0.1 + i * 0.35;
      const p = eOut5(seg(t, at, 0.22));
      setO(o.h, p * dimOf(i)); o.h.style.transform = `rotate(${i ? 3 : -3}deg) scale(${lerp(2.0, 1, p).toFixed(3)})`;
      if (o.sub) setO(o.sub, eOut(seg(t, at + 0.35, 0.5)) * dimOf(i));
    });
    css(div, "height", (eInOut(seg(t, 0.2, 0.9)) * 900).toFixed(0) + "px");
    items.forEach(({ it, tx, path }) => {
      const at = it.at || 0;
      const a = eOut(seg(t, at, 0.45));
      setO(tx, a * dimOf(it.side)); setT(tx, (1 - a) * 30, 0);
      const q = eInOut(seg(t, at + 0.25, 0.35));
      path.setAttribute("stroke-dashoffset", (130 * (1 - q)).toFixed(1));
      path.style.opacity = (q > 0 ? 1 : 0) * dimOf(it.side);
    });
    if (st) st(t);
  };
};
