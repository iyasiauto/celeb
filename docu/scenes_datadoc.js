/* scenes_datadoc.js - the "Data Documentary" template (Emerge X style 17, docu/templates/Data_Documentary).

   Big, quiet numbers drawn on near-black navy between full-frame real footage. One serif (Playfair
   Display) for what is said, one sans (Poppins) for labels and sources, one red accent.

   ddroll      a figure rolling like an odometer (0.78 -> 0.72, or 0 -> 2,600), kicker + serif sub-line
   ddticker    one enormous sum typed digit by digit
   ddbars      horizontal bars compared, the subject red, an optional dashed reference line
   dddots      100 people / units as glowing dots; a share of them lights red (80-90 of 100)
   ddstrike    2-6 words in rows; each rises in, then a red bar strikes through it (strike:false = a list)
   ddread      the thesis line: every word lights as it is spoken, the key words get a yellow box
   ddtitle     the title card: blurs in, letter-spacing opens, hairline, italic sub-line
   ddtimeline  a glowing line drawn by a pen across the years; the camera follows the pen, marks pop on
   dddoc       a real document lying on navy, tilted, pushed in, a hairline out to a note
   ddspot      a real photo: the ground darkens, loses colour and blurs around the subject as it is named
   ddphoto     a real photo of a place or object with a slow push toward its subject

   overlays (on footage): ddlabel (top-left caps label with a red rule, or a counting figure), ddtab (chapter tab)
*/
"use strict";

const DD = {
  navy: "#070E14", ink: "#F4F1EA", red: "#E0434C", redL: "#FF8A93", redH: "#FF6B76", amber: "#F2B84B",
  steel: "#8FB3D9", hl: "#F2D14A", maroon: "#260C15", black: "#030405", tab: "#0B2033", tabN: "#8FD3FF", tabT: "#E6FFFF",
};
const SERIF = "'Play'", SANS_S = "'PopS'", SANS_M = "'PopM'";

/* ---- the navy ground: soft radial lift, deterministic grain, heavy vignette ---------------- */
let _GRAIN = null;
function grainURL() {
  if (_GRAIN) return _GRAIN;
  const c = document.createElement("canvas"); c.width = c.height = 256;
  const x = c.getContext("2d"), im = x.createImageData(256, 256), r = rng(4711);
  for (let i = 0; i < im.data.length; i += 4) {
    const v = Math.floor(r() * 255);
    im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255;
  }
  x.putImageData(im, 0, 0);
  _GRAIN = c.toDataURL("image/png");
  return _GRAIN;
}
function ddGround(root, color) {
  root.style.background = color || DD.navy;
  el("div", "full", root, { background: "radial-gradient(ellipse at 50% 45%, rgba(40,60,80,.22) 0%, rgba(0,0,0,0) 60%)" });
  const cam = el("div", "full", root, { transformOrigin: "50% 50%" });
  const g = el("div", "full", root, {
    backgroundImage: `url(${grainURL()})`, backgroundSize: "256px 256px", mixBlendMode: "overlay", opacity: 0.3,
    pointerEvents: "none",
  });
  el("div", "full", root, {
    background: "radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,.72) 100%)", pointerEvents: "none",
  });
  const gr = rng(99);
  const offs = Array.from({ length: 64 }, () => [Math.floor(gr() * 256), Math.floor(gr() * 256)]);
  return {
    cam,
    tick(t) {                                       /* grain moves every frame, but only from t */
      const o = offs[Math.floor(t * 30) % offs.length];
      css(g, "backgroundPosition", `${o[0]}px ${o[1]}px`);
    },
  };
}
/* the caps title top-left (types on) and the source line bottom-left */
function ddChrome(parent, s) {
  const out = {};
  if (s.title) out.title = el("div", "abs", parent, {
    left: "120px", top: "92px", font: `600 24px ${SANS_S}`, letterSpacing: ".2em", textTransform: "uppercase",
    color: "rgba(244,241,234,.72)", whiteSpace: "nowrap",
  });
  if (s.source) out.source = el("div", "abs", parent, {
    left: "120px", bottom: "54px", font: `500 19px ${SANS_M}`, letterSpacing: ".08em", textTransform: "uppercase",
    color: "rgba(244,241,234,.42)", whiteSpace: "nowrap",
  }, esc(s.source));
  return t => {
    if (out.title) typeOn(out.title, String(s.title).toUpperCase(), t, s.titleAt != null ? s.titleAt : 0.15, 30, false);
    if (out.source) setO(out.source, seg(t, s.sourceAt != null ? s.sourceAt : 0.4, 0.4));
  };
}
/* words leave in the last 0.5 s; the ground stays */
function ddOut(s, t) { return 1 - eInOut(seg(t, s.duration - 0.55, 0.5)); }
function ddPush(cam, s, t, amt) {
  const p = cl(t / s.duration, 0, 1);
  setT(cam, 0, 0, 1 + amt * p);
}
function textWidth(txt, font) {
  const c = textWidth._c || (textWidth._c = document.createElement("canvas").getContext("2d"));
  c.font = font;
  return c.measureText(txt).width;
}

