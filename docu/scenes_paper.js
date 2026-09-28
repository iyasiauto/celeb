/* scenes_paper.js - the tactile, hand-made scenes.

   collage    A Vox-style paper tabletop: photo cards, halftone cutouts with a white
              keyline and offset red stroke, stamps, typewriter strips, pins and red
              string, stat cards, handwritten notes. Every element arrives as a physical
              object (slides, drops, springs, slams) and the camera drifts slowly.
   newspaper  A full broadsheet page built in the DOM: it rises in tilted, the camera
              pushes onto the headline and a marker sweeps across it.
   headlines  Torn headline strips slapped onto a dark wall one after another.
   baskets    Three case folders - known / claimed / unknown - with one pulled forward.
   chapter    A chapter card: big number, kicker and title on torn paper over a photo.
*/
"use strict";

/* jagged torn-paper polygon for clip-path, seeded so it never flickers */
function tornClip(seed, amp = 1.2, n = 22, sides = "tblr") {
  const r = rng(seed), pts = [];
  const j = () => (r() * amp).toFixed(2);
  for (let i = 0; i <= n; i++) pts.push(`${(i / n * 100).toFixed(2)}% ${sides.includes("t") ? j() : 0}%`);
  for (let i = 0; i <= n / 3; i++) pts.push(`${100 - (sides.includes("r") ? j() : 0)}% ${(i / (n / 3) * 100).toFixed(2)}%`);
  for (let i = n; i >= 0; i--) pts.push(`${(i / n * 100).toFixed(2)}% ${100 - (sides.includes("b") ? j() : 0)}%`);
  for (let i = Math.floor(n / 3); i >= 0; i--) pts.push(`${sides.includes("l") ? j() : 0}% ${(i / (n / 3) * 100).toFixed(2)}%`);
  return `polygon(${pts.join(",")})`;
}

function paperGround(root, kind) {
  if (kind === "cork") return pic(ground("cork", "kit:kits/frames/gen_cork.jpg"), root, { width: W + "px", height: H + "px" });
  if (kind === "dark") return el("div", "full", root, { background: "radial-gradient(ellipse at 50% 45%, #2b2824 0%, #141312 62%, #080808 100%)" });
  if (kind === "desk") return pic("desk.jpg", root, { width: W + "px", height: H + "px" });
  const g = pic(kind === "map" ? ground("map", "paper_map.jpg") : ground("paper", "paper_tan.jpg"), root, { width: W + "px", height: H + "px" });
  return g;
}

/* entrance transform for a physical element: returns [dx, dy, rot, scale, opacity] */
function entrance(from, t, at, rot, seed) {
  const u = t - at;
  if (u < 0) return null;
  const r = rng(seed)();
  switch (from) {
    case "drop": { const p = eBack(seg(u, 0, 0.55), 1.3); return [0, (1 - p) * -700, rot + (1 - p) * (r * 16 - 8), 1, 1]; }
    case "pop": { const p = spring(u, 2.4, 0.42); return [0, 0, rot, 0.55 + 0.45 * p, cl(u / 0.12, 0, 1)]; }
    case "slam": { const p = eOut5(seg(u, 0, 0.22)); return [0, 0, rot, lerp(2.2, 1, p), cl(u / 0.08, 0, 1)]; }
    case "fade": return [0, 0, rot, 1, eOut(seg(u, 0, 0.5))];
    case "up": { const p = eBack(seg(u, 0, 0.6), 1.2); return [0, (1 - p) * 900, rot + (1 - p) * 6, 1, 1]; }
    case "down": { const p = eBack(seg(u, 0, 0.6), 1.2); return [0, (1 - p) * -900, rot - (1 - p) * 6, 1, 1]; }
    case "right": { const p = eBack(seg(u, 0, 0.6), 1.1); return [(1 - p) * 1300, 0, rot + (1 - p) * 10, 1, 1]; }
    default: { const p = eBack(seg(u, 0, 0.6), 1.1); return [(1 - p) * -1300, 0, rot - (1 - p) * 10, 1, 1]; }  /* left */
  }
}

