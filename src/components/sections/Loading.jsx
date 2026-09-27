import React, { useEffect, useRef, useState } from 'react';
import { useLoading } from '../../context/LoadingContext';
import './Loading.css';

/*
  Splash screen.

  The number on screen never jumps. `percent` is what the loaders report,
  and it can arrive as 100 at once when the house is already cached; the
  display counts up toward it at a steady pace instead, so the splash always
  reads as a short, deliberate count rather than a flash of "100%".

  When the count lands and the hero image is decoded, the panel lifts away
  like a curtain to reveal the landing plate underneath. No colour floods the
  screen on the way out.
*/
const MIN_SHOW_MS = 1600;   // never shorter than this, cached or not
const RATE = 62;            // display percent per second, at most

const Loading = ({ percent, ready = true }) => {
  const { setIsLoading } = useLoading();
  const [shown, setShown] = useState(0);
  const [leaving, setLeaving] = useState(false);
  const target = useRef(0);
  const start = useRef(performance.now());

  target.current = percent;

  // Count toward the reported value, capped per frame, never backwards.
  useEffect(() => {
    let raf;
    let last = performance.now();
    const tick = (now) => {
      const dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      // Hold short of 100 until the minimum time has passed
      const elapsed = now - start.current;
      const cap = elapsed < MIN_SHOW_MS ? Math.min(96, (elapsed / MIN_SHOW_MS) * 100) : 100;
      setShown((s) => {
        const goal = Math.min(target.current, cap);
        return s >= goal ? s : Math.min(goal, s + RATE * dt);
      });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  const done = shown >= 100 && ready;

  useEffect(() => {
    if (!done || leaving) return;
    const lift = setTimeout(() => setLeaving(true), 350);
    return () => clearTimeout(lift);
  }, [done, leaving]);

  useEffect(() => {
    if (!leaving) return;
    const gone = setTimeout(() => setIsLoading(false), 1150);
    return () => clearTimeout(gone);
  }, [leaving, setIsLoading]);

  const value = Math.floor(shown);

  return (
    <div className={`splash ${leaving ? 'splash-leaving' : ''}`} role="status" aria-live="polite">
      <div className="splash-inner">
        <img className="splash-logo" src="/bh-logo.png" alt="Better Homes" />
      </div>

      <div className="splash-foot">
        <span className="splash-count" aria-label={`Loading ${value} percent`}>
          {value}
          <span className="splash-pct">%</span>
        </span>
        <span className="splash-caption">
          Interior design <span className="splash-dot" aria-hidden="true" /> Bengaluru
        </span>
      </div>
      <div className="splash-bar" aria-hidden="true">
        <span style={{ transform: `scaleX(${shown / 100})` }} />
      </div>
    </div>
  );
};

export default Loading;
