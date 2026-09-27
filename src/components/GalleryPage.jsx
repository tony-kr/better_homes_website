import { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  projectPhotos,
  galleryTabs,
  roomFilters,
  roomLabel,
  planShots,
  beforeAfterPairs
} from '../data/projectPhotos';
import BeforeAfter from './BeforeAfter';
import { WhatsAppIcon } from './icons';
import { whatsappLink } from '../data/contact';
import './GalleryPage.css';

/*
  Gallery — its own page (#/gallery), in three tabs: the delivered work, the
  drawings and 3D views behind it, and before/after pairs.

  A room stop on the home page can still deep link into a single room
  ('#/gallery?room=kitchen'); that shows as a removable chip rather than a row
  of room buttons.
*/

const queryOf = () => new URLSearchParams(window.location.hash.split('?')[1] || '');

const tabFromHash = () => {
  const t = queryOf().get('tab');
  return galleryTabs.some((x) => x.id === t) ? t : 'works';
};

const roomFromHash = () => {
  const r = queryOf().get('room');
  return roomFilters.some((f) => f.id === r) ? r : null;
};

/* A designed holding state, so a tab without assets still reads as finished. */
const EmptyTab = ({ title, body, cta, message }) => (
  <motion.div
    className="gallery-empty"
    initial={{ opacity: 0, y: 22 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
  >
    <span className="gallery-empty-rule" aria-hidden="true" />
    <h2 className="gallery-empty-title">{title}</h2>
    <p className="gallery-empty-body">{body}</p>
    <a
      className="btn-whatsapp gallery-empty-cta"
      href={whatsappLink(message)}
      target="_blank"
      rel="noreferrer"
    >
      <WhatsAppIcon size={20} />
      <span>{cta}</span>
      <span className="arrow">→</span>
    </a>
  </motion.div>
);

const GalleryPage = () => {
  const [tab, setTab] = useState(tabFromHash);
  const [room, setRoom] = useState(roomFromHash);

  // Arriving from a room stop while already on this page re-filters in place
  useEffect(() => {
    const onHash = () => {
      setTab(tabFromHash());
      setRoom(roomFromHash());
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const meta = galleryTabs.find((t) => t.id === tab) || galleryTabs[0];

  const visible = useMemo(
    () => (room ? projectPhotos.filter((p) => p.room === room) : projectPhotos),
    [room]
  );

  const selectTab = (id) => {
    setTab(id);
    // The room chip only makes sense over the photographs
    const keepRoom = id === 'works' ? room : null;
    if (!keepRoom) setRoom(null);
    const q = [id === 'works' ? null : `tab=${id}`, keepRoom ? `room=${keepRoom}` : null]
      .filter(Boolean)
      .join('&');
    const next = q ? `#/gallery?${q}` : '#/gallery';
    if (window.location.hash !== next) window.history.replaceState(null, '', next);
  };

  const clearRoom = () => {
    setRoom(null);
    window.history.replaceState(null, '', tab === 'works' ? '#/gallery' : `#/gallery?tab=${tab}`);
  };

  return (
    <main className="gallery-page">
      <header className="gallery-page-header">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        >
          <a href="#/" className="btn-ghost gallery-back">
            <span className="arrow">←</span> Back to home
          </a>
          <p className="annotation gallery-page-eyebrow">
            Gallery <span className="tick">/</span> {meta.label}
          </p>
          <h1 className="gallery-page-title">
            Real homes, <em>really built</em>.
          </h1>
          <AnimatePresence mode="wait">
            <motion.p
              key={meta.id}
              className="gallery-page-lede"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.3 }}
            >
              {meta.blurb}
            </motion.p>
          </AnimatePresence>
        </motion.div>

        <motion.div
          className="gallery-tabs"
          role="tablist"
          aria-label="Gallery sections"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
        >
          {galleryTabs.map((t) => {
            const on = t.id === tab;
            return (
              <button
                key={t.id}
                role="tab"
                aria-selected={on}
                className={`gallery-tab ${on ? 'active' : ''}`}
                onClick={() => selectTab(t.id)}
              >
                {t.label}
                {on && (
                  <motion.span
                    className="gallery-tab-underline"
                    layoutId="gallery-tab-underline"
                    transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                  />
                )}
              </button>
            );
          })}
        </motion.div>

        {/* Deep-linked from a room stop */}
        <AnimatePresence>
          {tab === 'works' && room && (
            <motion.div
              className="gallery-chip-row"
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.3 }}
            >
              <span className="annotation gallery-chip">
                {roomLabel(room)}
                <span className="gallery-chip-count">{visible.length}</span>
                <button
                  className="gallery-chip-clear"
                  onClick={clearRoom}
                  aria-label="Show all work"
                >
                  ×
                </button>
              </span>
              <span className="annotation gallery-chip-note">
                Showing one room — clear the chip for everything
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      <AnimatePresence mode="wait">
        {tab === 'works' && (
          <motion.div
            key={`works-${room || 'all'}`}
            className="gallery-page-grid"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          >
            {visible.map((photo, i) => (
              <figure className="gallery-page-card" key={photo.n}>
                <img
                  src={photo.src}
                  alt={`${photo.label} — project ${photo.n}`}
                  loading={i < 6 ? 'eager' : 'lazy'}
                  draggable={false}
                />
                <figcaption className="annotation gallery-page-caption">
                  <span>{photo.label}</span>
                  <span className="tick">Fig. {String(photo.n).padStart(2, '0')}</span>
                </figcaption>
              </figure>
            ))}
          </motion.div>
        )}

        {tab === 'plans' && (
          <motion.div key="plans" className="gallery-panel">
            {planShots.length ? (
              <div className="gallery-page-grid">
                {planShots.map((p, i) => (
                  <figure className="gallery-page-card" key={p.src}>
                    <img src={p.src} alt={p.label} loading={i < 6 ? 'eager' : 'lazy'} />
                    <figcaption className="annotation gallery-page-caption">
                      <span>{p.label}</span>
                      <span className="tick">{p.kind}</span>
                    </figcaption>
                  </figure>
                ))}
              </div>
            ) : (
              <EmptyTab
                title="Drawings and 3D views, coming to this page"
                body="Every project starts as a measured 2D plan and an approved 3D view. We are putting that set together for the website. If you already have a floor plan, send it across and we will come back with a 3D view of your own home."
                cta="Send us your floor plan"
                message={
                  'Hello Better Homes!\n\nI saw the 2D & 3D section on your website. ' +
                  "I'd like to share my floor plan and get a 3D view of my home.\n\n" +
                  'My name:\nWhere the home is:\nSize (e.g. 2BHK, 1200 sq ft):'
                }
              />
            )}
          </motion.div>
        )}

        {tab === 'transform' && (
          <motion.div key="transform" className="gallery-panel">
            {beforeAfterPairs.length ? (
              <div className="gallery-ba-grid">
                {beforeAfterPairs.map((pair) => (
                  <BeforeAfter
                    key={pair.id}
                    before={pair.before}
                    after={pair.after}
                    alt={pair.label}
                    caption={pair.label}
                  />
                ))}
              </div>
            ) : (
              <EmptyTab
                title="Before and after, being photographed now"
                body="We are re-shooting recent handovers from the exact spot the first site photo was taken, so the pairs line up properly. Until they are up, ask us for the before-and-after on any project in Our Works and we will send it."
                cta="Ask for a before & after"
                message={
                  'Hello Better Homes!\n\nI saw the Before & After section on your website. ' +
                  "Could you send me the before-and-after photos for a project you've completed?\n\n" +
                  'The kind of home I am planning:'
                }
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <footer className="gallery-page-footer">
        <p className="annotation">
          Like what you see? <span className="tick">→</span>
        </p>
        <a href="#estimate" className="btn-primary">
          Get free estimate <span className="arrow">→</span>
        </a>
      </footer>
    </main>
  );
};

export default GalleryPage;