/* ---- ddroll: the odometer ---------------------------------------------------------------- */
SCENES.ddroll = async (s, root) => {
  const G = ddGround(root, s.ground);
  const chrome = ddChrome(G.cam, s);
  const size = s.size || (String(s.value).length > 7 ? 240 : 300);
  const box = el("div", "abs", G.cam, { left: 0, width: W + "px", top: (s.y || 330) + "px", textAlign: "center" });
  const kick = el("div", "", box, {
    font: `600 25px ${SANS_S}`, letterSpacing: ".23em", textTransform: "uppercase", color: "rgba(255,255,255,.61)", height: "40px",
  });
  const kA = el("span", "", kick, {}, esc(s.kickerFrom || s.kicker || ""));
  const kB = el("span", "abs", kick, { left: 0, width: W + "px", opacity: 0 }, esc(s.kicker || ""));
  const num = el("div", "", box, {
    font: `400 ${size}px ${SERIF}`, lineHeight: "1", height: size * 1.12 + "px", color: "#fff", whiteSpace: "nowrap",
    fontVariantNumeric: "lining-nums tabular-nums", display: "inline-flex", alignItems: "flex-start", marginTop: "18px",
    textShadow: "0 0 40px rgba(255,255,255,.18)",
  });
  const sub = el("div", "", box, { font: `400 42px ${SERIF}`, color: "rgba(255,255,255,.8)", marginTop: "10px" }, esc(s.sub || ""));
  /* one column per character: digits roll, everything else sits still */
  const to = String(s.value), from = s.from != null ? String(s.from) : null;
  const fromPad = from ? from.padStart(to.length, " ") : null;
  const lh = size * 1.12, cols = [];
  const nDig = to.replace(/\D/g, "").length;
  let dIdx = 0;
  for (let i = 0; i < to.length; i++) {
    const ch = to[i];
    if (/\d/.test(ch)) {
      const wrap = el("span", "", num, { display: "inline-block", height: lh + "px", overflow: "hidden", position: "relative", width: "0.62em", textAlign: "center" });
      const strip = el("span", "", wrap, { position: "absolute", left: 0, top: 0, width: "100%", display: "block" });
      strip.innerHTML = Array.from({ length: 40 }, (_, k) => `<div style="height:${lh}px;line-height:${lh}px">${k % 10}</div>`).join("");
      const d = +ch;
      let s0 = 0;
      if (fromPad && /\d/.test(fromPad[i])) s0 = +fromPad[i];
      const change = from ? (fromPad[i] !== ch) : true;
      const spins = from ? 0 : Math.min(2, Math.max(0, nDig - 1 - dIdx) > 0 ? 1 : 2);
      const span = from ? ((d - s0 + 10) % 10) : (d + 10 * spins);
      cols.push({ strip, s0, span, change, i: dIdx });
      dIdx++;
    } else {
      el("span", "", num, { display: "inline-block", height: lh + "px", lineHeight: lh + "px" }, esc(ch));
    }
  }
  const at = s.at != null ? s.at : 0.3, dur = s.rollFor || Math.min(1.8, s.duration * 0.42);
  return t => {
    G.tick(t); ddPush(G.cam, s, t, s.push != null ? s.push : 0.05); chrome(t);
    const o = ddOut(s, t);
    setO(box, Math.min(o, eOut(seg(t, 0.05, 0.35))));
    if (s.kickerFrom) {
      const k = seg(t, at + dur * 0.5, 0.3);
      setO(kA, 1 - k); setO(kB, k);
    }
    setO(sub, eOut(seg(t, at + dur * 0.6, 0.6)));
    let landed = true;
    cols.forEach(c => {
      const st = at + c.i * 0.04;
      const p = c.change ? eOut(seg(t, st, dur)) : 1;
      if (p < 1) landed = false;
      const v = c.s0 + c.span * p;
      setT(c.strip, 0, -v * lh);
    });
    const hot = s.hot && landed && t > at + dur;
    css(num, "color", hot ? DD.redH : "#fff");
  };
};

/* ---- ddticker: one enormous sum, typed ------------------------------------------------------ */
SCENES.ddticker = async (s, root) => {
  const G = ddGround(root, s.ground);
  const chrome = ddChrome(G.cam, s);
  const v = String(s.value);
  const size = s.size || (v.length <= 10 ? 190 : v.length <= 16 ? 160 : 132);
  const box = el("div", "abs", G.cam, { left: 0, width: W + "px", top: (s.y || 360) + "px", textAlign: "center" });
  const kick = el("div", "", box, {
    font: `600 25px ${SANS_S}`, letterSpacing: ".23em", textTransform: "uppercase", color: "rgba(255,255,255,.6)",
  }, esc(s.kicker || ""));
  const num = el("div", "", box, {
    font: `400 ${size}px ${SERIF}`, color: "#fff", whiteSpace: "nowrap", marginTop: "16px", height: size * 1.15 + "px",
    fontVariantNumeric: "lining-nums", textShadow: "0 0 30px rgba(255,255,255,.18)",
  });
  const sub = el("div", "", box, { font: `400 42px ${SERIF}`, color: "rgba(255,255,255,.8)", marginTop: "8px" }, esc(s.sub || ""));
  const at = s.at != null ? s.at : 0.35, cps = Math.max(8, v.length / Math.max(0.6, s.duration * 0.45 - at));
  return t => {
    G.tick(t); ddPush(G.cam, s, t, 0.05); chrome(t);
    const o = ddOut(s, t);
    setO(box, o);
    setO(kick, eOut(seg(t, 0.1, 0.4)));
    const n = Math.floor(cl((t - at) * cps, 0, v.length));
    const last = n > 0 ? v.slice(n - 1, n) : "";
    const drop = n > 0 ? (1 - eOut(seg(t, at + (n - 1) / cps, 0.12))) * -10 : 0;
    const html = esc(v.slice(0, Math.max(0, n - 1))) + (last ? `<span style="display:inline-block;transform:translateY(${drop.toFixed(1)}px)">${esc(last)}</span>` : "");
    if (num._s !== html) { num.innerHTML = html; num._s = html; }
    css(num, "color", s.hot && n >= v.length ? DD.redH : "#fff");
    setO(sub, eOut(seg(t, at + v.length / cps + 0.1, 0.5)));
  };
};