/* place a centred element with an entrance */
function placer(node, it, defFrom) {
  return t => {
    const e = entrance(it.from || defFrom, t, it.at || 0, it.rot || 0, (it.seed || 3) + Math.round((it.x || 0) + (it.y || 0)));
    if (!e) { vis(node, false); return; }
    vis(node, true);
    const w = node.offsetWidth, h = node.offsetHeight;
    setT(node, it.x - w / 2 + e[0], it.y - h / 2 + e[1], e[3], e[2]);
    setO(node, e[4] * (it.out != null ? 1 - seg(t, it.out, 0.3) : 1));
  };
}

const ITEMS = {
  photo(board, it) {
    const card = el("div", "abs", board, {
      left: 0, top: 0, background: "#F6F2EA", padding: (it.pad != null ? it.pad : 14) + "px",
      boxShadow: "0 22px 46px rgba(0,0,0,.42), 0 3px 8px rgba(0,0,0,.25)", transformOrigin: "50% 50%",
    });
    const im = pic(it.img, card, { position: "relative", width: it.w + "px" }, "");
    if (it.h) { im.style.height = it.h + "px"; im.style.objectFit = "cover"; }
    if (it.caption) el("div", "", card, {
      font: "24px 'Elite'", color: "#2a2622", paddingTop: "10px", textAlign: "center", width: it.w + "px",
    }, esc(it.caption));
    if (it.tape !== false) {
      const tp = el("div", "abs", card, {
        left: "50%", top: "-22px", width: "170px", height: "46px", marginLeft: "-85px",
        background: "rgba(236,226,196,.78)", boxShadow: "0 2px 6px rgba(0,0,0,.18)",
        transform: `rotate(${(it.rot || 0) > 0 ? -4 : 4}deg)`, clipPath: tornClip(it.x | 0, 5, 10, "lr"),
      });
    }
    return placer(card, it, "left");
  },
  cut(board, it) {
    const im = pic(it.img, board, { height: it.h + "px", left: 0, top: 0 }, "abs");
    /* keyline, red stroke and shadow are baked into the PNG by prep.bake_keyline */
    im.style.transformOrigin = "50% 50%";
    return placer(im, it, "up");
  },
  stamp(board, it) {
    const c = it.color || PAL.red;
    const s = el("div", "abs", board, {
      left: 0, top: 0, font: `${it.size || 86}px 'Stamp'`, color: c, border: `${Math.round((it.size || 86) / 12)}px solid ${c}`,
      padding: "4px 26px 0", letterSpacing: ".04em", whiteSpace: "nowrap", opacity: 0.92, transformOrigin: "50% 50%",
      webkitMaskImage: `url('${asset("grunge.png")}')`, webkitMaskSize: "600px 300px", willChange: "transform",
    }, esc(it.text));
    return placer(s, it, "slam");
  },
  strip(board, it) {
    const s = el("div", "abs", board, {
      left: 0, top: 0, background: it.bg || "#F4EFE3", color: it.color || "#1d1b18", font: `${it.size || 34}px '${it.font || "Elite"}'`,
      padding: "12px 30px 10px", whiteSpace: "nowrap", boxShadow: "0 8px 18px rgba(0,0,0,.32)",
      clipPath: tornClip((it.seed || 5) + (it.y | 0), 2.4, 28, "lr"), transformOrigin: "50% 50%",
    });
    const txt = el("span", "", s, {}, "");
    const sizer = el("span", "", s, { visibility: "hidden", position: "absolute" }, esc(it.text));
    s.style.minWidth = "40px";
    const pl = placer(s, it, it.from || "fade");
    return t => {
      if (it.type === false) { if (!txt._d) { txt.innerHTML = esc(it.text); txt._d = 1; } }
      else typeOn(txt, it.text, t, (it.at || 0) + 0.25, it.cps || 30, false);
      if (!s._w) { txt.innerHTML = esc(it.text); s.style.width = s.offsetWidth - 60 + "px"; s._w = 1; txt.innerHTML = ""; }
      pl(t);
    };
  },
  title(board, it) {
    const d = el("div", "abs", board, {
      left: 0, top: 0, font: `${it.size || 140}px '${it.font || "Anton"}'`, color: it.color || PAL.ink, lineHeight: "1.0",
      whiteSpace: "pre", textAlign: it.align || "left", letterSpacing: it.ls || ".01em", transformOrigin: "50% 50%",
      textShadow: it.shadow || "none",
    }, esc(it.text));
    const u = it.underline ? el("div", "abs", board, { left: 0, top: 0, height: Math.round((it.size || 140) * 0.09) + "px", background: PAL.red, transformOrigin: "0 50%" }) : null;
    const pl = placer(d, it, it.from || "fade");
    return t => {
      pl(t);
      if (u) {
        const w = d.offsetWidth, h = d.offsetHeight;
        const p = eOut(seg(t, (it.at || 0) + 0.45, 0.45));
        setT(u, it.x - w / 2, it.y + h / 2 + 4, 1, (it.rot || 0));
        css(u, "width", (w * p).toFixed(0) + "px");
        vis(u, p > 0);
      }
    };
  },
  note(board, it) {
    const n = el("div", "abs", board, {
      left: 0, top: 0, width: (it.w || 380) + "px", background: it.bg || "#F2D680", color: "#2a2210",
      font: `${it.size || 44}px 'Caveat'`, lineHeight: "1.05", padding: "26px 28px", boxShadow: "0 14px 28px rgba(0,0,0,.35)",
      transformOrigin: "50% 50%",
    }, esc(it.text));
    return placer(n, it, "drop");
  },
  stat(board, it) {
    const c = el("div", "abs", board, {
      left: 0, top: 0, background: it.bg || PAL.red, color: "#fff", padding: "22px 44px 26px", textAlign: "center",
      clipPath: tornClip((it.x | 0) + 11, 1.6, 20), boxShadow: "0 16px 30px rgba(0,0,0,.35)", transformOrigin: "50% 50%",
    });
    const v = el("div", "", c, { font: `${it.size || 150}px 'Anton'`, lineHeight: "1", color: it.color || "#2b1510" }, esc(it.value));
    const l = el("div", "", c, { font: "30px 'Elite'", color: "#fff", marginTop: "10px", whiteSpace: "nowrap" }, esc(it.label || ""));
    const pl = placer(c, it, "pop");
    return t => {
      if (!c._w) { c.style.width = c.offsetWidth - 88 + "px"; c._w = 1; }
      const p = it.count === false ? 1 : eOut(seg(t, (it.at || 0) + 0.1, it.countFor || 1.2));
      const s = countText(it.value, p);
      if (v._s !== s) { v.textContent = s; v._s = s; }
      pl(t);
    };
  },
  pin(board, it) {
    const p = el("div", "abs", board, {
      left: 0, top: 0, width: "34px", height: "34px", borderRadius: "50%",
      background: `radial-gradient(circle at 35% 30%, #ff8a7a 0%, ${PAL.red} 45%, #6d0f07 100%)`,
      boxShadow: "0 8px 10px rgba(0,0,0,.45)", transformOrigin: "50% 50%",
    });
    return placer(p, Object.assign({ from: "drop" }, it), "drop");
  },
  string(board, it) {
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    Object.assign(svg.style, { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px", overflow: "visible" });
    board.appendChild(svg);
    const path = document.createElementNS(svgNS, "path");
    const d = it.pts.map((p, i) => (i ? "L" : "M") + p[0] + " " + p[1]).join(" ");
    path.setAttribute("d", d);
    path.setAttribute("fill", "none"); path.setAttribute("stroke", it.color || "#B0180E");
    path.setAttribute("stroke-width", it.width || 5); path.setAttribute("stroke-linecap", "round");
    path.style.filter = "drop-shadow(0 6px 4px rgba(0,0,0,.35))";
    svg.appendChild(path);
    let len = 0;
    for (let i = 1; i < it.pts.length; i++) len += Math.hypot(it.pts[i][0] - it.pts[i - 1][0], it.pts[i][1] - it.pts[i - 1][1]);
    path.setAttribute("stroke-dasharray", len.toFixed(1));
    return t => {
      const p = eInOut(seg(t, it.at || 0, it.d || 0.9));
      path.setAttribute("stroke-dashoffset", (len * (1 - p)).toFixed(1));
      path.style.opacity = p > 0 ? 1 : 0;
    };
  },
  circle(board, it) {
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    Object.assign(svg.style, { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px", overflow: "visible" });
    board.appendChild(svg);
    const path = document.createElementNS(svgNS, "path");
    /* a hand-drawn loop: a little more than one turn, slightly wobbly */
    const r = rng(it.seed || 9), pts = [];
    for (let i = 0; i <= 64; i++) {
      const a = -Math.PI / 2 + i / 64 * Math.PI * 2.12, k = 1 + (r() - 0.5) * 0.04;
      pts.push([it.x + Math.cos(a) * it.rx * k, it.y + Math.sin(a) * it.ry * k]);
    }
    path.setAttribute("d", pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" "));
    path.setAttribute("fill", "none"); path.setAttribute("stroke", it.color || PAL.red);
    path.setAttribute("stroke-width", it.width || 9); path.setAttribute("stroke-linecap", "round");
    svg.appendChild(path);
    const len = Math.PI * 2.12 * (it.rx + it.ry) / 2 * 1.02;
    path.setAttribute("stroke-dasharray", len.toFixed(1));
    return t => {
      const p = eInOut(seg(t, it.at || 0, it.d || 0.6));
      path.setAttribute("stroke-dashoffset", (len * (1 - p)).toFixed(1));
      path.style.opacity = p > 0 ? 1 : 0;
    };
  },
  arrow(board, it) {
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    Object.assign(svg.style, { position: "absolute", left: 0, top: 0, width: W + "px", height: H + "px", overflow: "visible" });
    board.appendChild(svg);
    const [x0, y0] = it.from, [x1, y1] = it.to;
    const mx = (x0 + x1) / 2 + (it.bend || 0), my = (y0 + y1) / 2 - Math.abs(it.bend || 60);
    const path = document.createElementNS(svgNS, "path");
    path.setAttribute("d", `M${x0} ${y0} Q${mx} ${my} ${x1} ${y1}`);
    path.setAttribute("fill", "none"); path.setAttribute("stroke", it.color || PAL.red);
    path.setAttribute("stroke-width", 8); path.setAttribute("stroke-linecap", "round");
    svg.appendChild(path);
    const ang = Math.atan2(y1 - my, x1 - mx);
    const head = document.createElementNS(svgNS, "path");
    const hx = (a) => [x1 - 34 * Math.cos(ang + a), y1 - 34 * Math.sin(ang + a)];
    const [a1, a2] = [hx(0.5), hx(-0.5)];
    head.setAttribute("d", `M${a1[0]} ${a1[1]} L${x1} ${y1} L${a2[0]} ${a2[1]}`);
    head.setAttribute("fill", "none"); head.setAttribute("stroke", it.color || PAL.red);
    head.setAttribute("stroke-width", 8); head.setAttribute("stroke-linecap", "round"); head.setAttribute("stroke-linejoin", "round");
    svg.appendChild(head);
    const len = Math.hypot(mx - x0, my - y0) + Math.hypot(x1 - mx, y1 - my);
    path.setAttribute("stroke-dasharray", len.toFixed(1));
    return t => {
      const p = eInOut(seg(t, it.at || 0, it.d || 0.5));
      path.setAttribute("stroke-dashoffset", (len * (1 - p)).toFixed(1));
      path.style.opacity = p > 0 ? 1 : 0;
      head.style.opacity = p >= 1 ? 1 : 0;
    };
  },
  text(board, it) {
    const d = el("div", "abs", board, {
      left: 0, top: 0, width: (it.w || 800) + "px", font: `${it.size || 40}px '${it.font || "Lora"}'`,
      color: it.color || PAL.ink, lineHeight: it.lh || "1.3", textAlign: it.align || "left", transformOrigin: "50% 50%",
      whiteSpace: "pre-line",
    }, esc(it.text));
    return placer(d, it, it.from || "fade");
  },
};

SCENES.collage = async (s, root) => {
  const board = el("div", "full", root, { transformOrigin: "50% 50%" });
  paperGround(board, s.bg || "paper");
  const ups = (s.items || []).map(it => ITEMS[it.k](board, it));
  if (s.vignette !== 0) vignette(root, s.vignette || 0.42, 50);
  const D = s.duration;
  const [fx, fy] = s.focus || [0.5, 0.5];
  return t => {
    const p = drift(cl(t / D, 0, 1));
    const z = lerp(s.z0 || 1.0, s.z1 || 1.05, p);
    setT(board, (0.5 - fx) * W * (z - 1), (0.5 - fy) * H * (z - 1), z);
    ups.forEach(u => u(t));
  };
};

SCENES.newspaper = async (s, root) => {
  paperGround(root, s.ground || "dark");
  const persp = el("div", "full", root, { perspective: "2200px" });
  const PW = 1500;
  const page = el("div", "abs", persp, {
    left: 0, top: 0, width: PW + "px", background: "#ECE5D3", color: "#191714", padding: "56px 64px 80px",
    boxSizing: "border-box", transformOrigin: "50% 30%", boxShadow: "0 60px 140px rgba(0,0,0,.75)",
    backgroundImage: `url('${asset("newsprint.jpg")}')`, backgroundSize: "cover",
  });
  const r = rng(s.seed || 4);
  el("div", "", page, { display: "flex", justifyContent: "space-between", font: "20px 'Barlow'", letterSpacing: ".2em", borderBottom: "2px solid #191714", paddingBottom: "10px" },
    `<span>${esc(s.edition || "LATE EDITION")}</span><span>${esc(s.date || "")}</span><span>${esc(s.price || "")}</span>`);
  el("div", "", page, { font: "118px 'Cinzel'", textAlign: "center", letterSpacing: ".02em", padding: "10px 0 0", lineHeight: "1.1" }, esc(s.masthead || "THE MORNING LEDGER"));
  el("div", "", page, { borderTop: "5px double #191714", borderBottom: "2px solid #191714", height: "6px", margin: "6px 0 26px" });
  const hl = el("div", "", page, { position: "relative", font: `${s.hsize || 112}px 'Playfair'`, fontWeight: "900", lineHeight: "1.02", textAlign: "center", padding: "0 20px" });
  const words = (s.headline || "").split("\n");
  const lines = words.map(w => {
    const ln = el("div", "", hl, { position: "relative", display: "inline-block" });
    const mk = el("div", "abs", ln, { left: "-10px", top: "18%", height: "70%", width: "0", background: PAL.mustard, opacity: 0.85, mixBlendMode: "multiply" });
    el("span", "", ln, { position: "relative" }, esc(w));
    el("br", "", hl);
    return { ln, mk };
  });
  if (s.deck) el("div", "", page, { font: "38px 'LoraI'", textAlign: "center", margin: "22px 60px 26px", color: "#2e2a24" }, esc(s.deck));
  const body = el("div", "", page, { display: "flex", gap: "34px" });
  const colText = (s.body || []).join(" ");
  const cols = s.img ? 2 : 4;
  if (s.img) {
    const fig = el("div", "", body, { flex: "0 0 820px" });
    const im = pic(s.img, fig, { position: "relative", width: "820px", height: "560px", objectFit: "cover", filter: "grayscale(1) contrast(1.1)" }, "");
    el("div", "", fig, { font: "21px 'LoraI'", marginTop: "10px", color: "#3a352d" }, esc(s.caption || ""));
  }
  const cw = el("div", "", body, { flex: "1", columnCount: cols, columnGap: "28px", font: "22px 'Lora'", lineHeight: "1.42", textAlign: "justify", color: "#2b2722", height: "760px", overflow: "hidden" }, esc(colText));
  vignette(root, 0.55);
  const D = s.duration, hit = s.hit || 1.3;
  return t => {
    const ph = page.offsetHeight;
    const a = eOut5(seg(t, 0, 1.2));
    const p = eInOut(seg(t, 0.4, D - 0.4));
    const z = lerp(0.62, s.zoom || 1.25, p);
    /* camera aims at the headline block */
    const hy = hl.offsetTop + hl.offsetHeight / 2;
    const x = W / 2 - PW / 2;
    const y = lerp(H / 2 - ph * 0.3, H / 2 - hy, eInOut(seg(t, 0.2, 2.0))) + (1 - a) * 500;
    const rx = (1 - a) * 35 + 4 * (1 - p), rz = lerp(-4, -1, p);
    const v = `translate(${x.toFixed(1)}px,${y.toFixed(1)}px) rotateX(${rx.toFixed(2)}deg) rotateZ(${rz.toFixed(2)}deg) scale(${z.toFixed(4)})`;
    css(page, "transform", v);
    css(page, "transformOrigin", `50% ${hy}px`);
    lines.forEach((l, i) => {
      const q = eInOut(seg(t, hit + i * 0.45, 0.5));
      css(l.mk, "width", `calc(${(q * 100).toFixed(1)}% + 20px)`);
      vis(l.mk, q > 0);
    });
  };
};

SCENES.headlines = async (s, root) => {
  paperGround(root, s.bg || "dark");
  const board = el("div", "full", root, { transformOrigin: "50% 50%" });
  const ups = (s.items || []).map((it, i) => {
    const style = it.style || ["white", "red", "black", "tan"][i % 4];
    const bg = { white: "#F3EFE6", red: PAL.red, black: "#141414", tan: "#D8CBAA" }[style];
    const fg = { white: "#141414", red: "#fff", black: "#F3EFE6", tan: "#141414" }[style];
    const d = el("div", "abs", board, {
      left: 0, top: 0, background: bg, color: fg, padding: "22px 46px 20px", boxShadow: "0 22px 44px rgba(0,0,0,.5)",
      clipPath: tornClip(i * 31 + 7, 2.2, 26), transformOrigin: "50% 50%", maxWidth: "1300px",
    });
    el("div", "", d, { font: `${it.size || 78}px 'Anton'`, lineHeight: "1.02", letterSpacing: ".01em" }, esc(it.text));
    if (it.sub) el("div", "", d, { font: "26px 'Elite'", marginTop: "10px", opacity: 0.85 }, esc(it.sub));
    return placer(d, Object.assign({ from: "slam" }, it), "slam");
  });
  vignette(root, 0.5);
  const D = s.duration;
  return t => {
    const z = lerp(1.0, 1.06, drift(cl(t / D, 0, 1)));
    setT(board, W / 2 * (1 - z), H / 2 * (1 - z), z);
    ups.forEach(u => u(t));
  };
};

SCENES.baskets = async (s, root) => {
  const board = el("div", "full", root, { transformOrigin: "50% 50%" });
  paperGround(board, "paper");
  const labels = s.labels || ["WHAT WE KNOW", "WHAT IS CLAIMED", "WHAT REMAINS UNKNOWN"];
  const stamps = s.stamps || ["VERIFIED", "CLAIMED", "UNKNOWN"];
  const colors = ["#2F6B3A", PAL.mustard, PAL.red];
  const folders = labels.map((lab, i) => {
    const f = el("div", "abs", board, { left: 0, top: 0, width: "520px", height: "640px", transformOrigin: "50% 60%" });
    el("div", "abs", f, { left: "30px", top: "0", width: "200px", height: "60px", background: "#C9A96A", borderRadius: "10px 10px 0 0" });
    const body = el("div", "abs", f, {
      left: 0, top: "46px", width: "520px", height: "594px", background: "linear-gradient(180deg,#D8BC80 0%,#C8A866 100%)",
      borderRadius: "4px 12px 12px 12px", boxShadow: "0 30px 60px rgba(0,0,0,.4)",
    });
    el("div", "abs", body, { left: "40px", top: "60px", font: "92px 'Anton'", color: "rgba(40,28,10,.85)" }, String(i + 1).padStart(2, "0"));
    el("div", "abs", body, { left: "40px", top: "190px", width: "440px", font: "54px 'Anton'", lineHeight: "1.05", color: "#231a0c" }, esc(lab));
    const st = el("div", "abs", body, {
      left: "60px", top: "420px", font: "72px 'Stamp'", color: colors[i], border: `6px solid ${colors[i]}`, padding: "2px 22px 0",
      transform: "rotate(-9deg)", webkitMaskImage: `url('${asset("grunge.png")}')`, webkitMaskSize: "600px 300px", opacity: 0,
    }, esc(stamps[i]));
    return { f, st };
  });
  const act = s.active == null ? -1 : s.active;
  vignette(root, 0.45, 50);
  const D = s.duration;
  return t => {
    const z = lerp(1.0, 1.04, drift(cl(t / D, 0, 1)));
    setT(board, W / 2 * (1 - z), H / 2 * (1 - z), z);
    folders.forEach((o, i) => {
      const at = s.reveal ? (s.at || 0.3) + i * (s.gap || 0.9) : 0;
      const a = s.reveal ? eBack(seg(t, at, 0.6), 1.1) : 1;
      const baseX = 130 + i * 580, baseY = 250;
      let x = baseX, y = baseY + (1 - a) * 900, sc = 1, rot = [-3, 1.5, -1][i];
      const fo = act >= 0 ? eInOut(seg(t, s.focusAt || 0.4, 0.8)) : 0;
      if (i === act) { x = lerp(baseX, W / 2 - 260, fo); y = lerp(baseY, 200, fo); sc = lerp(1, 1.28, fo); rot = lerp(rot, 0, fo); }
      else if (act >= 0) { sc = lerp(1, 0.92, fo); }
      setT(o.f, x, y, sc, rot);
      setO(o.f, (i === act || act < 0) ? 1 : lerp(1, 0.35, fo));
      o.f.style.zIndex = i === act ? 5 : 1;
      const stAt = s.reveal ? at + 0.45 : (s.stampAt || 1.0);
      const sp = (act < 0 || i === act) ? eOut5(seg(t, stAt, 0.22)) : 0;
      setO(o.st, sp * 0.95);
      o.st.style.transform = `rotate(-9deg) scale(${lerp(2.0, 1, sp).toFixed(3)})`;
    });
  };
};

SCENES.chapter = async (s, root) => {
  const L = s.img ? photoLayer(root, Object.assign({ move: "in" }, s)) : null;
  if (!s.img) paperGround(root, "dark");
  el("div", "full", root, { background: "linear-gradient(90deg, rgba(8,8,8,.82) 0%, rgba(8,8,8,.55) 55%, rgba(8,8,8,.25) 100%)" });
  vignette(root, 0.6);
  const n = el("div", "abs", root, { left: "140px", top: "250px", font: "300px 'Anton'", lineHeight: "1", color: PAL.mustard, textShadow: "0 20px 60px rgba(0,0,0,.5)" }, esc(s.n || ""));
  const rule = el("div", "abs", root, { left: "150px", top: "590px", height: "5px", width: "0", background: PAL.mustard });
  const k = el("div", "abs", root, { left: "150px", top: "620px", font: "40px 'Barlow'", letterSpacing: ".3em", color: "#EFE7D6" }, esc(s.kicker || ""));
  const tt = el("div", "abs", root, {
    left: "130px", top: "690px", background: "#F3EEE2", color: PAL.ink, font: "96px 'Anton'", padding: "14px 40px 8px",
    clipPath: tornClip(17, 1.4, 30), whiteSpace: "nowrap", boxShadow: "0 20px 40px rgba(0,0,0,.5)",
  }, esc(s.title || ""));
  const D = s.duration;
  return t => {
    if (L) L.draw(drift(cl(t / D, 0, 1)));
    const a = eOut5(seg(t, 0.15, 0.7));
    setO(n, a); setT(n, 0, (1 - a) * 60);
    css(rule, "width", (eOut(seg(t, 0.45, 0.6)) * 520).toFixed(0) + "px");
    const b = eOut(seg(t, 0.6, 0.6));
    setO(k, b); setT(k, (1 - b) * -30, 0);
    const c = eBack(seg(t, 0.85, 0.55), 1.2);
    setT(tt, (1 - c) * -1400, 0, 1, -1.5 * c);
    vis(tt, t >= 0.85);
    if (s.out != null) setO(root.lastChild, 1);
  };
};
