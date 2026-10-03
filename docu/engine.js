/* engine.js - the core of the documentary scene renderer.

   Every scene is a function of time alone: setupScene(spec) builds the DOM once and
   returns when every picture and font is decoded; renderFrame(t) then draws frame t
   in any order. No timers, no CSS transitions, no Math.random - render.py screenshots
   each frame, so anything not computed from t would flicker between workers.

   CFG (set by render.py before load): { kit, assets } as file:// URLs.
*/
"use strict";

const W = 1920, H = 1080;
const PAL = {
  tan: "#C9BB9C", paper: "#E8DFC9", paper2: "#F3EEE2", ink: "#1A1A1A", gray: "#8C8C8C",
  red: "#D62E1F", mustard: "#D9A441", cream: "#F2EBDD", gold: "#C99A3B",
  teal: "#123B47", deep: "#071B22", night: "#0B0B0C",
};

/* ---- math & easing ------------------------------------------------------ */
const cl = (x, a, b) => Math.max(a, Math.min(b, x));
const seg = (t, s, d) => cl((t - s) / Math.max(1e-4, d), 0, 1);
const lerp = (a, b, p) => a + (b - a) * p;
const eOut = p => 1 - Math.pow(1 - p, 3);
const eOut5 = p => 1 - Math.pow(1 - p, 5);
const eIn = p => p * p * p;
const eInOut = p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
const eSine = p => -(Math.cos(Math.PI * p) - 1) / 2;
const eBack = (p, c = 1.6) => 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2);
/* a damped spring 0 -> 1: f swings per second, z damping 0..1 */
function spring(t, f = 2.2, z = 0.45) {
  if (t <= 0) return 0;
  const w = 2 * Math.PI * f, wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
}
/* documentary camera: mostly linear drift with softened ends */
const drift = p => 0.55 * p + 0.45 * eSine(p);
function rng(seed) {
  let s = (seed >>> 0) || 7;
  return () => { s = (s * 1664525 + 1013904223) % 4294967296; return s / 4294967296; };
}

/* ---- DOM helpers ---------------------------------------------------------- */
const STAGE = document.getElementById("stage");
let WAITS = [];

function el(tag, cls, parent, style, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (style) Object.assign(e.style, style);
  if (html != null) e.innerHTML = html;
  (parent || STAGE).appendChild(e);
  return e;
}
function asset(src) {
  if (!src) return src;
  if (/^(file|data|https?):/.test(src)) return src;
  if (src.startsWith("/")) return "file://" + src;
  if (/^[A-Za-z]:[\\/]/.test(src)) return "file:///" + src.replace(/\\/g, "/");
  if (src.startsWith("kit:")) return CFG.kit + "/" + src.slice(4);
  return CFG.assets + "/" + src;
}
function pic(src, parent, style, cls) {
  const i = el("img", cls || "layer", parent, style);
  WAITS.push(new Promise(res => { i.onload = () => { i.decode().then(res, res); }; i.onerror = () => { console.warn("missing", src); res(); }; }));
  i.src = asset(src);
  return i;
}
function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
function setT(e, x, y, s = 1, r = 0) {
  const v = `translate(${x.toFixed(2)}px,${y.toFixed(2)}px) rotate(${r.toFixed(3)}deg) scale(${s.toFixed(5)})`;
  if (e._t !== v) { e.style.transform = v; e._t = v; }
}
function setO(e, o) {
  const v = o <= 0.001 ? "0" : o >= 0.999 ? "1" : o.toFixed(3);
  if (e._o !== v) { e.style.opacity = v; e._o = v; }
}
function vis(e, on) {
  const v = on ? "visible" : "hidden";
  if (e.style.visibility !== v) e.style.visibility = v;
}
function css(e, k, v) {
  if (e["_" + k] !== v) { e.style[k] = v; e["_" + k] = v; }
}

