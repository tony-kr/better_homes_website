import { useEffect, useRef } from 'react';
import './PixelLogo.css';

/*
  The logo, built out of pixels (after the client's reference,
  mellowdesigns.co). The mark is cut into a grid of square cells. They arrive
  in a loose left-to-right scatter: first as a single solid square of the
  cell's colour, then as the real piece of the logo. It holds, then shreds
  back into squares and away, and (if `loop`) assembles again.

  The <img> underneath keeps the layout and the accessible name, so any CSS
  that sizes the logo (the header chip shrinking on scroll) still applies;
  the canvas simply redraws to whatever size the image is given. With
  reduced motion, or before the canvas is ready, the plain image shows.
*/
const IN_MS = 650;
const OUT_MS = 520;
const GAP_MS = 220;
const BAND = 0.22; // share of the timeline a cell spends as a bare square

export default function PixelLogo({
  src,
  alt = '',
  className = '',
  imgClassName = '',
  loop = true,
  hold = 2000,
  cells = 16, // rows of cells across the logo's height
  delay = 0,
  ...imgProps
}) {
  const imgRef = useRef(null);
  const canvasRef = useRef(null);
  const wrapRef = useRef(null);

  useEffect(() => {
    const img = imgRef.current;
    const canvas = canvasRef.current;
    const wrap = wrapRef.current;
    if (!img || !canvas || !wrap) return undefined;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined;

    const ctx = canvas.getContext('2d');
    const off = document.createElement('canvas');
    const octx = off.getContext('2d', { willReadFrequently: true });
    let grid = []; // { x, y, s, t, color }
    let raf = 0;
    let ready = false;
    let phase = 'wait';
    let phaseStart = performance.now() + delay;
    let lastP = -1;

    // Cut the logo into cells at its current on-screen size
    const build = () => {
      const w = img.clientWidth;
      const h = img.clientHeight;
      if (!w || !h || !img.naturalWidth) return false;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const W = Math.round(w * dpr);
      const H = Math.round(h * dpr);
      canvas.width = off.width = W;
      canvas.height = off.height = H;
      octx.clearRect(0, 0, W, H);
      octx.drawImage(img, 0, 0, W, H);
      const data = octx.getImageData(0, 0, W, H).data;
      const s = Math.max(2, Math.round(H / cells));
      grid = [];
      for (let y = 0; y < H; y += s) {
        for (let x = 0; x < W; x += s) {
          let r = 0, g = 0, b = 0, a = 0, n = 0;
          // Sample a few points rather than every pixel
          for (let yy = y; yy < Math.min(y + s, H); yy += Math.max(1, s >> 2)) {
            for (let xx = x; xx < Math.min(x + s, W); xx += Math.max(1, s >> 2)) {
              const i = (yy * W + xx) * 4;
              const al = data[i + 3];
              n++;
              if (al > 24) { r += data[i]; g += data[i + 1]; b += data[i + 2]; a++; }
            }
          }
          if (a / n < 0.12) continue;
          // Mostly random, drifting left to right
          const t = (Math.random() * 0.7 + (x / W) * 0.3) * (1 - BAND);
          grid.push({ x, y, s, t, color: `rgb(${(r / a) | 0},${(g / a) | 0},${(b / a) | 0})` });
        }
      }
      lastP = -1;
      return true;
    };

    const draw = (p) => {
      if (p === lastP) return;
      lastP = p;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (p >= 1) {
        ctx.drawImage(off, 0, 0);
        return;
      }
      for (const c of grid) {
        if (c.t + BAND < p) {
          ctx.drawImage(off, c.x, c.y, c.s, c.s, c.x, c.y, c.s, c.s);
        } else if (c.t < p) {
          // A bare square, smaller than the cell, so the edge reads as dust
          const k = c.s * 0.62;
          ctx.fillStyle = c.color;
          ctx.fillRect(c.x + (c.s - k) / 2, c.y + (c.s - k) / 2, k, k);
        }
      }
    };

    const ease = (x) => 1 - Math.pow(1 - x, 2);

    const tick = (now) => {
      raf = requestAnimationFrame(tick);
      if (!ready) return;
      const e = now - phaseStart;
      if (phase === 'wait') {
        draw(0);
        if (e >= 0) { phase = 'in'; phaseStart = now; }
      } else if (phase === 'in') {
        draw(ease(Math.min(1, e / IN_MS)));
        if (e >= IN_MS) { phase = 'hold'; phaseStart = now; }
      } else if (phase === 'hold') {
        draw(1);
        if (loop && e >= hold) { phase = 'out'; phaseStart = now; }
        else if (!loop) cancelAnimationFrame(raf);
      } else if (phase === 'out') {
        draw(1 - ease(Math.min(1, e / OUT_MS)));
        if (e >= OUT_MS) { phase = 'gap'; phaseStart = now; }
      } else if (phase === 'gap') {
        draw(0);
        if (e >= GAP_MS) { phase = 'in'; phaseStart = now; }
      }
    };

    const start = () => {
      if (!build()) return;
      ready = true;
      wrap.classList.add('is-pixel');
    };

    if (img.complete && img.naturalWidth) start();
    else img.addEventListener('load', start, { once: true });

    // The header chip changes size on scroll; recut at the new size
    const ro = new ResizeObserver(() => {
      if (!ready) return;
      build();
      if (phase === 'hold' && !loop) draw(1);
    });
    ro.observe(img);

    // No point animating a hidden tab
    const onVis = () => {
      cancelAnimationFrame(raf);
      if (!document.hidden && !(phase === 'hold' && !loop)) {
        phaseStart = performance.now();
        raf = requestAnimationFrame(tick);
      }
    };
    document.addEventListener('visibilitychange', onVis);
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      img.removeEventListener('load', start);
      document.removeEventListener('visibilitychange', onVis);
      wrap.classList.remove('is-pixel');
    };
  }, [src, loop, hold, cells, delay]);

  return (
    <span ref={wrapRef} className={`pixel-logo ${className}`}>
      <img ref={imgRef} src={src} alt={alt} className={imgClassName} draggable={false} {...imgProps} />
      <canvas ref={canvasRef} className="pixel-logo-canvas" aria-hidden="true" />
    </span>
  );
}