/* ---- ddbars: things compared ---------------------------------------------------------------- */
SCENES.ddbars = async (s, root) => {
  const G = ddGround(root, s.ground);
  const chrome = ddChrome(G.cam, s);
  const rows = s.rows || [], n = rows.length;
  const max = s.max || Math.max(...rows.map(r => +r.value || 0)) * 1.08;
  const x0 = 700, wMax = 1000, rh = Math.min(120, 600 / Math.max(1, n)), y0 = 540 - (n * rh) / 2 + 20;
  const items = rows.map((r, i) => {
    const y = y0 + i * rh;
    const lab = el("div", "abs", G.cam, {
      left: "100px", width: x0 - 140 + "px", top: y + "px", height: rh * 0.6 + "px", lineHeight: rh * 0.6 + "px", textAlign: "right",
      font: `400 ${r.hi ? 40 : 36}px ${SERIF}`, color: r.hi ? "#fff" : "rgba(255,255,255,.82)", whiteSpace: "nowrap",
    }, esc(r.label));
    const bar = el("div", "abs", G.cam, {
      left: x0 + "px", top: y + rh * 0.12 + "px", height: rh * 0.36 + "px", width: "0px", borderRadius: "2px",
      background: r.hi ? DD.red : "linear-gradient(90deg, rgba(255,255,255,.55), rgba(255,255,255,.9))",
      boxShadow: r.hi ? "0 0 22px rgba(224,67,76,.55)" : "0 0 16px rgba(255,255,255,.18)",
    });
    const val = el("div", "abs", G.cam, {
      left: x0 + "px", top: y + "px", height: rh * 0.6 + "px", lineHeight: rh * 0.6 + "px", font: `500 30px ${SANS_M}`,
      color: r.hi ? DD.redL : "rgba(255,255,255,.75)", whiteSpace: "nowrap", opacity: 0,
    }, esc(r.text || String(r.value)));
    return { r, lab, bar, val, w: wMax * cl((+r.value || 0) / max, 0, 1), at: r.at != null ? r.at : 0.5 + i * 0.35 };
  });
  let ref = null;
  if (s.ref) {
    const rx = x0 + wMax * cl(s.ref.value / max, 0, 1);
    ref = {
      line: el("div", "abs", G.cam, { left: rx + "px", top: y0 - 50 + "px", width: "0", height: n * rh + 60 + "px", borderLeft: "2.5px dashed rgba(255,255,255,.72)", clipPath: "inset(0 0 100% 0)" }),
      lab: el("div", "abs", G.cam, { left: rx + 12 + "px", top: y0 - 62 + "px", font: `600 21px ${SANS_S}`, letterSpacing: ".16em", textTransform: "uppercase", color: "rgba(255,255,255,.62)", whiteSpace: "nowrap" }),
      at: s.ref.at != null ? s.ref.at : 1.2,
    };
  }
  return t => {
    G.tick(t); ddPush(G.cam, s, t, 0.04); chrome(t);
    const o = ddOut(s, t);
    items.forEach(it => {
      const a = eOut(seg(t, it.at - 0.2, 0.35));
      setO(it.lab, a * o);
      const p = eOut(seg(t, it.at, 0.9));
      css(it.bar, "width", (it.w * p).toFixed(1) + "px");
      setO(it.bar, o);
      setT(it.val, it.w * p + 18, 0);
      setO(it.val, eOut(seg(t, it.at + 0.6, 0.4)) * o);
    });
    if (ref) {
      const p = eOut(seg(t, ref.at, 1.0));
      css(ref.line, "clipPath", `inset(0 0 ${((1 - p) * 100).toFixed(1)}% 0)`);
      setO(ref.line, o);
      typeOn(ref.lab, String(s.ref.label || "").toUpperCase(), t, ref.at + 0.4, 26, false);
      setO(ref.lab, o);
    }
  };
};

/* ---- dddots: a share of 100 ------------------------------------------------------------------- */
SCENES.dddots = async (s, root) => {
  const G = ddGround(root, s.ground);
  const chrome = ddChrome(G.cam, s);
  const total = s.total || 100, cols = s.cols || 20, rowsN = Math.ceil(total / cols);
  const lo = s.lit != null ? s.lit : 0, hi = s.litTo != null ? s.litTo : lo;
  const gap = 46, gx = s.big ? 0 : 860, gw = (cols - 1) * gap, gh = (rowsN - 1) * gap;
  const left = s.big ? (W - gw) / 2 : gx, top = s.big ? 330 : 540 - gh / 2 + 10;
  const dots = [];
  for (let i = 0; i < total; i++) {
    const c = i % cols, r = Math.floor(i / cols);
    const d = el("div", "abs", G.cam, {
      left: left + c * gap - 9 + "px", top: top + r * gap - 9 + "px", width: "18px", height: "18px", borderRadius: "50%",
      background: "rgba(255,255,255,.85)", boxShadow: "0 0 10px rgba(255,255,255,.35)", opacity: 0,
    });
    dots.push(d);
  }
  const txt = s.big ? null : el("div", "abs", G.cam, { left: "150px", top: "330px", width: "640px" });
  const kick = txt && el("div", "", txt, { font: `600 24px ${SANS_S}`, letterSpacing: ".22em", textTransform: "uppercase", color: "rgba(255,255,255,.6)" }, esc(s.kicker || ""));
  const big = txt && el("div", "", txt, { font: `400 ${s.size || 170}px ${SERIF}`, color: "#fff", lineHeight: "1.05", marginTop: "14px", whiteSpace: "nowrap", fontVariantNumeric: "lining-nums", textShadow: "0 0 30px rgba(255,255,255,.15)" }, esc(s.value || ""));
  const sub = txt && el("div", "", txt, { font: `400 40px ${SERIF}`, color: "rgba(255,255,255,.8)", marginTop: "12px", lineHeight: "1.25" }, esc(s.sub || ""));
  const at = s.at != null ? s.at : 0.3, litAt = s.litAt != null ? s.litAt : at + 1.0;
  return t => {
    G.tick(t); ddPush(G.cam, s, t, 0.04); chrome(t);
    const o = ddOut(s, t);
    dots.forEach((d, i) => {
      const r = Math.floor(i / cols);
      const a = eOut(seg(t, at + r * 0.08 + (i % cols) * 0.008, 0.3));
      const isLit = i < hi;
      const lp = isLit ? eOut(seg(t, litAt + (i / Math.max(1, hi)) * 1.0, 0.25)) : 0;
      const partial = i >= lo && i < hi;
      const col = lp > 0 ? (partial ? `rgba(224,67,76,${(0.45 + 0.2 * lp).toFixed(2)})` : DD.red) : "rgba(255,255,255,.85)";
      css(d, "background", col);
      css(d, "boxShadow", lp > 0 ? `0 0 ${partial ? 6 : 14}px rgba(224,67,76,.6)` : "0 0 10px rgba(255,255,255,.3)");
      setO(d, a * o * (lp > 0 || !s.dimRest ? 1 : 1 - 0.55 * seg(t, litAt + 1.0, 0.6)));
    });
    if (txt) {
      setO(kick, eOut(seg(t, 0.15, 0.4)) * o);
      setO(big, eOut(seg(t, litAt + 0.4, 0.5)) * o);
      setT(big, 0, (1 - eOut(seg(t, litAt + 0.4, 0.5))) * 16);
      setO(sub, eOut(seg(t, litAt + 0.9, 0.5)) * o);
    }
  };
};

