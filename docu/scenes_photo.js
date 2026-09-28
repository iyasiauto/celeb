/* scenes_photo.js - scenes built on one real photograph.

   photo      Ken Burns over a still: cover-fit camera drift, or contain-fit over a
              blurred copy of itself for pictures that are not 16:9.
   depth      "Depth pop": the subject, cut out of the picture, lifts off it - the
              ground blurs and darkens, the subject grows a white keyline and shadow.
   spotlight  Everything but one region dims and blurs; a red ring draws round the
              region and a label hangs off it on a leader line.
   tv         A picture shown on a real television set in a dark room.
   card       A found object (a post, a clipping) floating over a dark ground.
   split      Two pictures side by side with a divider and a label on each.

   Pictures arrive pre-graded from prep.py (colour, black-and-white, blurred and
   dimmed variants), so no per-frame CSS filter ever touches a full-frame layer.
*/
"use strict";

/* The camera over one picture: centre (cx, cy) in picture fractions and zoom z >= 1
   relative to a cover fit. Clamped so the picture always covers the frame. */
function coverCam(iw, ih, cx, cy, z, fw = W, fh = H) {
  const k = Math.max(fw / iw, fh / ih) * z;
  let tx = fw / 2 - cx * iw * k, ty = fh / 2 - cy * ih * k;
  tx = cl(tx, fw - iw * k, 0); ty = cl(ty, fh - ih * k, 0);
  return { tx, ty, k };
}

/* Start and end camera for a named move around a focus point. */
function moveKeys(move, focus, zoom) {
  const [fx, fy] = focus || [0.5, 0.5];
  const z = zoom || 1.14, d = 0.06;
  switch (move) {
    case "out": return [[fx, fy, z], [0.5, 0.5, 1.02]];
    case "left": return [[fx + d, fy, z - 0.02], [fx - d, fy, z - 0.02]];
    case "right": return [[fx - d, fy, z - 0.02], [fx + d, fy, z - 0.02]];
    case "up": return [[fx, fy + d, z - 0.02], [fx, fy - d, z - 0.02]];
    case "down": return [[fx, fy - d, z - 0.02], [fx, fy + d, z - 0.02]];
    case "none": return [[fx, fy, 1.03], [fx, fy, 1.03]];
    case "push": return [[fx, fy, 1.04], [fx, fy, z + 0.12]];
    default: return [[0.5, 0.5, 1.02], [fx, fy, z]];           /* "in" */
  }
}

/* A picture on its own camera: returns (layer, draw(p)) where p is 0..1 along the move. */
function photoLayer(parent, s) {
  const cam = el("div", "full", parent, { overflow: "hidden" });
  const im = pic(s.img, cam);
  const keys = s.keys || moveKeys(s.move || "in", s.focus, s.zoom);
  let fill = null, inner = null;
  if (s.fit === "contain") {
    fill = pic(s.fill || s.img.replace(/\.jpg$/, "_blur.jpg"), cam);
    cam.insertBefore(fill, im);
  }
  return {
    cam, im,
    draw(p) {
      const iw = im.naturalWidth || W, ih = im.naturalHeight || H;
      const [a, b] = keys;
      const cx = lerp(a[0], b[0], p), cy = lerp(a[1], b[1], p), z = lerp(a[2], b[2], p);
      if (s.fit === "contain") {
        const fk = Math.max(W / (fill.naturalWidth || 1), H / (fill.naturalHeight || 1)) * 1.05;
        setT(fill, (W - fill.naturalWidth * fk) / 2, (H - fill.naturalHeight * fk) / 2, fk);
        const m = s.margin || 0.9;
        const k = Math.min(W * m / iw, H * m / ih) * (0.97 + 0.06 * (z - 1) / 0.14);
        const ox = (0.5 - cx) * iw * k * 0.3, oy = (0.5 - cy) * ih * k * 0.3;
        setT(im, (W - iw * k) / 2 + ox, (H - ih * k) / 2 + oy, k);
        if (!im._sh) { im.style.boxShadow = "0 30px 80px rgba(0,0,0,.6)"; im._sh = 1; }
      } else {
        const c = coverCam(iw, ih, cx, cy, z);
        setT(im, c.tx, c.ty, c.k);
      }
    },
  };
}