/* ---- fonts: every face in the kit, by the family names used below ----------- */
const FONTS = {
  "Anton": "Anton-Regular.ttf", "Bebas": "BebasNeue.ttf", "Oswald": "Oswald.ttf",
  "OswaldB": "Oswald-Bold.ttf", "Barlow": "BarlowCondensed-SemiBold.ttf",
  "BarlowB": "BarlowCondensed-Bold.ttf", "Garamond": "EB-Garamond.ttf",
  "GaramondI": "EB-Garamond-Italic.ttf", "DMSerif": "DMSerifDisplay.ttf",
  "Playfair": "PlayfairDisplay.ttf", "Lora": "Lora.ttf", "LoraI": "Lora-Italic.ttf",
  "Elite": "SpecialElite.ttf", "Courier": "CourierPrime.ttf", "CourierB": "CourierPrime-Bold.ttf",
  "Cinzel": "Cinzel.ttf", "Inter": "Inter-SemiBold.ttf", "InterB": "Inter-Bold.ttf",
  "InterK": "Inter-Black.ttf", "Caveat": "Caveat.ttf", "Archivo": "ArchivoBlack.ttf",
  "Stencil": "SairaStencilOne.ttf", "Mono": "SpaceMono-Bold.ttf", "Montserrat": "Montserrat-ExtraBold.ttf",
};
/* ---- themes: one engine, a different look per video ------------------------
   A theme remaps the font families the scenes use, overrides the palette and names
   the surfaces the paper scenes stand on. CFG.theme picks one; "paper" is the default. */
FONTS.Stamp = FONTS.Anton;
const THEMES = {
  paper: { fonts: {}, pal: {}, grounds: {} },
  /* forensic: a lab report / case file - graph paper, stencil stamps, cyan and amber */
  forensic: {
    fonts: {
      Anton: "Oswald-Bold.ttf", Stamp: "SairaStencilOne.ttf", Elite: "CourierPrime.ttf",
      DMSerif: "PlayfairDisplay.ttf", Garamond: "InterDisplay-Black.ttf", GaramondI: "Lora-Italic.ttf",
      Caveat: "PatrickHand.ttf",
    },
    pal: {
      mustard: "#F2B134", red: "#E5484D", gold: "#F2B134", cyan: "#3FC7D6", green: "#3DBE7A",
      ink: "#15191C", cream: "#EEF1F0",
    },
    grounds: { paper: "paper_lab.jpg", map: "paper_lab.jpg", cork: "lightbox.jpg", parchment: "paper_lab.jpg" },
  },
  /* expedition: an explorer's field journal and a courtroom - ruled journal pages, a leather
     desk, an antique parchment map, brass and oxblood, evidence tags and the scales */
  expedition: {
    fonts: {
      Anton: "BebasNeue.ttf", DMSerif: "Cinzel.ttf", Elite: "SpecialElite.ttf", GaramondI: "EB-Garamond-Italic.ttf",
    },
    pal: {
      mustard: "#C8963E", red: "#9E2B25", gold: "#C8963E", cyan: "#2F6F7E", green: "#5E8A3E",
      ink: "#241A10", cream: "#F1E6CF",
    },
    grounds: { paper: "paper_journal.jpg", map: "parchment.jpg", cork: "leather.jpg", parchment: "parchment.jpg" },
    map: {
      bg0: "#E9DCBC", bg1: "#CDB88E", sea: "rgba(118,146,146,.55)", rim: "rgba(80,55,30,.5)", grat: "rgba(90,60,30,.18)",
      land: "rgba(238,226,196,.94)", border: "rgba(90,60,30,.7)", admin: "110,80,45", hi: "158,43,37", hiA: 0.42, text: "#2A1E12",
      sub: "#4A3A26", dot: "#9E2B25", dotText: "#2A1E12", name: "rgba(60,40,20,.75)", shadow: "rgba(255,245,225,.85)",
      paper: "parchment.jpg",
    },
  },
};
/* broadcast: a breaking-news desk - LIVE bug, ticker, lower-third bars, a navy studio,
   signal red and alert yellow, heavy geometric sans type */
