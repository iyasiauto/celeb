/* scenes_news.js - the broadcast / breaking-news scenes.

   breaking   The opener: a red BREAKING NEWS slab slams in with a glitch, the headline
              bar wipes across, a sub strip follows - over a dimmed photograph.
   borehole   A cross-section of the ground under a drill rig: layers, a water-filled
              cavity, a hard layer. The drill string descends with a depth readout; on the
              hit the panel shakes, the bit shatters into fragments and cracks spread.
   factcheck  A claim card beside a rating meter (CONFIRMED / UNVERIFIED / DISPUTED /
              FALSE); the needle swings and settles, the rating stamps.
   echo       A wall of headlines appears one by one, then collapses into the one source
              they all came from: "10 headlines = 1 source".
   columns    Two data panels - OBSERVED and CLAIMED - filled row by row; then the gap
              between them lights up: arrows reach across and stop short.
   videowall  A 3x3 wall of monitors; the camera pushes into one screen until it fills
              the frame.
   newslist   Numbered broadcast rows, each with a status pill (UNANSWERED, PLANNED...).
   segment    The segment bumper (the broadcast chapter card): red and navy bars sweep
              across, a number box and the segment title land, the bars clear.

   Overlays (any scene, and clips - rendered as an animated alpha layer):
   ticker     The crawl along the bottom. Its position is driven by the scene's global
              start time, so it runs on without a jump across cuts.
   bug        The LIVE bug top-right, with a pulsing dot and a place line.
   newslower  A broadcast lower third: kicker tab, white headline bar, navy sub strip.
*/
"use strict";

const NEWS = {
  red: () => PAL.red, yellow: () => PAL.mustard, navy: () => PAL.navy || "#0A1730", white: "#F4F6FA",
};

/* a thin diagonal light sweep across a bar, from time a over d seconds */
function sweep(parent, h) {
  return el("div", "abs", parent, {
    left: "0", top: "0", width: "180px", height: h + "px", opacity: 0,
    background: "linear-gradient(100deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.55) 50%, rgba(255,255,255,0) 100%)",
  });
}

/* ---- overlays ------------------------------------------------------------------ */
OVERLAYS.ticker = (o, root) => {
  const H0 = 64, y = o.y != null ? o.y : 1016;
  const bar = el("div", "abs", root, { left: 0, top: y + "px", width: W + "px", height: H0 + "px", overflow: "hidden" });
  el("div", "abs", bar, { left: 0, top: 0, width: W + "px", height: H0 + "px", background: "rgba(8,14,32,.94)", borderTop: `3px solid ${PAL.red}` });
  const lab = el("div", "abs", bar, {
    left: 0, top: 0, height: H0 + "px", padding: "0 30px", background: PAL.red, color: "#fff", font: "30px 'Anton'",
    lineHeight: H0 + 3 + "px", letterSpacing: ".04em", whiteSpace: "nowrap", zIndex: 2,
  }, esc(o.label || "BREAKING"));
  const lane = el("div", "abs", bar, { left: 0, top: 0, height: H0 + "px", whiteSpace: "nowrap", font: "32px 'Barlow'",
    lineHeight: H0 + 3 + "px", color: "#F4F6FA", letterSpacing: ".02em", textTransform: "uppercase" });
  const items = (o.items || [o.text || ""]).map(x => `<span>${esc(x)}</span><span style="color:${PAL.mustard};padding:0 34px">■</span>`).join("");
  const one = el("span", "", lane, {}, items);
  el("span", "", lane, {}, items); el("span", "", lane, {}, items);
  const clock = o.clock ? el("div", "abs", bar, {
    right: 0, top: 0, height: H0 + "px", padding: "0 26px", background: "#0B1220", color: PAL.mustard, font: "28px 'OswaldB'",
    lineHeight: H0 + 3 + "px", zIndex: 2, borderLeft: "2px solid rgba(255,255,255,.15)",
  }, esc(o.clock)) : null;
  const speed = o.speed || 150;
  return t => {
    const w = one.offsetWidth || 2000, lw = lab.offsetWidth;
    const g = (window.SCENE.t0 || 0) + t;
    setT(lane, lw + 24 - ((g * speed) % w), 0);
    if (o.intro != null) { const a = eOut(seg(t, o.intro, 0.45)); setT(bar, 0, (1 - a) * 90); }
    if (o.out != null) setO(bar, 1 - seg(t, o.out, 0.3));
  };
};

OVERLAYS.bug = (o, root) => {
  const box = el("div", "abs", root, { right: "64px", top: "52px", display: "flex", alignItems: "stretch", height: "48px" });
  const live = el("div", "", box, { background: PAL.red, color: "#fff", font: "28px 'Anton'", padding: "0 18px 0 44px",
    lineHeight: "50px", position: "relative", letterSpacing: ".06em" }, esc(o.text || "LIVE"));
  const dot = el("div", "abs", live, { left: "18px", top: "17px", width: "14px", height: "14px", borderRadius: "50%", background: "#fff" });
  const place = el("div", "", box, { background: "rgba(8,14,32,.88)", color: "#F4F6FA", font: "24px 'Barlow'", padding: "0 18px",
    lineHeight: "50px", letterSpacing: ".12em", textTransform: "uppercase", whiteSpace: "nowrap" }, esc(o.place || ""));
  if (!o.place) place.style.display = "none";
  return t => {
    const g = (window.SCENE.t0 || 0) + t;
    setO(dot, 0.35 + 0.65 * (0.5 + 0.5 * Math.cos(g * Math.PI * 1.6)));
    if (o.intro != null) { const a = eOut(seg(t, o.intro, 0.4)); setO(box, a); setT(box, (1 - a) * 40, 0); }
    if (o.out != null) setO(box, 1 - seg(t, o.out, 0.3));
  };
};