SCENES.photo = async (s, root) => {
  const L = photoLayer(root, s);
  const dim = s.dim ? el("div", "full", root, { background: `rgba(0,0,0,${s.dim})` }) : null;
  if (s.vignette !== 0) vignette(root, s.vignette || 0.5);
  const D = s.duration;
  return t => L.draw(drift(cl(t / D, 0, 1)));
};

SCENES.depth = async (s, root) => {
  /* the ground: the sharp picture, then its blurred + dimmed twin fading in on the hit */
  const cam = el("div", "full", root, { overflow: "hidden" });
  const sharp = pic(s.img, cam);
  const soft = pic(s.soft || s.img.replace(/\.jpg$/, "_soft.jpg"), cam);
  const tint = el("div", "full", root, { background: s.tint || "rgba(8,8,10,.35)", opacity: 0 });
  vignette(root, 0.6);
  /* the subject: a cutout the same size as the picture, so it sits exactly on it */
  /* keyline and shadow are baked in (prep: <key>_cutk.png) - no per-frame filter */
  const subj = pic(s.cut || s.img.replace(/\.jpg$/, "_cutk.png"), root);
  const hit = s.hit != null ? s.hit : 0.9, D = s.duration;
  const keys = s.keys || moveKeys(s.move || "in", s.focus, s.zoom || 1.08);
  return t => {
    const iw = sharp.naturalWidth || W, ih = sharp.naturalHeight || H;
    const p = drift(cl(t / D, 0, 1));
    const cx = lerp(keys[0][0], keys[1][0], p), cy = lerp(keys[0][1], keys[1][1], p), z = lerp(keys[0][2], keys[1][2], p);
    const c = coverCam(iw, ih, cx, cy, z);
    setT(sharp, c.tx, c.ty, c.k);
    setT(soft, c.tx, c.ty, c.k);
    const h = eInOut(seg(t, hit, 0.7));
    setO(soft, h); setO(tint, h);
    /* the subject grows around its own centre and drifts against the ground */
    const [sx, sy] = s.subject || [0.5, 0.55];
    const pop = 1 + (s.pop || 0.07) * eBack(seg(t, hit, 0.8), 1.2);
    const px = c.tx + sx * iw * c.k, py = c.ty + sy * ih * c.k;
    const k2 = c.k * pop;
    const par = (s.parallax || 26) * h;
    setT(subj, px - sx * iw * k2 - par, py - sy * ih * k2 - par * 0.3, k2);
    setO(subj, cl(h * 3, 0, 1));
  };
};

