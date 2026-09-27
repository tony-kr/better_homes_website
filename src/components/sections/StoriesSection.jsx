import { useCallback, useEffect, useRef, useState } from 'react';
import { motion, useInView, useReducedMotion } from 'framer-motion';
import { featuredPhoto } from '../../data/projectPhotos';
import { sheetNumber } from '../../data/journey';
import { MaskReveal, rise } from '../motion';
import './StoriesSection.css';

const sheet = sheetNumber('stories');

/*
  Client stories — "What Our Clients Say" from betterhomesindia.in, retold in
  the site's voice. Priya's story is verbatim from the current website.

  Laid out after the client's reference (the Experiences cards on
  hotelaurelia.online): tall photographic cards on a horizontal track, each
  set at a slight tilt, the quote and name over a dark fade at the foot. The
  track moves on by itself every few seconds; a red rule under the counter
  shows the time left. It holds while a card is pointed at or focused, and
  when the section is off screen. Arrows, a click on any card, or a swipe
  take over. The photographs are the studio's own work.
*/
const stories = [
  {
    name: 'Priya Sharma',
    initials: 'PS',
    project: '3BHK · Whitefield',
    scope: 'Full home interior',
    photo: 2,
    quote:
      'Better Homes transformed our 3BHK into a dream space. The modular kitchen is stunning, and the team delivered everything on time. The 3D visualization helped us make confident decisions.'
  },
  {
    name: 'Rajesh & Kavitha Menon',
    initials: 'RM',
    project: 'Full home · Koramangala',
    scope: 'Wardrobes, TV unit, kitchen',
    photo: 7,
    quote:
      'From the first sketch to the final handover, everything was transparent — budget, timeline, materials. The wardrobes and TV unit look exactly like the design we approved.'
  },
  {
    name: 'Ananya Iyer',
    initials: 'AI',
    project: 'Modular kitchen · HSR Layout',
    scope: 'Modular kitchen',
    photo: 34,
    quote:
      'They understood how we actually cook. The kitchen is beautiful, but more importantly it works — every shelf, every drawer is where our hands expect it to be.'
  },
  {
    name: 'Mohammed Faisal',
    initials: 'MF',
    project: '2BHK · Electronic City',
    scope: 'Full home interior',
    photo: 44,
    quote:
      'We handed over an empty flat and got back a home. The pooja unit they designed is the first thing every guest asks about.'
  }
];

const AUTO_ADVANCE_MS = 5500;
const TILTS = [-2.2, 1.6, -1.2, 2];

const Stars = () => (
  <span className="story-stars" aria-label="Five out of five">
    {[0, 1, 2, 3, 4].map((i) => (
      <svg key={i} width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="m12 2 2.9 6.26 6.85.72-5.12 4.6 1.45 6.72L12 16.9l-6.08 3.4 1.45-6.72L2.25 8.98l6.85-.72L12 2z" />
      </svg>
    ))}
  </span>
);