THEMES.broadcast = {
  fonts: {
    Anton: "Montserrat-Black.ttf", Stamp: "Montserrat-Black.ttf", DMSerif: "Poppins-Bold.ttf", Elite: "Roboto-Condensed.ttf",
    Garamond: "InterDisplay-Black.ttf", GaramondI: "Roboto-Condensed-Italic.ttf", Caveat: "PatrickHand.ttf",
    Barlow: "Roboto-Condensed.ttf", Oswald: "Montserrat-ExtraBold.ttf", OswaldB: "Montserrat-ExtraBold.ttf",
  },
  pal: {
    mustard: "#FFC21A", red: "#E10600", gold: "#FFC21A", cyan: "#1EA7FF", green: "#18C07A",
    ink: "#0B1220", cream: "#F4F6FA", navy: "#0A1730",
  },
  grounds: { paper: "studio_light.jpg", map: "studio_dark.jpg", cork: "studio_dark.jpg", parchment: "studio_light.jpg" },
  map: {
    bg0: "#10214A", bg1: "#040A1A", sea: "#081430", rim: "rgba(30,167,255,.4)", grat: "rgba(120,170,255,.08)",
    land: "#1A2C55", border: "rgba(150,195,255,.5)", admin: "140,185,255", hi: "225,6,0", hiA: 0.55, text: "#F4F6FA",
    sub: "#B9C7E0", dot: "#FFFFFF", dotText: "#DCE6F5", name: "rgba(200,215,240,.85)", shadow: "rgba(0,0,0,.8)",
  },
};
/* documentary: calm, classic long-form documentary - serif titles, thin rules, muted warm
   palette, no stamps or slams; pictures carry the story */
THEMES.documentary = {
  fonts: {
    Anton: "PlayfairDisplay.ttf", Stamp: "Oswald.ttf", DMSerif: "PlayfairDisplay.ttf", Elite: "Lora.ttf",
    Garamond: "EB-Garamond.ttf", GaramondI: "Lora-Italic.ttf", Barlow: "Inter-SemiBold.ttf", BarlowB: "Inter-Bold.ttf",
    Oswald: "Inter-SemiBold.ttf", OswaldB: "Inter-Bold.ttf", Caveat: "Lora-Italic.ttf",
  },
  pal: {
    mustard: "#D8B26E", red: "#B5523B", gold: "#D8B26E", cyan: "#7FA7B5", green: "#8DAA7B",
    ink: "#1C1A17", cream: "#F3EEE4",
  },
  grounds: { paper: "paper_tan.jpg", map: "paper_map.jpg", cork: "studio_dark.jpg", parchment: "parchment.jpg" },
  map: {
    bg0: "#23272B", bg1: "#0E1012", sea: "#171B1E", rim: "rgba(216,178,110,.25)", grat: "rgba(255,255,255,.05)",
    land: "#353A3E", border: "rgba(243,238,228,.35)", admin: "243,238,228", hi: "216,178,110", hiA: 0.45, text: "#F3EEE4",
    sub: "#CFC8BA", dot: "#F3EEE4", dotText: "#E6E0D4", name: "rgba(243,238,228,.7)", shadow: "rgba(0,0,0,.8)",
  },
};
/* almanac: a farmer's almanac / heritage field guide - slab-serif headings with a stitched
   chapter badge laid over moving footage, seed-packet place tags, quilt-frame cards, charts
   drawn on cream paper and a cream survey map. Barn red, field green, wheat, denim. */