SCENES.spotlight = async (s, root) => {
  const cam = el("div", "full", root, { overflow: "hidden" });
  const inner = el("div", "layer", cam, { width: "10px", height: "10px" });
  const base = pic(s.img, inner, { left: 0, top: 0, transformOrigin: "0 0" });
  const dim = pic(s.dimImg || s.img.replace(/\.jpg$/, "_dim.jpg"), inner, { left: 0, top: 0 });
  const top = pic(s.img, inner, { left: 0, top: 0 });
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  Object.assign(svg.style, { position: "absolute", left: 0, top: 0, overflow: "visible" });
  inner.appendChild(svg);
  const ring = document.createElementNS(svgNS, "ellipse");
  ring.setAttribute("fill", "none"); ring.setAttribute("stroke", PAL.red);
  svg.appendChild(ring);
  vignette(root, 0.45);
  const lab = s.label ? el("div", "abs", root, {
    font: "34px 'OswaldB'", letterSpacing: ".08em", color: PAL.ink, background: PAL.mustard,
    padding: "8px 18px 6px", textTransform: "uppercase", whiteSpace: "nowrap", boxShadow: "0 10px 30px rgba(0,0,0,.45)",
  }, esc(s.label)) : null;
  const lineEl = s.label ? el("div", "abs", root, { height: "3px", background: PAL.mustard, transformOrigin: "0 50%" }) : null;
  const hit = s.hit != null ? s.hit : 0.8, D = s.duration;
  const [cx, cy] = s.center || [0.5, 0.5];
  const [rx, ry] = s.radius || [0.18, 0.18];
  return t => {
    const iw = base.naturalWidth || W, ih = base.naturalHeight || H;
    const p = drift(cl(t / D, 0, 1));
    const z = lerp(1.02, s.zoom || 1.22, p);
    const fx = lerp(0.5, cx, p * 0.85), fy = lerp(0.5, cy, p * 0.85);
    const c = coverCam(iw, ih, fx, fy, z);
    setT(inner, c.tx, c.ty, c.k);
    const h = eInOut(seg(t, hit, 0.8));
    setO(dim, h);
    /* the sharp picture shows only inside the ellipse once the hit lands */
    const grow = lerp(3.0, 1.0, h);
    const mx = cx * iw, my = cy * ih, ax = rx * iw * grow, ay = ry * ih * grow;
    const m = `radial-gradient(ellipse ${ax.toFixed(0)}px ${ay.toFixed(0)}px at ${mx.toFixed(0)}px ${my.toFixed(0)}px, #000 92%, transparent 100%)`;
    css(top, "webkitMaskImage", m);
    css(svg, "width", iw + "px"); css(svg, "height", ih + "px");
    ring.setAttribute("cx", mx); ring.setAttribute("cy", my);
    ring.setAttribute("rx", rx * iw * 1.04); ring.setAttribute("ry", ry * ih * 1.04);
    ring.setAttribute("stroke-width", (6 / c.k).toFixed(2));
    const per = Math.PI * (rx * iw + ry * ih) * 1.04;
    const r = eOut(seg(t, hit + 0.4, 0.7));
    ring.setAttribute("stroke-dasharray", per.toFixed(1));
    ring.setAttribute("stroke-dashoffset", (per * (1 - r)).toFixed(1));
    ring.style.opacity = r > 0 ? 1 : 0;
    if (lab) {
      const ex = c.tx + (cx + rx * 1.04 * (s.side === "left" ? -0.72 : 0.72)) * iw * c.k;
      const ey = c.ty + (cy - ry * 0.72) * ih * c.k;
      const lx = s.side === "left" ? ex - 260 : ex + 160, ly = ey - 120;
      const q = eOut(seg(t, hit + 0.9, 0.5));
      const dx = lx - ex, dy = ly + 26 - ey, len = Math.hypot(dx, dy);
      setT(lineEl, ex, ey, 1, Math.atan2(dy, dx) * 180 / Math.PI);
      css(lineEl, "width", (len * q).toFixed(1) + "px");
      const q2 = eOut(seg(t, hit + 1.2, 0.45));
      setT(lab, s.side === "left" ? lx - lab.offsetWidth : lx, ly);
      css(lab, "clipPath", `inset(0 ${((1 - q2) * 100).toFixed(1)}% 0 0)`);
    }
  };
};

SCENES.tv = async (s, root) => {
  /* the set is pre-cut by prep.py: screen area transparent, room around it */
  const box = s.box || [562, 250, 1209, 709];
  const world = el("div", "full", root, { transformOrigin: "50% 50%" });
  const screen = el("div", "abs", world, {
    left: box[0] + "px", top: box[1] + "px", width: box[2] - box[0] + "px", height: box[3] - box[1] + "px",
    overflow: "hidden", background: "#111",
  });
  const inner = pic(s.img, screen);
  const scan = el("div", "abs", screen, {
    left: 0, top: 0, width: "100%", height: "100%",
    background: "repeating-linear-gradient(0deg, rgba(0,0,0,.22) 0 2px, rgba(0,0,0,0) 2px 4px)", mixBlendMode: "multiply",
  });
  const glow = el("div", "abs", screen, {
    left: 0, top: 0, width: "100%", height: "100%",
    background: "radial-gradient(ellipse at 50% 45%, rgba(255,255,255,.10) 0%, rgba(0,0,0,.35) 100%)",
  });
  const set = pic(s.set || "kit_tv_cut.png", world);
  vignette(root, 0.5);
  const D = s.duration;
  const [fx, fy] = s.focus || [0.5, 0.5];
  return t => {
    const sw = box[2] - box[0], sh = box[3] - box[1];
    const iw = inner.naturalWidth || sw, ih = inner.naturalHeight || sh;
    const p = drift(cl(t / D, 0, 1));
    const c = coverCam(iw, ih, fx, fy, lerp(1.0, 1.08, p), sw, sh);
    setT(inner, c.tx, c.ty, c.k);
    setT(set, 0, 0, 1);
    const z = lerp(s.from || 1.0, s.to || 1.28, eInOut(cl(t / D, 0, 1)));
    const ccx = (box[0] + box[2]) / 2, ccy = (box[1] + box[3]) / 2;
    setT(world, (W / 2 - ccx) * (z - 1) * 0.9, (H / 2 - ccy) * (z - 1) * 0.9, z);
    setO(glow, 0.85 + 0.15 * Math.sin(t * 23.0) * Math.sin(t * 7.3));
  };
};