/* ---- ddstrike: words struck through (or simply listed) -------------------------------------- */
SCENES.ddstrike = async (s, root) => {
  const G = ddGround(root, s.ground);
  const chrome = ddChrome(G.cam, s);
  const items = s.items || [];
  const size = s.size || (items.length > 4 ? 64 : 84);
  const head = s.head ? el("div", "abs", G.cam, {
    left: 0, width: W + "px", top: (s.headY || 250) + "px", textAlign: "center", font: `400 46px 'PlayI'`, color: "rgba(255,255,255,.75)",
  }, esc(s.head)) : null;
  /* lay the words out in centred rows no wider than 1500 px */
  const font = `400 ${size}px ${SERIF}`, gap = 90, maxW = 1500;
  const ws = items.map(it => textWidth(it.text, font));
  const rows = [[]]; let rw = 0;
  items.forEach((it, i) => {
    const w = ws[i];
    if (rows[rows.length - 1].length && (rw + gap + w > maxW || (s.perRow && rows[rows.length - 1].length >= s.perRow))) { rows.push([]); rw = 0; }
    rows[rows.length - 1].push(i); rw += (rw ? gap : 0) + w;
  });
  const lineH = size * 1.55, top0 = (s.y || 540) - (rows.length * lineH) / 2 + (head ? 40 : 0);
  const nodes = [];
  rows.forEach((r, ri) => {
    const tw = r.reduce((a, i) => a + ws[i], 0) + gap * (r.length - 1);
    let x = (W - tw) / 2;
    r.forEach(i => {
      const it = items[i];
      const n = el("div", "abs", G.cam, { left: x + "px", top: top0 + ri * lineH + "px", font, color: it.hot ? DD.redH : "#fff", whiteSpace: "nowrap" }, esc(it.text));
      const bar = el("div", "abs", G.cam, {
        left: x - 6 + "px", top: top0 + ri * lineH + size * 0.62 + "px", width: ws[i] + 12 + "px", height: "9px", background: DD.red,
        boxShadow: "0 0 18px rgba(224,67,76,.55)", transformOrigin: "0 50%", transform: "scaleX(0)",
      });
      nodes.push({ it, n, bar, at: it.at != null ? it.at : 0.4 + i * 0.6 });
      x += ws[i] + gap;
    });
  });
  return t => {
    G.tick(t); ddPush(G.cam, s, t, 0.05); chrome(t);
    const o = ddOut(s, t);
    if (head) setO(head, eOut(seg(t, 0.1, 0.5)) * o);
    nodes.forEach(nd => {
      const a = eOut(seg(t, nd.at, 0.45));
      const st = nd.it.strike === false || s.strike === false ? null : (nd.it.strikeAt != null ? nd.it.strikeAt : nd.at + 0.55);
      const sp = st == null ? 0 : eOut(seg(t, st, 0.32));
      setT(nd.n, 0, (1 - a) * 26);
      setO(nd.n, a * o * (1 - 0.55 * sp));
      css(nd.bar, "transform", `scaleX(${sp.toFixed(3)})`);
      setO(nd.bar, o);
    });
  };
};