OVERLAYS.newslower = (o, root) => {
  const x = o.x != null ? o.x : 110, y = o.y != null ? o.y : 810;
  const wrap = el("div", "abs", root, { left: x + "px", top: y + "px" });
  const kick = el("div", "abs", wrap, { left: 0, top: 0, background: o.color || PAL.red, color: "#fff", font: "24px 'Anton'",
    padding: "6px 16px 4px", letterSpacing: ".08em", whiteSpace: "nowrap" }, esc(o.kicker || "BREAKING"));
  const main = el("div", "abs", wrap, { left: 0, top: "40px", background: "#F4F6FA", color: "#0B1220", font: `${o.size || 46}px 'Anton'`,
    padding: "10px 26px 8px", whiteSpace: "nowrap", boxShadow: "0 16px 40px rgba(0,0,0,.45)" }, esc(o.text || ""));
  const sub = o.sub ? el("div", "abs", wrap, { left: 0, top: 40 + (o.size || 46) * 1.25 + 18 + "px", background: "rgba(10,23,48,.94)",
    color: "#DCE6F5", font: "26px 'Barlow'", padding: "8px 26px 6px", whiteSpace: "nowrap", letterSpacing: ".04em" }, esc(o.sub)) : null;
  const sw = sweep(main, 90);
  const at = o.at || 0.4;
  return t => {
    const a = eOut5(seg(t, at, 0.4));
    css(kick, "clipPath", `inset(0 ${((1 - a) * 100).toFixed(1)}% 0 0)`);
    const b = eOut5(seg(t, at + 0.15, 0.5));
    css(main, "clipPath", `inset(0 ${((1 - b) * 100).toFixed(1)}% 0 0)`);
    const q = seg(t, at + 0.55, 0.6);
    setO(sw, q > 0 && q < 1 ? 1 : 0); setT(sw, lerp(-200, (main.offsetWidth || 900) + 40, q), 0);
    if (sub) { const c = eOut5(seg(t, at + 0.4, 0.5)); css(sub, "clipPath", `inset(0 ${((1 - c) * 100).toFixed(1)}% 0 0)`); }
    if (o.out != null) setO(wrap, 1 - seg(t, o.out, 0.3));
  };
};

/* ---- breaking ------------------------------------------------------------------ */
SCENES.breaking = async (s, root) => {
  const L = s.img ? photoLayer(root, Object.assign({ move: "in", zoom: 1.12 }, s)) : (paperGround(root, "cork"), null);
  el("div", "full", root, { background: "linear-gradient(180deg, rgba(4,10,26,.55) 0%, rgba(4,10,26,.35) 40%, rgba(4,10,26,.9) 100%)" });
  el("div", "full", root, { background: "repeating-linear-gradient(0deg, rgba(0,0,0,.14) 0 2px, rgba(0,0,0,0) 2px 4px)" });
  vignette(root, 0.55);
  const y = s.y || 560;
  const slab = el("div", "abs", root, { left: "110px", top: y + "px", background: PAL.red, color: "#fff", font: `${s.ksize || 118}px 'Anton'`,
    padding: "10px 40px 2px", letterSpacing: ".02em", whiteSpace: "nowrap", boxShadow: "0 20px 60px rgba(0,0,0,.5)" }, esc(s.kicker || "BREAKING NEWS"));
  /* two chromatic ghosts for the glitch on entry */
  const gA = el("div", "abs", root, { left: "110px", top: y + "px", color: "rgba(0,220,255,.7)", font: `${s.ksize || 118}px 'Anton'`,
    padding: "10px 40px 2px", letterSpacing: ".02em", whiteSpace: "nowrap", mixBlendMode: "screen" }, esc(s.kicker || "BREAKING NEWS"));
  const gB = el("div", "abs", root, { left: "110px", top: y + "px", color: "rgba(255,40,80,.7)", font: `${s.ksize || 118}px 'Anton'`,
    padding: "10px 40px 2px", letterSpacing: ".02em", whiteSpace: "nowrap", mixBlendMode: "screen" }, esc(s.kicker || "BREAKING NEWS"));
  const kh = (s.ksize || 118) * 1.12 + 12;
  const head = el("div", "abs", root, { left: "110px", top: y + kh + 8 + "px", maxWidth: "1640px", background: "#F4F6FA", color: "#0B1220",
    font: `${s.hsize || 64}px 'Anton'`, lineHeight: "1.1", padding: "14px 34px 10px", boxShadow: "0 20px 60px rgba(0,0,0,.5)" }, esc(s.headline || ""));
  const sw = sweep(head, 200);
  const sub = s.sub ? el("div", "abs", root, { left: "110px", top: "0", background: "rgba(10,23,48,.95)", color: "#DCE6F5",
    font: "32px 'Barlow'", padding: "10px 34px 8px", letterSpacing: ".05em", whiteSpace: "nowrap" }, esc(s.sub)) : null;
  const flash = flashLayer(root);
  const D = s.duration, at = s.at != null ? s.at : 0.25, hAt = s.headAt != null ? s.headAt : at + 0.5, sAt = s.subAt != null ? s.subAt : hAt + 0.5;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    const p = eOut5(seg(t, at, 0.28));
    vis(slab, t >= at); setT(slab, 0, 0, lerp(1.35, 1, p));
    const g = t >= at && t < at + 0.45 ? 1 - (t - at) / 0.45 : 0;
    const j = Math.sin(t * 91) * 14 * g;
    setO(gA, g); setO(gB, g); setT(gA, -j - 10 * g, 3 * g); setT(gB, j + 10 * g, -3 * g);
    flash(t, at, 0.2);
    const b = eOut5(seg(t, hAt, 0.5));
    css(head, "clipPath", `inset(0 ${((1 - b) * 100).toFixed(1)}% 0 0)`);
    const q = seg(t, hAt + 0.6, 0.7);
    setO(sw, q > 0 && q < 1 ? 1 : 0); setT(sw, lerp(-200, (head.offsetWidth || 1400) + 60, q), 0);
    if (sub) {
      if (!sub._y) { sub.style.top = head.offsetTop + head.offsetHeight + 10 + "px"; sub._y = 1; }
      const c = eOut5(seg(t, sAt, 0.5)); css(sub, "clipPath", `inset(0 ${((1 - c) * 100).toFixed(1)}% 0 0)`);
    }
  };
};