const StoriesSection = () => {
  const sectionRef = useRef(null);
  const onScreen = useInView(sectionRef, { amount: 0.35 });
  const [active, setActive] = useState(0);
  const [hold, setHold] = useState(false);
  const [tick, setTick] = useState(0); // restarts the progress rule
  const reduced = useReducedMotion();
  const swipe = useRef(null);
  const trackRef = useRef(null);
  const [offset, setOffset] = useState(0);

  // Slide so the active card sits at the start of the track
  useEffect(() => {
    const measure = () => {
      const card = trackRef.current?.children[active];
      if (card) setOffset(card.offsetLeft);
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [active]);

  const go = useCallback((next) => {
    setActive((next + stories.length) % stories.length);
    setTick((t) => t + 1);
  }, []);

  const running = onScreen && !hold && !reduced;

  useEffect(() => {
    if (!running) return undefined;
    const id = setTimeout(() => go(active + 1), AUTO_ADVANCE_MS);
    return () => clearTimeout(id);
  }, [running, active, tick, go]);

  // A hidden tab should not burn through the stories
  useEffect(() => {
    const onVis = () => setHold(document.hidden);
    document.addEventListener('visibilitychange', onVis);
    return () => document.removeEventListener('visibilitychange', onVis);
  }, []);

  const onPointerDown = (e) => { swipe.current = e.clientX; };
  const onPointerUp = (e) => {
    if (swipe.current == null) return;
    const dx = e.clientX - swipe.current;
    swipe.current = null;
    if (Math.abs(dx) > 50) go(active + (dx < 0 ? 1 : -1));
  };

  return (
    <section ref={sectionRef} className="stories-section" aria-roledescription="carousel" aria-label="Client stories">
      <div className="stories-content">
        <header className="stories-header">
          <div>
            <motion.p className="annotation stories-eyebrow" {...rise(0)}>
              {sheet.n} <span className="tick">/</span> {sheet.total} — Client stories
            </motion.p>
            <MaskReveal className="stories-title">
              In their <span className="accent">own words</span><span className="dot">.</span>
            </MaskReveal>
          </div>

          <motion.div className="stories-controls" {...rise(0.2)}>
            <span className="stories-counter" aria-live="polite">
              <span className="stories-counter-now">{String(active + 1).padStart(2, '0')}</span>
              <span className="stories-counter-sep">/</span>
              {String(stories.length).padStart(2, '0')}
            </span>
            <span className="stories-progress" aria-hidden="true">
              <span
                key={`${active}-${tick}`}
                className={`stories-progress-fill ${running ? 'is-running' : ''}`}
                style={{ '--dur': `${AUTO_ADVANCE_MS}ms` }}
              />
            </span>
            <button className="stories-arrow" onClick={() => go(active - 1)} aria-label="Previous story">
              <span aria-hidden="true">←</span>
            </button>
            <button className="stories-arrow" onClick={() => go(active + 1)} aria-label="Next story">
              <span aria-hidden="true">→</span>
            </button>
          </motion.div>
        </header>

        <div
          className="stories-viewport"
          onMouseEnter={() => setHold(true)}
          onMouseLeave={() => setHold(false)}
          onFocusCapture={() => setHold(true)}
          onBlurCapture={() => setHold(false)}
          onPointerDown={onPointerDown}
          onPointerUp={onPointerUp}
          onPointerCancel={() => { swipe.current = null; }}
        >
          <motion.ol
            ref={trackRef}
            className="stories-track"
            animate={{ x: -offset }}
            transition={{ duration: reduced ? 0 : 1.1, ease: [0.16, 1, 0.3, 1] }}
          >
            {stories.map((s, i) => {
              const on = i === active;
              return (
                <motion.li
                  key={s.name}
                  className={`story-card ${on ? 'is-active' : ''}`}
                  initial={{ opacity: 0, y: 60, rotate: TILTS[i % TILTS.length] * 2 }}
                  whileInView={{ opacity: 1, y: 0, rotate: TILTS[i % TILTS.length] }}
                  viewport={{ once: true, amount: 0.2 }}
                  transition={{ duration: 1.1, delay: 0.1 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                  aria-roledescription="slide"
                  aria-label={`${i + 1} of ${stories.length}: ${s.name}`}
                  aria-current={on ? 'true' : undefined}
                >
                  <div className="story-card-inner">
                  <button className="story-card-hit" onClick={() => go(i)} tabIndex={on ? -1 : 0} aria-label={`Show ${s.name}'s story`} />
                  <img className="story-card-photo" src={featuredPhoto(s.photo)} alt="" draggable={false} loading="lazy" />
                  <div className="story-card-body">
                    <span className="story-card-index annotation">
                      {String(i + 1).padStart(2, '0')} / {String(stories.length).padStart(2, '0')}
                    </span>
                    <blockquote className="story-card-quote">
                      <span className="story-card-mark" aria-hidden="true">&ldquo;</span>
                      {s.quote}
                    </blockquote>
                    <div className="story-card-foot">
                      <Stars />
                      <p className="story-card-name">{s.name}</p>
                      <p className="story-card-meta annotation">{s.scope} · {s.project.split(' · ').pop()}</p>
                    </div>
                  </div>
                  </div>
                </motion.li>
              );
            })}
          </motion.ol>
        </div>
      </div>
    </section>
  );
};

export default StoriesSection;
