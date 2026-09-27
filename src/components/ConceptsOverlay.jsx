import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getLenis } from '../lib/scroll';
import './ConceptsOverlay.css';

/*
  Concept boards for one room — the ideas stage, not delivered work.
  Built work lives in the gallery, and the note at the top says so.
*/
const ConceptsOverlay = ({ room, open, onClose }) => {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    getLenis()?.stop();
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = prevOverflow;
      getLenis()?.start();
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && room && (
        <motion.div
          className="concepts-overlay"
          role="dialog"
          aria-modal="true"
          aria-label={`${room.label} concepts`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.35 }}
        >
          <div className="concepts-scroll" data-lenis-prevent>
            <div className="concepts-header">
              <div>
                <p className="annotation concepts-eyebrow">
                  Concept boards <span className="tick">/</span> {room.label}
                </p>
                <h3 className="concepts-title">
                  {room.label} <em>concepts</em>.
                </h3>
                <p className="annotation concepts-note">
                  Inspiration boards — for the homes we actually built, visit the{' '}
                  <a href={`#/gallery?room=${room.galleryFilter}`}>gallery</a>
                </p>
              </div>
              <button
                className="concepts-close"
                onClick={onClose}
                aria-label="Close concepts"
              >
                ×
              </button>
            </div>

            <div className="concepts-grid">
              {room.concepts.map((src, i) => (
                <motion.figure
                  className="concepts-card"
                  key={src}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    duration: 0.5,
                    delay: 0.08 + i * 0.06,
                    ease: [0.22, 1, 0.36, 1]
                  }}
                >
                  <img
                    src={src}
                    alt={`${room.label} concept ${i + 1}`}
                    loading="lazy"
                    draggable={false}
                  />
                  <figcaption className="annotation concepts-caption">
                    Concept {String(i + 1).padStart(2, '0')} — {room.label}
                  </figcaption>
                </motion.figure>
              ))}
            </div>

            <div className="concepts-footer">
              <p className="annotation">
                Ready to see the built version? <span className="tick">→</span>
              </p>
              <a className="btn-primary" href={`#/gallery?room=${room.galleryFilter}`}>
                {room.label} projects <span className="arrow">→</span>
              </a>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ConceptsOverlay;