/* ---- borehole ------------------------------------------------------------------ */
SCENES.borehole = async (s, root) => {
  paperGround(root, s.bg || "cork");
  const world = el("div", "full", root, { transformOrigin: "50% 50%" });
  const cv = el("canvas", "full", world); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  const X0 = 150, X1 = 1290, TOP = s.top || 390, BOT = s.bot || 1020;               /* the cross-section panel */
  const maxD = s.maxDepth || 6, hitD = s.hitDepth != null ? s.hitDepth : 4.5;
  const yOf = d => TOP + (d / maxD) * (BOT - TOP);
  const RX = s.rigX || 840;
  const layers = s.layers || [
    { from: 0, to: 0.6, kind: "soil" }, { from: 0.6, to: 2.0, kind: "sediment" }, { from: 2.0, to: 2.7, kind: "organic" },
    { from: 2.7, to: 4.4, kind: "sediment" }, { from: 4.4, to: maxD, kind: "hard" }];
  const cavities = s.cavities || [];
  const rr = rng(s.seed || 17);
  const speck = []; for (let i = 0; i < 900; i++) speck.push([rr(), rr(), rr()]);
  const title = s.title ? el("div", "abs", root, { left: X0 + "px", top: "120px", font: "58px 'Anton'", color: "#F4F6FA", letterSpacing: ".01em" }, esc(s.title)) : null;
  const kick = s.kicker ? el("div", "abs", root, { left: X0 + 2 + "px", top: "88px", font: "26px 'OswaldB'", color: PAL.mustard, letterSpacing: ".25em" }, esc(s.kicker)) : null;
  /* the readout panel on the right */
  const panel = el("div", "abs", root, { left: "1370px", top: "330px", width: "430px", height: "360px", background: "rgba(8,14,32,.9)",
    border: "2px solid rgba(30,167,255,.45)", boxShadow: "0 30px 60px rgba(0,0,0,.5)" });
  el("div", "abs", panel, { left: "28px", top: "24px", font: "24px 'OswaldB'", color: PAL.cyan, letterSpacing: ".25em" }, "DEPTH");
  const num = el("div", "abs", panel, { left: "24px", top: "60px", font: "150px 'Garamond'", color: "#F4F6FA", lineHeight: "1" }, "0.0");
  el("div", "abs", panel, { left: "30px", top: "226px", font: "30px 'Barlow'", color: "#9FB3D6", letterSpacing: ".1em" }, esc(s.unit || "METRES BELOW SURFACE"));
  const st = el("div", "abs", panel, { left: "28px", top: "282px", font: "30px 'Anton'", color: PAL.mustard, letterSpacing: ".06em" }, esc(s.statusText || "DRILLING"));
  const labs = (s.labels || []).map(lb => {
    const d = el("div", "abs", root, { left: 0, top: 0, background: lb.bg || "#F4F6FA", color: lb.color || "#0B1220", font: `${lb.size || 28}px 'Barlow'`,
      padding: "6px 16px 4px", whiteSpace: "nowrap", boxShadow: "0 8px 20px rgba(0,0,0,.4)", letterSpacing: ".03em" }, esc(lb.text));
    const ln = el("div", "abs", root, { left: 0, top: 0, height: "2px", background: "rgba(255,255,255,.7)", transformOrigin: "0 50%" });
    return { d, ln, lb };
  });
  const stamp = s.stamp ? ITEMS.stamp(root, Object.assign({ x: 1585, y: 800, rot: -6, size: 64 }, s.stamp)) : null;
  const B = Object.assign({ draw: 0.1, drill: 1.0, hit: 4.0 }, s.beats || {});
  const shatter = s.shatter !== false;
  const frags = []; const fr = rng(99);
  for (let i = 0; i < 26; i++) frags.push({ vx: (fr() - 0.5) * 520, vy: -120 - fr() * 380, r: fr() * 6.28, vr: (fr() - 0.5) * 16, s: 6 + fr() * 12 });
  const cracks = []; const cr = rng(7);
  for (let i = 0; i < 9; i++) { const a = -Math.PI * (0.05 + 0.9 * cr()) + (cr() < 0.5 ? 0 : Math.PI); const pts = [[0, 0]];
    let x = 0, y = 0; for (let k = 0; k < 6; k++) { x += Math.cos(a + (cr() - 0.5) * 0.9) * (10 + cr() * 18); y += Math.abs(Math.sin(a + (cr() - 0.5) * 0.6)) * (4 + cr() * 10); pts.push([x, y]); }
    cracks.push(pts); }
  const style = {
    soil: ["#5A4330", "#6B513A"], sediment: ["#9C8763", "#B09A74"], organic: ["#3B2C1F", "#4A3726"], hard: ["#3F4652", "#4E5663"], clay: ["#7D6A57", "#8B7762"],
  };
  const D = s.duration;
  return t => {
    const drawP = eInOut(seg(t, B.draw, 0.9));
    const dp = eInOut(seg(t, B.drill, Math.max(0.2, B.hit - B.drill)));
    const depth = lerp(0, shatter ? hitD : (s.toDepth || maxD), dp);
    const hitT = t - B.hit;
    const shake = shatter && hitT > 0 ? Math.exp(-hitT * 5) * 14 : 0;
    setT(world, Math.sin(t * 83) * shake, Math.cos(t * 71) * shake * 0.6);
    c.clearRect(0, 0, W, H);
    c.save();
    c.beginPath(); c.rect(X0, 0, (X1 - X0) * drawP, H); c.clip();
    /* sky band + surface with the formation's raised edges */
    const surf = x => TOP - 26 * Math.exp(-(((x - (RX - 300)) / 60) ** 2)) - 26 * Math.exp(-(((x - (RX + 300)) / 60) ** 2)) - 6 * Math.sin(x / 90);
    layers.forEach((L, i) => {
      const y0 = i === 0 ? null : yOf(L.from), y1 = yOf(Math.min(L.to, maxD));
      const [a, b] = style[L.kind] || style.sediment;
      c.beginPath();
      if (i === 0) { c.moveTo(X0, surf(X0)); for (let x = X0; x <= X1; x += 10) c.lineTo(x, surf(x)); }
      else { c.moveTo(X0, y0); for (let x = X0; x <= X1; x += 20) c.lineTo(x, y0 + Math.sin(x / 70 + i) * 5); }
      for (let x = X1; x >= X0; x -= 20) c.lineTo(x, y1 + Math.sin(x / 70 + i + 1) * 5);
      c.closePath();
      const g = c.createLinearGradient(0, y0 || TOP, 0, y1); g.addColorStop(0, a); g.addColorStop(1, b);
      c.fillStyle = g; c.fill();
      if (L.kind === "sediment" || L.kind === "clay") {
        c.strokeStyle = "rgba(60,45,30,.25)"; c.lineWidth = 2;
        for (let yy = (y0 || TOP) + 18; yy < y1; yy += 22) { c.beginPath(); for (let x = X0; x <= X1; x += 30) c.lineTo(x, yy + Math.sin(x / 55 + yy) * 3); c.stroke(); }
      }
      if (L.kind === "organic") { c.fillStyle = "rgba(20,14,8,.6)"; speck.forEach(([u, v, w]) => { if (w < 0.5) c.fillRect(X0 + u * (X1 - X0), (y0 || TOP) + v * (y1 - (y0 || TOP)), 3, 2); }); }
      if (L.kind === "hard") {
        c.strokeStyle = "rgba(255,255,255,.08)"; c.lineWidth = 2;
        for (let x = X0 - 400; x < X1; x += 26) { c.beginPath(); c.moveTo(x, y0); c.lineTo(x + (y1 - y0) * 0.6, y1); c.stroke(); }
      }
    });
    /* cavities */
    cavities.forEach(cv2 => {
      const q = eOut(seg(t, cv2.at != null ? cv2.at : 0, 0.6));
      if (q <= 0) return;
      const cx = cv2.x || RX + 160, cy = yOf(cv2.depth), rx = (cv2.w || 120) * q, ry = (cv2.h || 34) * q;
      c.fillStyle = "#101820"; c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.fill();
      if (cv2.water) {
        const lvl = cy + ry * (1 - 2 * cl(seg(t, cv2.fill != null ? cv2.fill : 0, 2.5), 0, 0.85));
        c.save(); c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.clip();
        c.fillStyle = "rgba(30,140,230,.75)"; c.fillRect(cx - rx, lvl, rx * 2, cy + ry - lvl);
        c.fillStyle = "rgba(170,220,255,.8)"; c.fillRect(cx - rx, lvl, rx * 2, 3); c.restore();
      }
      c.strokeStyle = "rgba(255,255,255,.35)"; c.lineWidth = 2; c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.stroke();
    });
    /* depth scale */
    c.fillStyle = "rgba(244,246,250,.85)"; c.font = "22px 'Barlow'"; c.textAlign = "right";
    for (let d = 0; d <= maxD; d += (maxD > 8 ? 2 : 1)) { const y = yOf(d); c.fillRect(X0 + 4, y - 1, 18, 2); c.fillText(d + " m", X0 - 10, y + 7); }
    /* the borehole, the drill string and the bit */
    const by = yOf(depth);
    c.fillStyle = "rgba(10,10,12,.85)"; c.fillRect(RX - 16, surf(RX) - 2, 32, by - surf(RX) + 4);
    const jit = t > B.drill && (t < B.hit || !shatter) ? Math.sin(t * 120) * 2 : 0;
    const steel = c.createLinearGradient(RX - 9, 0, RX + 9, 0); steel.addColorStop(0, "#6D7682"); steel.addColorStop(0.5, "#E1E6EC"); steel.addColorStop(1, "#5B636E");
    c.fillStyle = steel; c.fillRect(RX - 8 + jit, TOP - 170, 16, by - (TOP - 170) - 18);
    /* rig mast */
    c.strokeStyle = PAL.mustard; c.lineWidth = 6;
    c.beginPath(); c.moveTo(RX - 60, surf(RX) - 4); c.lineTo(RX - 10, TOP - 185); c.lineTo(RX + 10, TOP - 185); c.lineTo(RX + 60, surf(RX) - 4); c.stroke();
    c.lineWidth = 3; for (let k = 1; k < 4; k++) { const yy = surf(RX) - 4 - k * 42; const w = 60 - k * 13; c.beginPath(); c.moveTo(RX - w, yy); c.lineTo(RX + w, yy - 40); c.stroke(); }
    c.fillStyle = "#1B2B4F"; c.fillRect(RX - 90, surf(RX) - 30, 180, 26);
    if (!(shatter && hitT > 0)) {
      c.fillStyle = "#C9CED6"; c.beginPath(); c.moveTo(RX - 14 + jit, by - 20); c.lineTo(RX + 14 + jit, by - 20); c.lineTo(RX + jit, by + 6); c.closePath(); c.fill();
    } else {
      /* fragments and cracks */
      const u = hitT;
      frags.forEach(f => {
        const x = RX + f.vx * u * 0.6, y = by - 6 + f.vy * u * 0.6 + 600 * u * u * 0.6;
        if (y > by + 40 && u > 0.2) return;
        c.save(); c.translate(x, Math.min(y, by + 40)); c.rotate(f.r + f.vr * u); c.fillStyle = "#D6DBE2";
        c.beginPath(); c.moveTo(-f.s / 2, -f.s / 3); c.lineTo(f.s / 2, -f.s / 4); c.lineTo(0, f.s / 2); c.closePath(); c.fill(); c.restore();
      });
      const cp = eOut(seg(u, 0, 0.7));
      c.strokeStyle = "rgba(255,244,220,.85)"; c.lineWidth = 2;
      cracks.forEach(pts => { c.beginPath(); pts.forEach(([px, py], k) => { const q = Math.min(1, cp * 6 - k * 0.9); if (q <= 0) return;
        k ? c.lineTo(RX + px, by + py) : c.moveTo(RX + px, by + py); }); c.stroke(); });
      const fl = Math.exp(-u * 6);
      c.fillStyle = `rgba(255,230,160,${(0.8 * fl).toFixed(3)})`; c.beginPath(); c.arc(RX, by, 30 + 90 * (1 - fl), 0, Math.PI * 2); c.fill();
    }
    c.restore();
    /* panel frame */
    c.strokeStyle = "rgba(244,246,250,.25)"; c.lineWidth = 2; c.strokeRect(X0, TOP - 200, (X1 - X0) * drawP, BOT - TOP + 200);
    const txt = depth.toFixed(1);
    if (num._s !== txt) { num.textContent = txt; num._s = txt; }
    setO(panel, eOut(seg(t, B.draw + 0.4, 0.5)));
    if (shatter && hitT > 0) { if (st._s !== 1) { st.textContent = s.hitText || "BIT SHATTERED"; st.style.color = PAL.red; st._s = 1; } }
    if (title) setO(title, eOut(seg(t, 0.1, 0.5)));
    if (kick) setO(kick, eOut(seg(t, 0.1, 0.5)));
    labs.forEach(({ d, ln, lb }) => {
      const a = eOut(seg(t, lb.at || 0, 0.4));
      const ty = yOf(lb.depth), tx = lb.x || X1 - 40;
      const w = d.offsetWidth;
      setT(d, tx - w, ty - 22 - (lb.dy || 0)); setO(d, a);
      const x0 = RX + 30, x1 = tx - w - 10;
      setT(ln, x0, ty - (lb.dy || 0) * 0.0); css(ln, "width", Math.max(0, (x1 - x0) * a).toFixed(0) + "px"); setO(ln, a * (lb.line === false ? 0 : 1));
    });
    if (stamp) stamp(t);
  };
};

