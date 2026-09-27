import { useEffect, useRef, useState } from 'react';
import './LaserPointer.css';

/*
  Cursor: a red dot on the pointer and a thin ring that eases after it. Over
  anything clickable the ring opens up, so the page answers the hand before
  the click. Pointer devices only; touch never sees it.
*/
const LaserPointer = () => {
  const [enabled, setEnabled] = useState(false);
  const dotRef = useRef(null);
  const glowRef = useRef(null);

  useEffect(() => {
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setEnabled(fine.matches && !reduced.matches);
    update();
    fine.addEventListener('change', update);
    reduced.addEventListener('change', update);
    return () => {
      fine.removeEventListener('change', update);
      reduced.removeEventListener('change', update);
    };
  }, []);

  useEffect(() => {
    if (!enabled) return;

    const dot = dotRef.current;
    const glow = glowRef.current;
    const target = { x: -100, y: -100 };
    const trail = { x: -100, y: -100 };
    let visible = false;
    let raf;

    const onMove = (e) => {
      target.x = e.clientX;
      target.y = e.clientY;
      if (!visible) {
        visible = true;
        trail.x = e.clientX;
        trail.y = e.clientY;
        dot.style.opacity = '1';
        glow.style.opacity = '1';
      }
    };

    const onLeave = () => {
      visible = false;
      dot.style.opacity = '0';
      glow.style.opacity = '0';
    };

    const onDown = () => dot.classList.add('is-pressed');
    const onUp = () => dot.classList.remove('is-pressed');
    const onOver = (e) => {
      const hot = e.target.closest?.('a, button, [role="button"], input, select, textarea, label');
      glow.classList.toggle('is-hot', Boolean(hot));
    };

    const tick = () => {
      // The dot sits on the cursor; the ring eases after it
      trail.x += (target.x - trail.x) * 0.2;
      trail.y += (target.y - trail.y) * 0.2;
      dot.style.transform = `translate3d(${target.x}px, ${target.y}px, 0) translate(-50%, -50%)`;
      glow.style.transform = `translate3d(${trail.x}px, ${trail.y}px, 0) translate(-50%, -50%)`;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    window.addEventListener('pointermove', onMove, { passive: true });
    window.addEventListener('pointerover', onOver, { passive: true });
    window.addEventListener('pointerdown', onDown);
    window.addEventListener('pointerup', onUp);
    document.documentElement.addEventListener('pointerleave', onLeave);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerover', onOver);
      window.removeEventListener('pointerdown', onDown);
      window.removeEventListener('pointerup', onUp);
      document.documentElement.removeEventListener('pointerleave', onLeave);
    };
  }, [enabled]);

  if (!enabled) return null;

  return (
    <div className="laser-pointer" aria-hidden="true">
      <div ref={glowRef} className="laser-glow" />
      <div ref={dotRef} className="laser-dot" />
    </div>
  );
};

export default LaserPointer;