THEMES.almanac_v1 = {
  fonts: {
    Anton: "ZillaSlab-Bold.ttf", Stamp: "ZillaSlab-Bold.ttf", DMSerif: "ZillaSlab-SemiBold.ttf", Elite: "LibreBaskerville.ttf",
    Garamond: "LibreBaskerville.ttf", GaramondI: "LibreBaskerville-Italic.ttf", Barlow: "Roboto-Condensed.ttf",
    BarlowB: "BarlowCondensed-Bold.ttf", Oswald: "Roboto-Condensed.ttf", OswaldB: "BarlowCondensed-Bold.ttf",
    Caveat: "CrimsonPro-Italic.ttf", Slab: "ZillaSlab-Bold.ttf", SlabM: "ZillaSlab-Medium.ttf",
    Bask: "LibreBaskerville.ttf", BaskI: "LibreBaskerville-Italic.ttf", Crimson: "CrimsonPro.ttf", CrimsonI: "CrimsonPro-Italic.ttf",
  },
  pal: {
    mustard: "#D4A85A", red: "#9E3A2B", gold: "#D4A85A", cyan: "#4E6E8A", green: "#5E7A44",
    ink: "#23211C", cream: "#F2EBDA", wheat: "#D4A85A", barn: "#9E3A2B", field: "#5E7A44", denim: "#4E6E8A", paperA: "#EFE6D2",
  },
  grounds: { paper: "paper_tan.jpg", map: "paper_tan.jpg", cork: "studio_dark.jpg", parchment: "parchment.jpg" },
  map: {
    bg0: "#EEE6D3", bg1: "#D9CDB2", sea: "#B9C6C4", rim: "rgba(35,33,28,.35)", grat: "rgba(35,33,28,.07)",
    land: "#E4DCC4", border: "rgba(35,33,28,.55)", admin: "35,33,28", hi: "158,58,43", hiA: 0.30, text: "#23211C",
    sub: "#4A443A", dot: "#9E3A2B", dotText: "#23211C", name: "rgba(35,33,28,.62)", shadow: "rgba(242,235,218,.95)",
    pin: "survey", route: "#23211C", hiLine: "rgba(158,58,43,A)",
  },
};
/* almanac2 ("heritage gazetteer"): the almanac's second edition - a county atlas / land-survey
   gazetteer instead of a seed catalogue. Engraved caps headings on a letterpress plate, high-contrast
   didone numerals, Garamond body, a surveyor's pencil for the notes, and a township-grid plat map with
   square section markers. Cool slate ink and oatmeal paper; ochre, oxblood, verdigris, slate. */
THEMES.almanac = {          /* updated edition; the first edition is kept as THEMES.almanac_v1 */
  fonts: {
    Anton: "PlayfairDisplay.ttf", Stamp: "Cinzel.ttf", DMSerif: "PlayfairDisplay.ttf", Elite: "EB-Garamond.ttf",
    Garamond: "EB-Garamond.ttf", GaramondI: "EB-Garamond-Italic.ttf", Barlow: "Oswald.ttf", BarlowB: "Oswald-Bold.ttf",
    Oswald: "Oswald.ttf", OswaldB: "Oswald-Bold.ttf", Caveat: "PatrickHand.ttf",
    /* the almanac aliases, re-pointed: slab -> didone, Baskerville -> Garamond */
    Slab: "PlayfairDisplay.ttf", SlabM: "DMSerifDisplay.ttf", Bask: "EB-Garamond.ttf", BaskI: "EB-Garamond-Italic.ttf",
    Crimson: "EB-Garamond.ttf", CrimsonI: "EB-Garamond-Italic.ttf",
    /* its own: engraved caps, a pencil hand and a ledger mono */
    Engr: "Cinzel.ttf", Pencil: "PatrickHand.ttf", Ledger: "CourierPrime.ttf", LedgerB: "CourierPrime-Bold.ttf",
  },
  pal: {
    mustard: "#BE8A2C", red: "#7A2F2A", gold: "#BE8A2C", cyan: "#2C4760", green: "#38655C",
    ink: "#1E2832", cream: "#E8E2D0", wheat: "#BE8A2C", barn: "#7A2F2A", field: "#38655C", denim: "#2C4760",
    ochre: "#BE8A2C", oxblood: "#7A2F2A", verdigris: "#38655C", slate: "#2C4760",
    paperA: "#E3DCC8", tagc: "#EFE9D9", subc: "#4C5663",
    paperWash: "234,228,211", paperEdge: "rgba(40,50,62,.20)",
  },
  grounds: { paper: "paper_tan.jpg", map: "paper_tan.jpg", cork: "studio_dark.jpg", parchment: "parchment.jpg" },
  map: {
    bg0: "#E6DFCB", bg1: "#CFC6AC", sea: "#A9BBBE", rim: "rgba(30,40,50,.35)", grat: "rgba(30,40,50,.06)",
    land: "#E0D8C2", border: "rgba(30,40,50,.5)", admin: "30,40,50", hi: "44,71,96", hiA: 0.22, text: "#1E2832",
    sub: "#4C5663", dot: "#7A2F2A", dotText: "#1E2832", name: "rgba(30,40,50,.6)", shadow: "rgba(232,226,208,.95)",
    pin: "plat", route: "#2C4760", hiLine: "rgba(122,47,42,A)", grid: "township",
  },
};
THEMES.almanac2 = THEMES.almanac;   /* the id the updated template was drafted under */
const THEME = THEMES[(window.CFG && CFG.theme) || "paper"] || THEMES.paper;
Object.assign(FONTS, THEME.fonts);
Object.assign(PAL, THEME.pal);
/* per-video variety (docu/variety.py): accent colours and a font pairing on top of the theme */
const VARY = (window.CFG && CFG.vary) || {};
Object.assign(FONTS, VARY.fonts || {});
Object.assign(PAL, VARY.pal || {});
if (!PAL.cyan) PAL.cyan = "#3FC7D6";
if (!PAL.green) PAL.green = "#3DBE7A";
if (!PAL.navy) PAL.navy = "#0A1730";
function ground(kind, fallback) { return THEME.grounds[kind] || fallback; }