/* ---- factcheck ------------------------------------------------------------------ */
SCENES.factcheck = async (s, root) => {
  paperGround(root, s.bg || "cork");
  vignette(root, 0.45);
  const card = el("div", "abs", root, { left: "110px", top: "170px", width: "940px", background: "rgba(244,246,250,.97)", color: "#0B1220",
    padding: "44px 56px 40px", boxShadow: "0 40px 90px rgba(0,0,0,.55)", borderLeft: `14px solid ${PAL.red}` });
  el("div", "", card, { font: "26px 'OswaldB'", color: PAL.red, letterSpacing: ".25em", marginBottom: "18px" }, esc(s.kicker || "THE CLAIM"));
  const q = el("div", "", card, { font: `${s.size || 54}px 'DMSerif'`, lineHeight: "1.18" }, esc(s.claim || ""));
  el("div", "", card, { font: "26px 'Barlow'", color: "#4A5670", marginTop: "24px", letterSpacing: ".04em" }, esc(s.source || ""));
  const scale = s.scale || ["CONFIRMED", "UNVERIFIED", "DISPUTED", "FALSE"];
  const cols = s.colors || [PAL.green, PAL.mustard, "#FF7A1A", PAL.red];
  const MX = 1260, MW = 540, MY = 250;
  const meter = el("div", "abs", root, { left: MX + "px", top: MY + "px", width: MW + "px" });
  el("div", "", meter, { font: "26px 'OswaldB'", color: "#DCE6F5", letterSpacing: ".25em", marginBottom: "18px" }, esc(s.meterTitle || "FACT CHECK"));
  const rows = scale.map((lab, i) => el("div", "", meter, { height: "86px", marginBottom: "12px", background: "rgba(8,14,32,.85)",
    border: `2px solid ${cols[i]}55`, color: "#9FB3D6", font: "40px 'Anton'", lineHeight: "90px", paddingLeft: "34px", letterSpacing: ".04em",
    position: "relative" }, esc(lab)));
  const needle = el("div", "abs", meter, { left: "-44px", top: 0, width: 0, height: 0, borderTop: "22px solid transparent",
    borderBottom: "22px solid transparent", borderLeft: `34px solid ${"#F4F6FA"}` });
  const ri = Math.max(0, scale.indexOf(s.rating || "UNVERIFIED"));
  const note = s.note ? el("div", "abs", root, { left: "120px", top: "0", width: "1000px", font: "34px 'GaramondI'", color: "#DCE6F5", lineHeight: "1.3" }, esc(s.note)) : null;
  const A = s.ratingAt != null ? s.ratingAt : 1.6;
  return t => {
    const a = eOut5(seg(t, 0.1, 0.6)); setO(card, a); setT(card, (1 - a) * -80, 0);
    setO(meter, eOut(seg(t, 0.5, 0.5)));
    /* the needle scans the scale, then settles on the rating */
    const top0 = 44 + 43 - 22;
    const scan = seg(t, 0.8, Math.max(0.3, A - 0.8));
    let pos = scan < 1 ? (Math.sin(scan * Math.PI * 2.5) * 0.5 + 0.5) * (scale.length - 1) : ri;
    if (t >= A) pos = ri + (Math.exp(-(t - A) * 6) * Math.sin((t - A) * 20)) * 0.25;
    setT(needle, 0, top0 + pos * 98);
    setO(needle, t > 0.8 ? 1 : 0);
    rows.forEach((r, i) => {
      const on = t >= A && i === ri;
      css(r, "background", on ? cols[i] : "rgba(8,14,32,.85)");
      css(r, "color", on ? (i === 1 ? "#0B1220" : "#fff") : "#9FB3D6");
      r.style.transform = on ? `scale(${(1 + 0.06 * Math.exp(-(t - A) * 5)).toFixed(3)})` : "none";
    });
    if (note) { if (!note._y) { note.style.top = card.offsetTop + card.offsetHeight + 40 + "px"; note._y = 1; }
      setO(note, eOut(seg(t, s.noteAt != null ? s.noteAt : A + 0.8, 0.6))); }
  };
};

