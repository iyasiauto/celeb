/* scenes_map.js - map animation over real geography (Natural Earth, from the kit).

   One scene is one continuous camera move on an orthographic globe: at a small scale
   it is the planet, at a large one a province fills the frame. The camera travels
   through `stops` ({at, lon, lat, scale}); countries light up, pins drop with rings,
   routes and distance lines draw themselves, and labels hang off leader lines.

   Style: the dark teal explainer map of the documentary sample.
*/
"use strict";

const MAPLIB = { loaded: null, topo: {} };
function loadScript(src) {
  return new Promise((res, rej) => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = rej; document.head.appendChild(s); });
}
async function mapLibs() {
  if (!MAPLIB.loaded) MAPLIB.loaded = (async () => {
    await loadScript(CFG.kit + "/maps/lib/d3-array.min.js");
    await loadScript(CFG.kit + "/maps/lib/d3-geo.min.js");
    await loadScript(CFG.kit + "/maps/lib/topojson-client.min.js");
  })();
  return MAPLIB.loaded;
}
async function topo(name) {
  /* fetch() refuses file:// even with file access allowed; XHR does not */
  if (!MAPLIB.topo[name]) MAPLIB.topo[name] = new Promise((res, rej) => {
    const x = new XMLHttpRequest();
    x.open("GET", CFG.kit + "/maps/" + name);
    x.onload = () => { try { res(JSON.parse(x.responseText)); } catch (e) { rej(e); } };
    x.onerror = rej;
    x.send();
  });
  return MAPLIB.topo[name];
}

/* map palette: the dark teal explainer by default, a theme may swap in its own */
const MAPC = Object.assign({
  bg0: "#0E3440", bg1: "#04141A", sea: "#0B2A34", rim: "rgba(120,200,215,.35)", grat: "rgba(120,190,205,.08)",
  land: "#18505E", border: "rgba(160,220,232,.45)", admin: "150,210,222", hi: "47,150,168", text: "#F4EFE4",
  sub: "#CFE3E6", dot: "#EAF2F3", dotText: "#DDEBED", name: "rgba(214,232,236,.8)", shadow: "rgba(0,0,0,.7)", paper: null,
}, (THEME && THEME.map) || {});

