import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { projectPhotos, galleryFilters } from '../data/projectPhotos';
import './GalleryPage.css';

/*
  Gallery — its own page (#/gallery). Every photo here is the client's
  actual delivered work from /assets; concepts live in the Spaces section.
*/
const GalleryPage = () => {
  const [filter, setFilter] = useState('all');

  const visible = useMemo(
    () => (filter === 'all' ? projectPhotos : projectPhotos.filter((p) => p.room === filter)),
    [filter]
  );

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
            Gallery <span className="tick">/</span> Delivered work
          </p>
          <h1 className="gallery-page-title">
            Real homes, <em>really built</em>.
          </h1>
          <p className="gallery-page-lede">
            No renders, no stock photography — every frame below was shot on
            site in a home we delivered.
          </p>
        </motion.div>

        <motion.div
          className="gallery-page-filters"
          role="tablist"
          aria-label="Filter photos by room"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
        >
          {galleryFilters.map((f) => (
            <button
              key={f.id}
              role="tab"
              aria-selected={filter === f.id}
              className={`gallery-page-filter annotation ${filter === f.id ? 'active' : ''}`}
              onClick={() => setFilter(f.id)}
            >
              {f.label}
              <span className="filter-count">
                {f.id === 'all'
                  ? projectPhotos.length
                  : projectPhotos.filter((p) => p.room === f.id).length}
              </span>
            </button>
          ))}
        </motion.div>
      </header>

      <AnimatePresence mode="wait">
        <motion.div
          key={filter}
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