/* ---- echo: many headlines, one source ------------------------------------------------ */
SCENES.echo = async (s, root) => {
  paperGround(root, s.bg || "cork");
  vignette(root, 0.5);
  const hs = s.headlines || [];
  const cols = s.cols || 4, rows = Math.ceil(hs.length / cols);
  const CW = 400, CH = 150, GX = 36, GY = 30;
  const ox = (W - (cols * CW + (cols - 1) * GX)) / 2, oy = 220;
  const counter = el("div", "abs", root, { left: 0, width: W + "px", top: "70px", textAlign: "center", font: "70px 'Anton'", color: "#F4F6FA" }, "");
  const cards = hs.map((h, i) => {
    const d = el("div", "abs", root, { left: 0, top: 0, width: CW + "px", height: CH + "px", boxSizing: "border-box", background: "#F4F6FA",
      color: "#0B1220", padding: "16px 20px", boxShadow: "0 16px 30px rgba(0,0,0,.45)", borderTop: `6px solid ${PAL.red}`, transformOrigin: "50% 50%" });
    el("div", "", d, { font: "18px 'OswaldB'", color: "#6A7896", letterSpacing: ".2em", marginBottom: "8px" }, esc(h.tag || `HEADLINE ${i + 1}`));
    el("div", "", d, { font: "27px 'Anton'", lineHeight: "1.12" }, esc(h.text || h));
    return { d, i, x: ox + (i % cols) * (CW + GX), y: oy + Math.floor(i / cols) * (CH + GY), at: h.at != null ? h.at : 0.2 + i * (s.gap || 0.18) };
  });
  const srcs = (s.sources || [{ title: "ONE PRESS RELEASE", sub: "" }]).map((sr, k) => {
    const d = el("div", "abs", root, { left: 0, top: 0, width: "720px", boxSizing: "border-box", background: "#F4F6FA", color: "#0B1220",
      padding: "30px 40px", boxShadow: "0 40px 90px rgba(0,0,0,.6)", borderLeft: `14px solid ${k ? PAL.mustard : PAL.red}` });
    el("div", "", d, { font: "56px 'Anton'", lineHeight: "1.05" }, esc(sr.title));
    if (sr.sub) el("div", "", d, { font: "28px 'Barlow'", color: "#4A5670", marginTop: "12px" }, esc(sr.sub));
    return { d, k, sr };
  });
  const C = s.collapseAt != null ? s.collapseAt : 3.0;
  const n = hs.length;
  return t => {
    let shown = 0;
    cards.forEach(o => {
      const a = eOut5(seg(t, o.at, 0.35));
      if (t >= o.at) shown++;
      const q = eInOut(seg(t, C + o.i * 0.03, 0.7));
      const tx = W / 2 - CW / 2 + (o.i % 3 - 1) * 8, ty = 470 + (o.i % 2) * 6;
      setT(o.d, lerp(o.x, tx, q), lerp(o.y, ty, q), lerp(lerp(1.3, 1, a), 0.6, q), lerp(0, (o.i % 5 - 2) * 3, q));
      setO(o.d, (t >= o.at ? a : 0) * (1 - seg(t, C + 0.6, 0.3)));
    });
    srcs.forEach(({ d, k, sr }) => {
      const at = C + 0.6 + k * (s.sourceGap || 0.7);
      const a = eBack(seg(t, at, 0.5), 1.3);
      const h = d.offsetHeight;
      setT(d, W / 2 - 360, (srcs.length > 1 ? 380 + k * (h + 34) : 470) , lerp(0.6, 1, a));
      setO(d, cl((t - at) * 5, 0, 1));
    });
    const txt = t < C + 0.6 ? `${shown} ${esc(s.unit || "HEADLINES")}` : (s.result || `${n} HEADLINES = ${srcs.length} SOURCE${srcs.length > 1 ? "S" : ""}`);
    if (counter._s !== txt) { counter.innerHTML = txt; counter._s = txt; }
    setO(counter, eOut(seg(t, 0.1, 0.4)));
    css(counter, "color", t < C + 0.6 ? "#F4F6FA" : PAL.mustard);
  };
};