SCENES.map = async (s, root) => {
  await mapLibs();
  const detail = s.detail || "geo_mid.json";
  const tp = await topo(detail);
  const countries = topojson.feature(tp, tp.objects.countries).features;
  const admin = tp.objects.admin1 ? topojson.feature(tp, tp.objects.admin1).features : [];
  let water = [];
  try { const wt = await topo("water.json"); const key = Object.keys(wt.objects)[0]; water = topojson.feature(wt, wt.objects[key]).features; } catch (e) {}
  const byId = {}; countries.forEach(f => { byId[f.id] = f; });
  const adminById = {}; admin.forEach(f => { adminById[f.id] = f; });
  /* cull: bounds once, then per frame only what can be on screen */
  countries.forEach(f => { f._b = d3.geoBounds(f); });
  const adminKeep = new Set(s.adminCountries || ["TUR", "IRN", "ARM", "AZE", "GEO", "IRQ", "SYR"]);
  const adminUse = admin.filter(f => adminKeep.has(String(f.id).split("-")[0]));
  adminUse.forEach(f => { f._b = d3.geoBounds(f); });
  water.forEach(f => { f._b = d3.geoBounds(f); });
  function inView(f, cam) {
    const b = f._b; if (!b) return true;
    const spanLat = 90 * 1100 / cam.scale + 2, spanLon = spanLat / Math.max(0.2, Math.cos(cam.lat * Math.PI / 180)) * 1.8;
    if (cam.scale < 1400) return true;
    const [[x0, y0], [x1, y1]] = b;
    if (y1 < cam.lat - spanLat || y0 > cam.lat + spanLat) return false;
    if (x0 <= x1) return !(x1 < cam.lon - spanLon || x0 > cam.lon + spanLon);
    return true;
  }

  const cv = el("canvas", "full", root); cv.width = W; cv.height = H;
  const c = cv.getContext("2d");
  let paperImg = null;
  if (MAPC.paper) { paperImg = new Image(); WAITS.push(new Promise(r => { paperImg.onload = r; paperImg.onerror = r; })); paperImg.src = asset(MAPC.paper); }
  const over = el("div", "full", root);
  vignette(root, 0.55);

  const proj = d3.geoOrthographic().translate([W / 2, H / 2]).clipAngle(90).precision(1.2);
  const path = d3.geoPath(proj, c);
  const grat = d3.geoGraticule10();
  const stops = s.stops;
  const D = s.duration;

  /* camera at time t: eased hops between stops, scale interpolated in log space */
  function camera(t) {
    let a = stops[0];
    let cur = { lon: a.lon, lat: a.lat, scale: a.scale };
    for (let i = 1; i < stops.length; i++) {
      const b = stops[i];
      const prevAt = stops[i - 1].at || 0, dur = b.d || Math.max(0.6, (b.at || 0) - prevAt);
      const p = eInOut(seg(t, (b.at || 0) - dur, dur));
      if (p <= 0) break;
      cur = { lon: lerp(cur.lon, b.lon, p), lat: lerp(cur.lat, b.lat, p), scale: Math.exp(lerp(Math.log(cur.scale), Math.log(b.scale), p)) };
    }
    /* a gentle continuous drift so a held stop never looks frozen */
    const dz = 1 + 0.02 * (t / D);
    return { lon: cur.lon, lat: cur.lat, scale: cur.scale * dz };
  }

  /* labels and pins live in the DOM so type stays crisp */
  const pins = (s.pins || []).map(p => {
    const g = el("div", "abs", over, { left: 0, top: 0 });
    const ring1 = el("div", "abs", g, { left: "-10px", top: "-10px", width: "20px", height: "20px", borderRadius: "50%", border: `3px solid ${PAL.red}` });
    const ring2 = el("div", "abs", g, { left: "-10px", top: "-10px", width: "20px", height: "20px", borderRadius: "50%", border: `3px solid ${PAL.red}` });
    const head = el("div", "abs", g, {
      left: "-17px", top: "-52px", width: "34px", height: "34px", borderRadius: "50% 50% 50% 0", transform: "rotate(-45deg)",
      background: p.color || "#E0412F", boxShadow: "0 8px 14px rgba(0,0,0,.45)",
    });
    el("div", "abs", head, { left: "11px", top: "11px", width: "12px", height: "12px", borderRadius: "50%", background: "#fff" });
    const side = p.side || "left";
    const lab = el("div", "abs", g, { top: "-40px", whiteSpace: "nowrap", textAlign: side === "left" ? "right" : "left" });
    if (side === "left") lab.style.right = (p.gap || 170) + "px"; else lab.style.left = (p.gap || 170) + "px";
    el("div", "", lab, { font: `${p.size || 54}px 'DMSerif'`, color: MAPC.text, textShadow: `0 3px 16px ${MAPC.shadow}`, letterSpacing: ".02em" }, esc((p.label || "").toUpperCase()));
    if (p.sub) el("div", "", lab, { font: "22px 'Barlow'", color: MAPC.sub, letterSpacing: ".08em", marginTop: "2px", textShadow: "0 2px 10px rgba(0,0,0,.8)" }, esc(p.sub));
    const lead = el("div", "abs", g, { top: "-14px", height: "2px", background: "rgba(244,239,228,.85)" });
    if (side === "left") lead.style.right = "22px"; else lead.style.left = "22px";
    return { p, g, ring1, ring2, head, lab, lead };
  });
  const dots = (s.dots || []).map(d => {
    const g = el("div", "abs", over, { left: 0, top: 0 });
    el("div", "abs", g, { left: "-7px", top: "-7px", width: "14px", height: "14px", borderRadius: "50%", background: MAPC.dot, boxShadow: "0 0 0 4px rgba(234,242,243,.18)" });
    el("div", "abs", g, { left: "16px", top: "-16px", font: "26px 'Barlow'", color: MAPC.dotText, letterSpacing: ".06em", whiteSpace: "nowrap", textShadow: "0 2px 8px rgba(0,0,0,.9)" }, esc(d.label));
    return { d, g };
  });
  const names = (s.names || []).map(n => {
    const e = el("div", "abs", over, { left: 0, top: 0, font: `${n.size || 34}px 'Barlow'`, letterSpacing: ".45em", color: n.color || MAPC.name, whiteSpace: "nowrap", textShadow: "0 2px 12px rgba(0,0,0,.7)" }, esc(n.text.toUpperCase()));
    return { n, e };
  });
  const title = s.title ? el("div", "abs", over, { left: "110px", top: "90px", font: "30px 'BarlowB'", letterSpacing: ".35em", color: PAL.mustard }, esc(s.title)) : null;

  return t => {
    const cam = camera(t);
    proj.rotate([-cam.lon, -cam.lat]).scale(cam.scale);
    const g = c.createRadialGradient(W / 2, H / 2, 100, W / 2, H / 2, 1200);
    g.addColorStop(0, MAPC.bg0); g.addColorStop(1, MAPC.bg1);
    c.fillStyle = g; c.fillRect(0, 0, W, H);
    if (paperImg) { c.globalAlpha = 0.9; c.drawImage(paperImg, 0, 0, W, H); c.globalAlpha = 1; }
    /* ocean disc with a soft rim when the whole globe is in view */
    c.beginPath(); path({ type: "Sphere" });
    c.fillStyle = MAPC.sea; c.fill();
    if (cam.scale < 900) { c.lineWidth = 2; c.strokeStyle = MAPC.rim; c.stroke(); }
    c.beginPath(); path(grat); c.lineWidth = 1; c.strokeStyle = MAPC.grat; c.stroke();
    /* land */
    const vis_ = countries.filter(f => inView(f, cam));
    const land = new Path2D(d3.geoPath(proj)({ type: "FeatureCollection", features: vis_ }) || "");
    c.fillStyle = MAPC.land; c.fill(land);
    if (water.length && cam.scale > 1500) {
      const wv = water.filter(f => inView(f, cam));
      if (wv.length) { c.fillStyle = MAPC.sea; c.fill(new Path2D(d3.geoPath(proj)({ type: "FeatureCollection", features: wv }) || "")); }
    }
    if (adminUse.length && cam.scale > 2200) {
      const av = adminUse.filter(f => inView(f, cam));
      c.lineWidth = 1; c.strokeStyle = `rgba(${MAPC.admin},${cl((cam.scale - 2200) / 3000, 0, 0.22).toFixed(3)})`;
      c.stroke(new Path2D(d3.geoPath(proj)({ type: "FeatureCollection", features: av }) || ""));
    }
    c.lineWidth = 1.4; c.strokeStyle = MAPC.border; c.stroke(land);
    /* highlighted countries / provinces */
    (s.highlight || []).forEach(h => {
      const f = byId[h.id] || adminById[h.id];
      if (!f) return;
      const a = eOut(seg(t, h.at || 0, 0.8)) * (h.out != null ? 1 - seg(t, h.out, 0.5) : 1);
      if (a <= 0) return;
      c.beginPath(); path(f);
      c.fillStyle = h.fill || `rgba(${MAPC.hi},${((MAPC.hiA || 0.75) * a).toFixed(3)})`; c.globalAlpha = h.fill ? a : 1; c.fill(); c.globalAlpha = 1;
      c.lineWidth = 3; c.strokeStyle = `rgba(217,164,65,${a.toFixed(3)})`; c.stroke();
    });
    /* radius circles (e.g. "29 km") */
    (s.circles || []).forEach(k => {
      const a = eOut(seg(t, k.at || 0, 0.8));
      if (a <= 0) return;
      const circ = d3.geoCircle().center([k.lon, k.lat]).radius(k.km / 111.2 * a)();
      c.beginPath(); path(circ); c.setLineDash([10, 8]); c.lineWidth = 3; c.strokeStyle = "rgba(244,239,228,.8)"; c.stroke(); c.setLineDash([]);
    });
    /* routes: great-circle lines that draw themselves */
    (s.routes || []).forEach(r => {
      const a = eInOut(seg(t, r.at || 0, r.d || 1.2));
      if (a <= 0) return;
      const interp = d3.geoInterpolate(r.from, r.to);
      const pts = []; for (let i = 0; i <= 60 * a; i++) pts.push(interp(i / 60));
      if (pts.length < 2) return;
      c.beginPath(); path({ type: "LineString", coordinates: pts });
      c.lineWidth = r.width || 5; c.strokeStyle = r.color || PAL.mustard; c.setLineDash(r.dash ? [14, 10] : []); c.stroke(); c.setLineDash([]);
      if (r.label && a >= 1) {
        const m = proj(interp(0.5));
        if (m) {
          const q = eOut(seg(t, (r.at || 0) + (r.d || 1.2), 0.4));
          c.globalAlpha = q; c.font = "44px 'Anton'"; c.fillStyle = MAPC.text; c.textAlign = "center";
          c.shadowColor = "rgba(0,0,0,.8)"; c.shadowBlur = 14;
          c.fillText(r.label, m[0] + (r.lx || 0), m[1] + (r.ly || -24)); c.shadowBlur = 0; c.globalAlpha = 1;
        }
      }
    });
    /* DOM overlays follow the projection */
    pins.forEach(o => {
      const xy = proj([o.p.lon, o.p.lat]);
      const at = o.p.at || 0;
      if (!xy || t < at) { vis(o.g, false); return; }
      vis(o.g, true);
      setT(o.g, xy[0], xy[1]);
      const drop = seg(t, at, 0.5);
      const b = drop < 1 ? (1 - (1 - drop) * (1 - drop)) : 1;
      o.head.style.transform = `translate(0px, ${((1 - b) * -120).toFixed(1)}px) rotate(-45deg)`;
      setO(o.head, cl(drop * 4, 0, 1));
      [o.ring1, o.ring2].forEach((r, i) => {
        const u = ((t - at - 0.45 - i * 0.6) % 1.8 + 1.8) % 1.8 / 1.8;
        const on = t > at + 0.45 + i * 0.6;
        setO(r, on ? (1 - u) * 0.8 : 0);
        r.style.transform = `scale(${(1 + u * 5).toFixed(3)})`;
      });
      const lq = eOut(seg(t, at + 0.5, 0.5));
      css(o.lead, "width", ((o.p.gap || 170) - 30) * lq + "px");
      const tq = eOut(seg(t, at + 0.8, 0.5));
      setO(o.lab, tq);
      o.lab.style.transform = `translate(${((1 - tq) * (o.p.side === "right" ? -16 : 16)).toFixed(1)}px,0)`;
      if (o.p.out != null) setO(o.g, 1 - seg(t, o.p.out, 0.4));
    });
    dots.forEach(o => {
      const xy = proj([o.d.lon, o.d.lat]);
      if (!xy) { vis(o.g, false); return; }
      vis(o.g, true); setT(o.g, xy[0], xy[1]);
      setO(o.g, eOut(seg(t, o.d.at || 0, 0.5)) * (o.d.out != null ? 1 - seg(t, o.d.out, 0.4) : 1));
    });
    names.forEach(o => {
      const xy = proj([o.n.lon, o.n.lat]);
      if (!xy) { vis(o.e, false); return; }
      vis(o.e, true);
      setT(o.e, xy[0] - o.e.offsetWidth / 2, xy[1] - o.e.offsetHeight / 2);
      setO(o.e, eOut(seg(t, o.n.at || 0, 0.6)) * (o.n.out != null ? 1 - seg(t, o.n.out, 0.4) : 1));
    });
    if (title) setO(title, eOut(seg(t, 0.3, 0.6)));
  };
};