function loadFonts() {
  const st = document.createElement("style");
  st.textContent = Object.entries(FONTS)
    .map(([n, f]) => `@font-face{font-family:'${n}';src:url('${CFG.kit}/fonts/${f}');font-display:block}`)
    .join("\n");
  document.head.appendChild(st);
  return Promise.all(Object.keys(FONTS).map(n => document.fonts.load(`40px '${n}'`).catch(() => {})));
}

/* ---- shared finishing layers ---------------------------------------------- */
function vignette(parent, strength = 0.55, inner = 45) {
  return el("div", "full", parent, {
    background: `radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) ${inner}%, rgba(0,0,0,${strength}) 100%)`,
    pointerEvents: "none",
  });
}
/* flash of white used on hard hits */
function flashLayer(parent) {
  const f = el("div", "full", parent, { background: "#fff", opacity: 0 });
  return (t, at, d = 0.18) => setO(f, t >= at ? Math.max(0, 1 - (t - at) / d) * 0.55 : 0);
}

/* ---- typography components -------------------------------------------------- */

/* A mustard label chip that wipes in (Lotus "CHECKERED FLAG" style). */
function chip(parent, text, x, y, opts = {}) {
  const size = opts.size || 30;
  const box = el("div", "abs", parent, {
    left: x + "px", top: y + "px", background: opts.bg || PAL.mustard, color: opts.color || PAL.ink,
    font: `${size}px 'OswaldB'`, letterSpacing: ".08em", padding: `${size * 0.22}px ${size * 0.5}px ${size * 0.18}px`,
    textTransform: "uppercase", whiteSpace: "nowrap", boxShadow: "0 8px 24px rgba(0,0,0,.35)",
  }, esc(text));
  const at = opts.at || 0.5;
  return t => {
    const p = eOut(seg(t, at, 0.45));
    css(box, "clipPath", `inset(0 ${((1 - p) * 100).toFixed(1)}% 0 0)`);
    vis(box, p > 0);
    if (opts.out != null) setO(box, 1 - seg(t, opts.out, 0.3));
  };
}

/* Name + role lower third with a gold rule (Lotus "JACK BRABHAM" style). */
function lowerThird(parent, name, role, opts = {}) {
  const x = opts.x || 120, y = opts.y || 850, at = opts.at || 0.6;
  const wrap = el("div", "abs", parent, { left: x + "px", top: y + "px" });
  const rule = el("div", "abs", wrap, { left: "0", top: "0", height: "4px", width: "0", background: opts.color || PAL.mustard });
  const nm = el("div", "abs", wrap, {
    left: "0", top: "18px", font: `${opts.size || 64}px 'DMSerif'`, color: "#fff", whiteSpace: "nowrap",
    textShadow: "0 4px 24px rgba(0,0,0,.7)",
  }, esc(name));
  const rl = el("div", "abs", wrap, {
    left: "2px", top: `${(opts.size || 64) + 34}px`, font: "26px 'Barlow'", letterSpacing: ".22em", color: "#E9E2D2",
    textTransform: "uppercase", whiteSpace: "nowrap", textShadow: "0 2px 12px rgba(0,0,0,.8)",
  }, esc(role || ""));
  return t => {
    const a = eOut(seg(t, at, 0.5));
    css(rule, "width", (a * (opts.rule || 90)).toFixed(1) + "px");
    const b = eOut(seg(t, at + 0.15, 0.6));
    setO(nm, b); setT(nm, 0, (1 - b) * 24);
    const c = eOut(seg(t, at + 0.35, 0.6));
    setO(rl, c); setT(rl, 0, (1 - c) * 16);
    if (opts.out != null) setO(wrap, 1 - seg(t, opts.out, 0.35));
  };
}