/* ---- columns: observed vs claimed ----------------------------------------------------- */
SCENES.columns = async (s, root) => {
  paperGround(root, s.bg || "cork");
  vignette(root, 0.45);
  const sides = [s.left || { title: "OBSERVED" }, s.right || { title: "CLAIMED" }];
  const cols = [sides[0].color || PAL.cyan, sides[1].color || PAL.red];
  const X = [110, 1090], CW = 720, TOP = 130;
  const heads = sides.map((sd, i) => {
    const h = el("div", "abs", root, { left: X[i] + "px", top: TOP + "px", width: CW + "px", height: "86px", background: cols[i], color: "#fff",
      font: "54px 'Anton'", lineHeight: "92px", paddingLeft: "30px", boxSizing: "border-box", letterSpacing: ".03em" }, esc(sd.title));
    if (sd.sub) el("div", "abs", h, { right: "24px", top: "0", lineHeight: "90px", font: "22px 'Barlow'", letterSpacing: ".15em", color: "rgba(255,255,255,.85)", textTransform: "uppercase" }, esc(sd.sub));
    return h;
  });
  const y0 = [0, 0];
  const rows = (s.items || []).map(it => {
    const y = TOP + 110 + y0[it.side]; y0[it.side] += s.gap || 108;
    const r = el("div", "abs", root, { left: X[it.side] + "px", top: y + "px", width: CW + "px", minHeight: "92px", boxSizing: "border-box",
      background: "rgba(8,14,32,.88)", borderLeft: `8px solid ${cols[it.side]}`, padding: "14px 24px 12px", color: "#F4F6FA" });
    el("div", "", r, { font: `${it.size || 34}px 'DMSerif'`, lineHeight: "1.15" }, esc(it.text));
    if (it.tag) el("div", "", r, { font: "20px 'Barlow'", color: cols[it.side], letterSpacing: ".14em", marginTop: "6px", textTransform: "uppercase" }, esc(it.tag));
    return { r, it, y };
  });
  /* the gap: arrows from the claims reach toward the observations and stop short */
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  Object.assign(svg.style, { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px", overflow: "visible" });
  root.appendChild(svg);
  const gapRows = rows.filter(r => r.it.side === 1);
  const arrows = gapRows.map((r, k) => {
    const p = document.createElementNS(svgNS, "path");
    const y = r.y + 46;
    p.setAttribute("stroke", PAL.mustard); p.setAttribute("stroke-width", 5); p.setAttribute("stroke-dasharray", "14 10"); p.setAttribute("fill", "none");
    svg.appendChild(p);
    const qm = el("div", "abs", root, { left: X[0] + CW + 18 + "px", top: y - 30 + "px", font: "54px 'Anton'", color: PAL.mustard }, "?");
    return { p, qm, k, y };
  });
  const gapText = s.gapText ? el("div", "abs", root, { left: 0, width: W + "px", top: "995px", textAlign: "center", font: "46px 'Anton'",
    color: PAL.mustard, letterSpacing: ".04em" }, esc(s.gapText)) : null;
  const G = s.gapAt;
  return t => {
    heads.forEach((h, i) => { const a = eOut5(seg(t, s.headAt ? s.headAt[i] : 0.1 + i * 0.3, 0.45)); css(h, "clipPath", `inset(0 ${((1 - a) * 100).toFixed(1)}% 0 0)`); });
    rows.forEach(({ r, it }) => { const a = eOut5(seg(t, it.at || 0, 0.45)); setO(r, a); setT(r, (it.side ? 1 : -1) * (1 - a) * 60, 0); });
    arrows.forEach(({ p, qm, k, y }) => {
      const q = G == null ? 0 : eInOut(seg(t, G + k * 0.15, 0.6));
      const len = X[1] - 10 - (X[0] + CW + 70);
      p.setAttribute("d", `M${X[1] - 10} ${y} L${(X[1] - 10 - len * q).toFixed(1)} ${y}`);
      p.style.opacity = q > 0 ? 1 : 0;
      setO(qm, G == null ? 0 : eOut(seg(t, G + k * 0.15 + 0.6, 0.3)));
    });
    if (gapText) setO(gapText, G == null ? 0 : eOut(seg(t, G + 0.9, 0.5)));
  };
};

/* ---- videowall ---------------------------------------------------------------------- */
SCENES.videowall = async (s, root) => {
  paperGround(root, s.bg || "cork");
  const world = el("div", "full", root, { transformOrigin: "0 0" });
  const imgs = s.imgs || [];
  const SW = 560, SH = 315, GX = 26, GY = 26;
  const ox = (W - (3 * SW + 2 * GX)) / 2, oy = (H - (3 * SH + 2 * GY)) / 2 + 20;
  const screens = [];
  for (let i = 0; i < 9; i++) {
    const x = ox + (i % 3) * (SW + GX), y = oy + Math.floor(i / 3) * (SH + GY);
    const box = el("div", "abs", world, { left: x + "px", top: y + "px", width: SW + "px", height: SH + "px", overflow: "hidden",
      background: "#050a14", boxShadow: "0 0 0 6px #111827, 0 0 40px rgba(30,167,255,.25)" });
    const im = pic(imgs[i % Math.max(1, imgs.length)], box);
    el("div", "abs", box, { left: 0, top: 0, width: "100%", height: "100%",
      background: "repeating-linear-gradient(0deg, rgba(0,0,0,.18) 0 2px, rgba(0,0,0,0) 2px 4px)" });
    screens.push({ box, im, x, y });
  }
  vignette(root, 0.55);
  const F = s.focus != null ? s.focus : 4, P = s.pushAt != null ? s.pushAt : 1.2, D = s.duration;
  return t => {
    screens.forEach((o, i) => {
      const iw = o.im.naturalWidth || SW, ih = o.im.naturalHeight || SH;
      const c = coverCam(iw, ih, 0.5, 0.5, 1.05 + 0.04 * Math.sin(t * 0.4 + i), SW, SH);
      setT(o.im, c.tx, c.ty, c.k);
      setO(o.box, eOut(seg(t, 0.05 + i * 0.06, 0.35)) * (i === F ? 1 : lerp(1, 0.45, seg(t, P, 0.5))));
    });
    const q = eInOut(seg(t, P, s.pushFor || 2.2));
    const f = screens[F];
    const k = lerp(1, W / SW * 1.02, q);
    const cx = lerp(W / 2, f.x + SW / 2, q), cy = lerp(H / 2, f.y + SH / 2, q);
    setT(world, W / 2 - cx * k, H / 2 - cy * k, k);
  };
};

/* ---- newslist ----------------------------------------------------------------------- */
SCENES.newslist = async (s, root) => {
  const L = s.img ? darkPhoto(root, s, s.dim != null ? s.dim : 0.72) : (paperGround(root, s.bg || "cork"), null);
  vignette(root, 0.5);
  const title = el("div", "abs", root, { left: "150px", top: "110px", font: "64px 'Anton'", color: "#F4F6FA", letterSpacing: ".01em" }, esc(s.title || ""));
  const bar = el("div", "abs", root, { left: "152px", top: "196px", height: "6px", width: "0", background: PAL.red });
  const rows = (s.items || []).map((it, i) => {
    const y = (s.y0 || 260) + i * (s.gap || 150);
    const r = el("div", "abs", root, { left: "150px", top: y + "px", width: "1620px", height: (s.rowH || 120) + "px", display: "flex", alignItems: "stretch" });
    el("div", "", r, { width: "120px", background: PAL.red, color: "#fff", font: "64px 'Anton'", textAlign: "center", lineHeight: (s.rowH || 120) + 4 + "px" },
      esc(it.n != null ? it.n : String(i + 1)));
    const body = el("div", "", r, { flex: "1", background: "rgba(244,246,250,.96)", color: "#0B1220", padding: "0 30px", display: "flex", flexDirection: "column", justifyContent: "center" });
    el("div", "", body, { font: `${it.size || s.size || 42}px 'Anton'`, lineHeight: "1.1" }, esc(it.text));
    if (it.sub) el("div", "", body, { font: "26px 'Barlow'", color: "#4A5670", marginTop: "6px" }, esc(it.sub));
    const pill = it.status ? el("div", "", r, { width: "330px", background: it.statusColor || "#0B1220", color: it.statusColor ? "#0B1220" : PAL.mustard,
      font: `${it.status.length > 13 ? 22 : it.status.length > 10 ? 26 : 32}px 'Anton'`, textAlign: "center", lineHeight: (s.rowH || 120) + 4 + "px",
      letterSpacing: ".03em", whiteSpace: "nowrap" }, esc(it.status)) : null;
    return { r, it, pill };
  });
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    setO(title, eOut(seg(t, 0.05, 0.5)));
    css(bar, "width", (eOut(seg(t, 0.3, 0.6)) * 260).toFixed(0) + "px");
    rows.forEach(({ r, it, pill }) => {
      const a = eOut5(seg(t, it.at || 0, 0.45));
      css(r, "clipPath", `inset(0 ${((1 - a) * 100).toFixed(1)}% 0 0)`);
      if (pill) { const p = eOut5(seg(t, it.statusAt != null ? it.statusAt : (it.at || 0) + 0.5, 0.25)); setO(pill, p); pill.style.transform = `scale(${lerp(1.4, 1, p).toFixed(3)})`; }
    });
  };
};

/* ---- segment bumper --------------------------------------------------------------- */
SCENES.segment = async (s, root) => {
  const L = s.img ? photoLayer(root, Object.assign({ move: "in", zoom: 1.1 }, s)) : null;
  if (!L) paperGround(root, "cork");
  el("div", "full", root, { background: L ? "linear-gradient(90deg, rgba(4,10,26,.92) 0%, rgba(4,10,26,.7) 55%, rgba(4,10,26,.35) 100%)" : "transparent" });
  const bars = [[PAL.red, 0, 150], ["#10214A", 0.08, 260], ["#F4F6FA", 0.16, 40], [PAL.red, 0.22, 90]].map(([col, d, h], i) =>
    ({ e: el("div", "abs", root, { left: 0, top: 380 + i * 70 + "px", width: W * 1.4 + "px", height: h + "px", background: col,
      transform: "skewX(-18deg)", transformOrigin: "0 0" }), d, i }));
  const box = el("div", "abs", root, { left: "150px", top: "400px", width: "170px", height: "170px", background: PAL.red, color: "#fff",
    font: "120px 'Anton'", textAlign: "center", lineHeight: "178px", boxShadow: "0 20px 50px rgba(0,0,0,.5)" }, esc(s.n || ""));
  const kick = el("div", "abs", root, { left: "360px", top: "404px", font: "30px 'OswaldB'", color: PAL.mustard, letterSpacing: ".3em" }, esc(s.kicker || ""));
  const tt = el("div", "abs", root, { left: "356px", top: "444px", font: `${s.size || 104}px 'Anton'`, color: "#F4F6FA", whiteSpace: "nowrap",
    lineHeight: "1.05", textShadow: "0 10px 40px rgba(0,0,0,.5)" }, esc(s.title || ""));
  const rule = el("div", "abs", root, { left: "360px", top: 444 + (s.size || 104) * 1.12 + 10 + "px", height: "6px", width: "0", background: PAL.red });
  const sub = s.sub ? el("div", "abs", root, { left: "360px", top: 444 + (s.size || 104) * 1.12 + 34 + "px", font: "34px 'Barlow'", color: "#B9C7E0",
    letterSpacing: ".06em" }, esc(s.sub)) : null;
  vignette(root, 0.5);
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    bars.forEach(({ e, d, i }) => {
      const a = eInOut(seg(t, d, 0.55)), b = eInOut(seg(t, 0.55 + d * 0.6, 0.55));
      const x = lerp(-W * 1.5, 0, a) + lerp(0, W * 1.6, b);
      setT(e, x, 0); setO(e, i === 1 ? 0.95 : 1);
    });
    const p = eBack(seg(t, 0.55, 0.45), 1.4); setT(box, 0, 0, p); setO(box, cl((t - 0.55) * 6, 0, 1));
    const q = eOut5(seg(t, 0.7, 0.5)); css(tt, "clipPath", `inset(0 ${((1 - q) * 100).toFixed(1)}% 0 0)`); vis(tt, t >= 0.7);
    setO(kick, eOut(seg(t, 0.8, 0.4)));
    css(rule, "width", (eOut(seg(t, 1.0, 0.6)) * 420).toFixed(0) + "px");
    if (sub) setO(sub, eOut(seg(t, 1.2, 0.5)));
  };
};
