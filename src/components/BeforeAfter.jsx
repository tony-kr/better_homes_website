import { useCallback, useRef, useState } from 'react';
import './BeforeAfter.css';

/*
  A before/after pair under one draggable divider. Works with a mouse, a finger
  and the arrow keys, so the comparison is reachable however someone is reading.
*/
const BeforeAfter = ({ before, after, alt, caption }) => {
  const frameRef = useRef(null);
  const [split, setSplit] = useState(50);
  const [dragging, setDragging] = useState(false);

  const setFromClientX = useCallback((clientX) => {
    const el = frameRef.current;
    if (!el) return;
    const { left, width } = el.getBoundingClientRect();
    const pct = ((clientX - left) / width) * 100;
    setSplit(Math.min(100, Math.max(0, pct)));
  }, []);

  const onPointerDown = (e) => {
    setDragging(true);
    e.currentTarget.setPointerCapture?.(e.pointerId);
    setFromClientX(e.clientX);
  };

  const onPointerMove = (e) => {
    if (!dragging) return;
    setFromClientX(e.clientX);
  };

  const onPointerUp = (e) => {
    setDragging(false);
    e.currentTarget.releasePointerCapture?.(e.pointerId);
  };

  const onKeyDown = (e) => {
    const step = e.shiftKey ? 10 : 3;
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setSplit((s) => Math.max(0, s - step));
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      setSplit((s) => Math.min(100, s + step));
    }
  };

  return (
    <figure className="ba" data-lenis-prevent>
      <div
        className={`ba-frame ${dragging ? 'is-dragging' : ''}`}
        ref={frameRef}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        style={{ '--ba-split': `${split}%` }}
      >
        <img className="ba-after" src={after} alt={`${alt} — after`} draggable={false} />
        <div className="ba-before-wrap">
          <img className="ba-before" src={before} alt={`${alt} — before`} draggable={false} />
        </div>

        <span className="annotation ba-tag ba-tag-before">Before</span>
        <span className="annotation ba-tag ba-tag-after">After</span>

        <div
          className="ba-handle"
          role="slider"
          tabIndex={0}
          aria-label={`${alt} — reveal before and after`}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(split)}
          onKeyDown={onKeyDown}
        >
          <span className="ba-handle-line" />
          <span className="ba-handle-grip">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="m9 6-5 6 5 6M15 6l5 6-5 6" />
            </svg>
          </span>
        </div>
      </div>
      {caption && <figcaption className="annotation ba-caption">{caption}</figcaption>}
    </figure>
  );
};

export default BeforeAfter;