/* ---- ddread: the thesis line ------------------------------------------------------------------ */
SCENES.ddread = async (s, root) => {
  const G = ddGround(root, s.ground);
  const words = String(s.text).split(/\s+/);
  const keys = new Set((s.key || "").toLowerCase().split(/\s+/).filter(Boolean));
  const box = el("div", "abs", G.cam, {
    left: (W - 1500) / 2 + "px", width: "1500px", top: "0", textAlign: "center", font: `400 ${s.size || 76}px ${SERIF}`,
    lineHeight: "1.32", color: "#fff",
  });
  const spans = words.map((w, i) => {
    const sp = el("span", "", box, { position: "relative", display: "inline-block", marginRight: ".26em", zIndex: 1 });
    const clean = w.toLowerCase().replace(/[^a-z0-9'’]/g, "");
    const isKey = keys.has(clean);
    let bg = null;
    if (isKey) bg = el("span", "abs", sp, { left: "-.08em", right: "-.08em", top: ".12em", bottom: ".02em", background: s.hot ? DD.red : DD.hl, zIndex: -1, transformOrigin: "0 50%", transform: "scaleX(0)" });
    el("span", "", sp, { position: "relative" }, esc(w));
    return { sp, isKey, bg, txt: sp.lastChild };
  });
  await document.fonts.ready;
  const hgt = box.getBoundingClientRect().height;
  css(box, "top", (540 - hgt / 2) + "px");
  const a0 = s.at != null ? s.at : 0.2, a1 = s.end != null ? s.end : Math.max(a0 + 0.8, s.duration * 0.6);
  const keyAt = s.keyAt != null ? s.keyAt : a1;
  /* where the key words sit, for the push in */
  let kx = W / 2, ky = 540;
  const ks = spans.filter(x => x.isKey);
  if (ks.length) {
    const r0 = ks[0].sp.getBoundingClientRect(), r1 = ks[ks.length - 1].sp.getBoundingClientRect();
    kx = (r0.left + r1.right) / 2; ky = (r0.top + r1.bottom) / 2;
  }
  return t => {
    G.tick(t);
    const o = ddOut(s, t);
    const n = words.length;
    spans.forEach((x, i) => {
      const wt = a0 + (a1 - a0) * (i / n);
      const lit = eOut(seg(t, wt, 0.25));
      setO(x.sp, (0.18 + 0.82 * lit) * o);
      if (x.bg) css(x.bg, "transform", `scaleX(${eOut(seg(t, keyAt, 0.4)).toFixed(3)})`);
      if (x.isKey) css(x.txt, "color", seg(t, keyAt, 0.4) > 0.5 && !s.hot ? "#111" : "#fff");
    });
    const base = 1 + 0.03 * cl(t / s.duration, 0, 1);
    const pz = eInOut(seg(t, keyAt + 0.3, Math.max(0.6, s.duration - keyAt - 0.6)));
    const sc = base * (1 + 0.35 * pz);
    const tx = (W / 2 - kx) * pz * sc, ty = (540 - ky) * pz * sc;
    css(G.cam, "transformOrigin", `${kx}px ${ky}px`);
    setT(G.cam, (W / 2 - kx) * pz, (540 - ky) * pz, sc);
  };
};

/* ---- ddtitle: the title card ------------------------------------------------------------------ */
SCENES.ddtitle = async (s, root) => {
  root.style.background = DD.black;
  const G = ddGround(root, DD.black);
  const t1 = el("div", "abs", G.cam, { left: 0, width: W + "px", top: (s.y || 440) + "px", textAlign: "center", font: `400 ${s.size || 104}px ${SERIF}`, color: DD.ink, whiteSpace: "nowrap" }, esc(s.text));
  const rule = el("div", "abs", G.cam, { left: W / 2 + "px", top: (s.y || 440) + (s.size || 104) * 1.45 + "px", height: "1.5px", width: "0", background: "rgba(244,241,234,.7)" });
  const sub = el("div", "abs", G.cam, { left: 0, width: W + "px", top: (s.y || 440) + (s.size || 104) * 1.45 + 34 + "px", textAlign: "center", font: `400 34px 'PlayI'`, color: "rgba(244,241,234,.66)" }, esc(s.sub || ""));
  const D = s.duration;
  return t => {
    G.tick(t);
    const a = eOut(seg(t, 0.25, 1.2));
    setO(t1, a); css(t1, "filter", `blur(${((1 - a) * 6).toFixed(2)}px)`);
    css(t1, "letterSpacing", lerp(0.04, 0.14, cl(t / D, 0, 1)).toFixed(4) + "em");
    const w = eInOut(seg(t, 0.9, 0.9)) * 300;
    css(rule, "width", w.toFixed(1) + "px"); css(rule, "left", (W / 2 - w / 2).toFixed(1) + "px");
    setO(sub, eOut(seg(t, 1.3, 0.6)));
    const f = Math.min(seg(t, 0, 0.5), 1 - seg(t, D - 0.5, 0.5));
    setO(G.cam, f);
  };
};

/* ---- ddtimeline: the pen draws the years ---------------------------------------------------- */
SCENES.ddtimeline = async (s, root) => {
  const G = ddGround(root, s.ground);
  const marks = s.marks || [];
  const y0 = s.from, y1 = s.to;
  const X0 = 160, X1 = W - 160, LY = 640;
  const px = y => X0 + (X1 - X0) * (y - y0) / (y1 - y0);
  const chart = el("div", "full", G.cam, { transformOrigin: "0 0" });
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("width", W); svg.setAttribute("height", H); svg.style.position = "absolute"; svg.style.left = "0"; svg.style.top = "0";
  chart.appendChild(svg);
  /* faint grid + axis years */
  const step = s.step || 10;
  for (let y = Math.ceil(y0 / step) * step; y <= y1; y += step) {
    const gl = document.createElementNS(NS, "line");
    gl.setAttribute("x1", px(y)); gl.setAttribute("x2", px(y)); gl.setAttribute("y1", 230); gl.setAttribute("y2", LY + 40);
    gl.setAttribute("stroke", "rgba(255,255,255,.075)"); gl.setAttribute("stroke-width", "1.5");
    svg.appendChild(gl);
    if ((y - Math.ceil(y0 / step) * step) % (s.labelEvery || step * 2) === 0)
      el("div", "abs", chart, { left: px(y) - 60 + "px", width: "120px", top: LY + 58 + "px", textAlign: "center", font: `500 22px ${SANS_M}`, color: "rgba(255,255,255,.42)" }, String(y));
  }
  const axis = document.createElementNS(NS, "line");
  axis.setAttribute("x1", X0); axis.setAttribute("x2", X1); axis.setAttribute("y1", LY + 40); axis.setAttribute("y2", LY + 40);
  axis.setAttribute("stroke", "rgba(255,255,255,.3)"); axis.setAttribute("stroke-width", "2"); svg.appendChild(axis);
  /* the line: a gentle path through the marks' heights (lv 0..1 above the axis) */
  const pts = [[y0, s.startLevel != null ? s.startLevel : 0.2]].concat(marks.map(m => [m.year, m.level != null ? m.level : 0.5])).concat([[y1, s.endLevel != null ? s.endLevel : 0.6]]);
  const YY = lv => LY - 320 * lv;
  const glow = document.createElementNS(NS, "path"), line = document.createElementNS(NS, "path");
  let d = `M ${px(pts[0][0])} ${YY(pts[0][1])}`;
  for (let i = 1; i < pts.length; i++) {
    const [ax, ay] = [px(pts[i - 1][0]), YY(pts[i - 1][1])], [bx, by] = [px(pts[i][0]), YY(pts[i][1])];
    const mx = (ax + bx) / 2;
    d += ` C ${mx} ${ay} ${mx} ${by} ${bx} ${by}`;
  }
  [glow, line].forEach(p => { p.setAttribute("d", d); p.setAttribute("fill", "none"); p.setAttribute("stroke", "#fff"); p.setAttribute("stroke-linecap", "round"); svg.appendChild(p); });
  glow.setAttribute("stroke-width", "10"); glow.setAttribute("opacity", ".45"); glow.style.filter = "blur(8px)";
  line.setAttribute("stroke-width", "4");
  const L = line.getTotalLength();
  [glow, line].forEach(p => { p.setAttribute("stroke-dasharray", `${L} ${L}`); });
  const pen = el("div", "abs", chart, { left: "-4px", top: "-4px", width: "8px", height: "8px", borderRadius: "50%", background: "#fff", boxShadow: "0 0 0 6px rgba(255,255,255,.22), 0 0 20px rgba(255,255,255,.5)" });
  const penY = el("div", "abs", chart, { font: `400 58px ${SERIF}`, color: "#fff", whiteSpace: "nowrap" });
  const wm = el("div", "abs", G.cam, { right: "60px", bottom: "-70px", font: `400 420px ${SERIF}`, color: "rgba(255,255,255,.04)", lineHeight: "1" });
  const title = el("div", "abs", root, { left: "120px", top: "92px", font: `600 24px ${SANS_S}`, letterSpacing: ".2em", color: "rgba(244,241,234,.72)", whiteSpace: "nowrap" });
  const src = s.source ? el("div", "abs", root, { left: "120px", bottom: "54px", font: `500 19px ${SANS_M}`, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(244,241,234,.42)" }, esc(s.source)) : null;
  /* where along the path is a given year (binary search on length) */
  function lenAtX(x) {
    let a = 0, b = L;
    for (let k = 0; k < 22; k++) { const m = (a + b) / 2; if (line.getPointAtLength(m).x < x) a = m; else b = m; }
    return (a + b) / 2;
  }
  const mk = marks.map((m, i) => {
    const l = lenAtX(px(m.year)), p = line.getPointAtLength(l);
    const last = i === marks.length - 1 || m.hot;
    const dot = el("div", "abs", chart, { left: p.x - 7 + "px", top: p.y - 7 + "px", width: "14px", height: "14px", borderRadius: "50%", background: last ? DD.redL : "#fff", border: "2px solid #070E14", opacity: 0 });
    const bl = !!m.below, sh = m.stem || 100;
    const stem = el("div", "abs", chart, { left: p.x - 0.75 + "px", top: (bl ? p.y + 10 : p.y - 10 - sh) + "px", width: "1.5px", height: sh + "px", background: "rgba(255,255,255,.55)", transformOrigin: bl ? "50% 0" : "50% 100%", transform: "scaleY(0)" });
    const lab = el("div", "abs", chart, { left: p.x + (m.side === "left" ? -560 : 16) + "px", width: "540px", top: (bl ? p.y + sh - 40 : p.y - sh - 50) + "px", textAlign: m.side === "left" ? "right" : "left" });
    const k = el("div", "", lab, { font: `600 21px ${SANS_S}`, letterSpacing: ".16em", color: last ? DD.redL : "rgba(255,255,255,.62)", whiteSpace: "nowrap" });
    const v = el("div", "", lab, { font: `400 ${m.size || 44}px ${SERIF}`, color: "#fff", whiteSpace: "nowrap", marginTop: "4px" });
    return { m, l, p, dot, stem, k, v };
  });
  const D = s.duration, drawEnd = s.drawEnd != null ? s.drawEnd : D - 1.9, pullAt = drawEnd + 0.1;
  const Z = 1.35;
  /* the pen's schedule: straight through, or arriving at each mark on its own cue (mark.at) */
  const keys = [[0.35, 0]];
  mk.forEach(o => { if (typeof o.m.at === "number" && o.m.at > keys[keys.length - 1][0] + 0.2 && o.m.at < drawEnd) keys.push([o.m.at, o.l]); });
  keys.push([drawEnd, L]);
  function penLen(t) {
    if (t <= keys[0][0]) return 0;
    for (let i = 1; i < keys.length; i++) {
      if (t <= keys[i][0]) {
        const p = (t - keys[i - 1][0]) / (keys[i][0] - keys[i - 1][0]);
        return lerp(keys[i - 1][1], keys[i][1], keys.length > 2 ? eInOut(p) : p);
      }
    }
    return L;
  }
  function penTime(l) {
    for (let i = 1; i < keys.length; i++) if (l <= keys[i][1] + 0.01) {
      const span = keys[i][1] - keys[i - 1][1];
      if (span <= 0) return keys[i][0];
      return keys[i - 1][0] + (keys[i][0] - keys[i - 1][0]) * ((l - keys[i - 1][1]) / span);
    }
    return drawEnd;
  }
  return t => {
    G.tick(t);
    typeOn(title, String(s.title || "").toUpperCase(), t, 0.15, 30, false);
    if (src) setO(src, seg(t, 0.5, 0.4));
    const pl = penLen(t), pd = pl / L;
    [glow, line].forEach(p => p.setAttribute("stroke-dashoffset", (L - pl).toFixed(1)));
    const pp = line.getPointAtLength(Math.max(0.01, pl));
    setT(pen, pp.x, pp.y);
    const yr = Math.round(y0 + (y1 - y0) * cl((pp.x - X0) / (X1 - X0), 0, 1));
    penY.innerHTML = `<div style="font:600 22px ${SANS_S};letter-spacing:.16em;color:rgba(255,255,255,.6)">${yr}</div>`;
    setT(penY, pp.x + 24, pp.y - 30);
    setO(penY, pd > 0 && pd < 0.995 ? 1 : 0);
    wm.textContent = String(yr);
    mk.forEach(o => {
      const hit = pl >= o.l;
      const ht = penTime(o.l);                             /* when the pen reaches it: a function of t only */
      const a = hit ? eOut(seg(t, ht, 0.25)) : 0;
      setO(o.dot, a);
      css(o.stem, "transform", `scaleY(${a.toFixed(3)})`);
      if (hit) { typeOn(o.k, String(o.m.kicker || o.m.year).toUpperCase(), t, ht + 0.1, 28, false); typeOn(o.v, o.m.value || "", t, ht + 0.25, 26, false); }
      else { o.k.innerHTML = ""; o.v.innerHTML = ""; o.k._s = ""; o.v._s = ""; }
    });
    /* the camera: 1.35x following the pen, then a pull-out to the whole line */
    const follow = eInOut(seg(t, 0.35, 1.6));
    const out = eInOut(seg(t, pullAt, 1.3));
    const z = lerp(1, lerp(1, Z, follow), 1 - out);
    const cx = lerp(W / 2, pp.x, follow * (1 - out)), cy = lerp(540, pp.y, follow * (1 - out) * 0.6);
    const tx = W / 2 - cx * z, ty = 540 - cy * z;
    const ctx = cl(tx, W - W * z, 0), cty = cl(ty, H - H * z, 0);
    setT(chart, ctx, cty, z);
    const o = ddOut(s, t);
    setO(title, o); mk.forEach(m => { setO(m.k.parentNode, o); });
  };
};

/* ---- dddoc: the real document on the table ---------------------------------------------------- */
SCENES.dddoc = async (s, root) => {
  const G = ddGround(root, s.ground);
  const wrap = el("div", "abs", G.cam, { left: 0, top: 0, width: W + "px", height: H + "px", transformOrigin: "50% 50%" });
  const iw = s.w || 1100;
  const im = pic(s.img, wrap, {
    position: "absolute", left: (s.x != null ? s.x : (W - iw) / 2 - 140) + "px", top: (s.y != null ? s.y : 110) + "px", width: iw + "px", height: "auto",
    transform: "rotate(-1.3deg)", boxShadow: "0 30px 80px rgba(0,0,0,.6), 0 6px 18px rgba(0,0,0,.45)",
    filter: "contrast(1.04) saturate(.92)",
  }, "abs");
  const dot = s.note ? el("div", "abs", wrap, { left: s.note.x - 7 + "px", top: s.note.y - 7 + "px", width: "14px", height: "14px", borderRadius: "50%", background: "#fff", boxShadow: "0 0 0 5px rgba(255,255,255,.25)", opacity: 0 }) : null;
  const hair = s.note ? el("div", "abs", wrap, { left: s.note.x + "px", top: s.note.y + "px", height: "1.5px", width: "0", background: "rgba(255,255,255,.8)" }) : null;
  const nb = s.note ? el("div", "abs", wrap, { left: (s.note.tx || 1380) + "px", top: s.note.y - 40 + "px", width: "480px" }) : null;
  const nv = nb && el("div", "", nb, { font: `400 48px ${SERIF}`, color: "#fff", lineHeight: "1.15" }, esc(s.note.text || ""));
  const ns = nb && el("div", "", nb, { font: `600 20px ${SANS_S}`, letterSpacing: ".16em", textTransform: "uppercase", color: "rgba(255,255,255,.6)", marginTop: "10px" }, esc(s.note.sub || ""));
  const chrome = ddChrome(root, s);
  const D = s.duration, na = s.note && s.note.at != null ? s.note.at : D * 0.25;
  return t => {
    G.tick(t); chrome(t);
    setT(wrap, 0, 0, lerp(0.94, 1.14, cl(t / D, 0, 1)));
    if (s.note) {
      setO(dot, eOut(seg(t, na, 0.25)));
      const hw = (s.note.tx || 1380) - s.note.x - 20;
      css(hair, "width", (eOut(seg(t, na + 0.15, 0.5)) * hw).toFixed(1) + "px");
      const o = ddOut(s, t);
      setO(nb, eOut(seg(t, na + 0.5, 0.4)) * o); setO(dot, eOut(seg(t, na, 0.25)) * o); setO(hair, o);
    }
  };
};

/* ---- ddspot / ddphoto: real photographs -------------------------------------------------------- */
function ddPhotoBase(root, s, push) {
  root.style.background = "#000";
  const cam = el("div", "full", root, { transformOrigin: `${(s.fx != null ? s.fx : 0.5) * 100}% ${(s.fy != null ? s.fy : 0.45) * 100}%` });
  const style = { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px", objectFit: "cover", objectPosition: s.pos || "50% 40%" };
  const a = pic(s.img, cam, Object.assign({ filter: "saturate(.88) contrast(1.05)" }, style), "abs");
  return { cam, a, style };
}
SCENES.ddphoto = async (s, root) => {
  const B = ddPhotoBase(root, s);
  vignette(root, 0.45, 50);
  const D = s.duration;
  return t => { setT(B.cam, 0, 0, 1 + (s.push || 0.045) * cl(t / D, 0, 1)); };
};
SCENES.ddspot = async (s, root) => {
  const B = ddPhotoBase(root, s);
  const bx = (s.fx != null ? s.fx : 0.5) * 100, by = (s.fy != null ? s.fy : 0.45) * 100, r = s.r || 26;
  const b = pic(s.img, B.cam, Object.assign({}, B.style, {
    filter: "grayscale(1) brightness(.45) blur(12px)",
    WebkitMaskImage: `radial-gradient(ellipse ${r}% ${r * 1.5}% at ${bx}% ${by}%, rgba(0,0,0,0) 55%, #000 100%)`,
    maskImage: `radial-gradient(ellipse ${r}% ${r * 1.5}% at ${bx}% ${by}%, rgba(0,0,0,0) 55%, #000 100%)`, opacity: 0,
  }), "abs");
  vignette(root, 0.4, 50);
  const D = s.duration, hit = s.hit != null ? s.hit : 0.6;
  return t => {
    setT(B.cam, 0, 0, 1 + 0.06 * eInOut(cl(t / D, 0, 1)));
    setO(b, eOut(seg(t, hit, 0.6)));
  };
};

/* ---- overlays over footage: the label and the chapter tab ----------------------------------- */
const DD_OUTLINE = "0 0 1.3px #05080B, 0 0 1.3px #05080B, 0 0 1.3px #05080B, 0 1.6px 3px rgba(0,0,0,.65)";
OVERLAYS.ddlabel = (o, root) => {
  const at = o.at != null ? o.at : 0.3;
  const wrap = el("div", "abs", root, { left: "120px", top: "96px" });
  const fig = !!o.figure;
  const tx = el("div", "abs", wrap, {
    left: 0, top: 0, font: `600 ${fig ? 65 : 34}px ${SANS_S}`, letterSpacing: "2px", textTransform: "uppercase",
    color: DD.ink, whiteSpace: "nowrap", textShadow: DD_OUTLINE, fontVariantNumeric: "lining-nums",
  }, esc(o.text));
  const h = fig ? 82 : 46;
  const rule = el("div", "abs", wrap, { left: "2px", top: h + "px", width: "90px", height: "5px", background: DD.red, transformOrigin: "0 50%", transform: "scaleX(0)", boxShadow: "0 1px 3px rgba(0,0,0,.5)" });
  const sub = o.sub ? el("div", "abs", wrap, {
    left: 0, top: h + 18 + "px", font: fig ? `600 24px ${SANS_S}` : `400 32px ${SERIF}`, letterSpacing: fig ? ".14em" : "0",
    textTransform: fig ? "uppercase" : "none", color: DD.ink, whiteSpace: "nowrap", textShadow: DD_OUTLINE,
  }, esc(o.sub)) : null;
  const out = o.out != null ? o.out : null;
  return t => {
    const end = out != null ? out : (SCENE.duration - 0.35);
    const a = seg(t, at, 0.06) * (1 - seg(t, end, 0.3));
    setO(wrap, a);
    if (fig) {
      const k = Math.min(9, Math.floor(Math.max(0, t - at) / 0.07));
      tx.textContent = k >= 9 ? o.text : countText(o.text, eOut(k / 9));
    }
    css(rule, "transform", `scaleX(${eOut(seg(t, at + 0.1, 0.42)).toFixed(3)})`);
    if (sub) setO(sub, eOut(seg(t, at + 0.25, 0.3)));
  };
};
OVERLAYS.ddtab = (o, root) => {
  const at = o.at != null ? o.at : 0.1;
  const shade = el("div", "full", root, { background: "linear-gradient(90deg, rgba(0,0,0,.45) 0%, rgba(0,0,0,0) 60%)" });
  const bar = el("div", "abs", root, {
    left: "97px", top: "895px", height: "79px", background: DD.tab, boxShadow: "0 0 30px rgba(0,0,0,.45)", overflow: "hidden",
    whiteSpace: "nowrap", display: "flex", alignItems: "center", clipPath: "inset(0 100% 0 0)",
  });
  el("div", "", bar, { font: `600 26px ${SANS_S}`, letterSpacing: ".08em", color: DD.tabN, padding: "0 22px 0 30px" }, esc(String(o.n).padStart(2, "0")));
  el("div", "", bar, { width: "1.5px", height: "34px", background: "rgba(143,211,255,.45)" });
  el("div", "", bar, { font: `600 29px ${SANS_S}`, letterSpacing: ".05em", textTransform: "uppercase", color: DD.tabT, padding: "0 34px 0 22px" }, esc(o.text));
  return t => {
    const end = o.out != null ? o.out : Math.min(SCENE.duration - 0.3, at + 3.4);
    const p = eInOut(seg(t, at, 1.63));
    css(bar, "clipPath", `inset(0 ${((1 - p) * 100).toFixed(2)}% 0 0)`);
    const f = 1 - seg(t, end, 0.35);
    setO(bar, f); setO(shade, Math.min(seg(t, at, 0.4), f));
  };
};