/* Typewriter text that types on character by character. */
function typeOn(node, text, t, at, cps = 28, cursor = true) {
  const n = Math.floor(cl((t - at) * cps, 0, text.length));
  const s = esc(text.slice(0, n)) + (cursor && n < text.length && t >= at ? "<span style='opacity:.8'>|</span>" : "");
  if (node._s !== s) { node.innerHTML = s; node._s = s; }
  return n >= text.length;
}

/* Count a number up from a to b, formatted like the target string. */
function countText(target, p) {
  const m = String(target).match(/^([^\d]*)([\d,]*\.?\d*)(.*)$/);
  if (!m || !m[2]) return String(target);
  const raw = m[2].replace(/,/g, "");
  const dec = raw.includes(".") ? raw.split(".")[1].length : 0;
  const v = parseFloat(raw) * p;
  let s = v.toFixed(dec);
  if (m[2].includes(",")) s = Number(s).toLocaleString("en-US", { minimumFractionDigits: dec, maximumFractionDigits: dec });
  return m[1] + s + m[3];
}

/* ---- the scene registry ------------------------------------------------------ */
const SCENES = {};
let UPDATE = () => {};
let READY = false;

window.setupScene = async function (spec) {
  READY = false;
  STAGE.innerHTML = "";
  WAITS = [];
  window.SCENE = spec;
  STAGE.style.background = spec.bgcolor || PAL.night;
  const make = SCENES[spec.type];
  if (!make) throw new Error("unknown scene type " + spec.type);
  const up = await make(spec, STAGE);
  const extras = (spec.overlays || []).map(o => OVERLAYS[o.type](o, STAGE));
  await Promise.all(WAITS);
  await document.fonts.ready;
  UPDATE = t => { up(t); extras.forEach(f => f(t)); };
  UPDATE(0);
  READY = true;
  return true;
};
window.renderFrame = function (t) { UPDATE(t); return true; };

SCENES.blank = async () => () => {};

/* overlays any scene can carry: chips, lower thirds, captions */
const OVERLAYS = {
  chip: (o, root) => chip(root, o.text, o.x != null ? o.x : 110, o.y != null ? o.y : 900, o),
  lower: (o, root) => lowerThird(root, o.name, o.role, o),
  caption: (o, root) => {
    const d = el("div", "abs", root, {
      left: "0", width: W + "px", top: (o.y || 940) + "px", textAlign: "center",
      font: `${o.size || 30}px 'GaramondI'`, color: "#EDE6D8", textShadow: "0 2px 14px rgba(0,0,0,.9)",
    }, esc(o.text));
    return t => { const a = seg(t, o.at || 0.4, 0.6) * (1 - seg(t, o.out || 1e9, 0.4)); setO(d, a); };
  },
  source: (o, root) => {
    const d = el("div", "abs", root, {
      right: "70px", bottom: "46px", font: "18px 'Barlow'", letterSpacing: ".2em", color: "rgba(235,228,214,.7)",
      textTransform: "uppercase", textShadow: "0 1px 8px rgba(0,0,0,.9)",
    }, esc(o.text));
    return t => setO(d, seg(t, o.at || 0.8, 0.6));
  },
  flash: (o, root) => { const f = flashLayer(root); return t => f(t, o.at || 0, o.d || 0.2); },
  fadein: (o, root) => {
    const f = el("div", "full", root, { background: o.color || "#000" });
    return t => setO(f, 1 - seg(t, 0, o.d || 0.5));
  },
  fadeout: (o, root) => {
    const f = el("div", "full", root, { background: o.color || "#000", opacity: 0 });
    return t => setO(f, seg(t, SCENE.duration - (o.d || 0.6), o.d || 0.6));
  },
};

loadFonts().then(() => { window.FONTS_READY = true; });