SCENES.card = async (s, root) => {
  const ground = s.ground ? pic(s.ground, root) : el("div", "full", root, {
    background: "radial-gradient(ellipse at 50% 40%, #2a2724 0%, #121110 60%, #070707 100%)",
  });
  if (s.ground) setT(ground, 0, 0, Math.max(W / 1920, 1));
  const persp = el("div", "full", root, { perspective: "1800px" });
  const card = el("div", "abs", persp, { left: "0", top: "0", transformOrigin: "50% 50%", willChange: "transform" });
  const im = pic(s.img, card, { position: "relative" }, "");
  im.style.boxShadow = "0 50px 120px rgba(0,0,0,.7), 0 6px 18px rgba(0,0,0,.4)";
  if (s.border) im.style.border = `${s.border}px solid #f4f1ea`;
  vignette(root, 0.55);
  const D = s.duration, h = s.height || 900;
  const [fx, fy] = s.focus || [0.5, 0.5];
  return t => {
    const iw = im.naturalWidth || 1, ih = im.naturalHeight || 1;
    const k = Math.min(h / ih, (s.width || 1500) / iw);
    css(im, "width", (iw * k).toFixed(0) + "px");
    const a = eOut5(seg(t, 0, 1.1));
    const p = drift(cl(t / D, 0, 1));
    const z = lerp(1, s.zoom || 1.35, p);
    const cw = iw * k, ch = ih * k;
    /* rise in tilted, settle flat, then the camera pushes toward the focus point */
    const x = W / 2 - cw / 2 - (fx - 0.5) * cw * (z - 1);
    const y = H / 2 - ch / 2 - (fy - 0.5) * ch * (z - 1) + (1 - a) * 260;
    const rx = (1 - a) * 28, rz = lerp(s.rot || -3, (s.rot || -3) * 0.4, p);
    const v = `translate(${x.toFixed(1)}px,${y.toFixed(1)}px) rotateX(${rx.toFixed(2)}deg) rotateZ(${rz.toFixed(2)}deg) scale(${z.toFixed(4)})`;
    css(card, "transform", v);
    setO(card, seg(t, 0, 0.35));
  };
};

SCENES.split = async (s, root) => {
  const halves = [s.left, s.right].map((src, i) => {
    const box = el("div", "abs", root, { left: i ? "960px" : "0", top: "0", width: "960px", height: "1080px", overflow: "hidden" });
    const im = pic(src, box);
    return { box, im };
  });
  const bar = el("div", "abs", root, { left: "957px", top: "0", width: "6px", height: "1080px", background: PAL.cream, boxShadow: "0 0 30px rgba(0,0,0,.6)" });
  vignette(root, 0.45);
  const chips = [s.leftLabel, s.rightLabel].map((txt, i) => txt ? chip(root, txt, i ? 1010 : 70, 950, { at: 0.5 + i * 0.35 }) : () => {});
  const D = s.duration;
  return t => {
    const p = drift(cl(t / D, 0, 1));
    halves.forEach((h, i) => {
      const iw = h.im.naturalWidth || W, ih = h.im.naturalHeight || H;
      const f = (i ? s.rightFocus : s.leftFocus) || [0.5, 0.5];
      const c = coverCam(iw, ih, f[0], f[1], lerp(1.02, 1.1, p), 960, 1080);
      setT(h.im, c.tx, c.ty, c.k);
      const a = eOut5(seg(t, i * 0.25, 0.8));
      setT(h.box, (i ? 1 : -1) * (1 - a) * 400, 0);
      setO(h.box, a);
    });
    css(bar, "height", (eOut(seg(t, 0.2, 0.7)) * 1080).toFixed(0) + "px");
    chips.forEach(f => f(t));
  };
};
