import { useEffect, useMemo, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './GallerySection.css';

// The client's real project photography, by room
const photos = [
  ...[1, 2, 3, 4, 5, 6].map((n) => ({
    src: `/living_room/living-0${n}.${['webp', 'jpg', 'webp', 'avif', 'jpg', 'jpg'][n - 1]}`,
    room: 'living-room',
    label: 'Living room'
  })),
  ...[1, 2, 3, 4, 5, 6, 7].map((n) => ({
    src: `/bedroom/bedroom-0${n}.${['jpg', 'jpg', 'avif', 'jpeg', 'jpeg', 'webp', 'webp'][n - 1]}`,
    room: 'bedroom',
    label: 'Bedroom'
  })),
  ...[1, 2, 3, 4, 5, 6].map((n) => ({
    src: `/kitchen/kitchen-0${n}.${['jpg', 'jpg', 'webp', 'jpg', 'jpeg', 'jpg'][n - 1]}`,
    room: 'kitchen',
    label: 'Kitchen'
  })),
  ...[1, 2, 3, 4, 5, 6].map((n) => ({
    src: `/dining_space/dining-0${n}.${['avif', 'jpg', 'jpeg', 'jpg', 'jpg', 'jpg'][n - 1]}`,
    room: 'dining',
    label: 'Dining'
  })),
  ...[1, 2, 3, 4, 5, 6].map((n) => ({
    src: `/patio/patio-0${n}.${['webp', 'jpeg', 'jpg', 'jpg', 'jpg', 'avif'][n - 1]}`,
    room: 'patio',
    label: 'Patio'
  }))
];

const filters = [
  { id: 'all', label: 'All' },
  { id: 'living-room', label: 'Living room' },
  { id: 'bedroom', label: 'Bedroom' },
  { id: 'kitchen', label: 'Kitchen' },
  { id: 'dining', label: 'Dining' },
  { id: 'patio', label: 'Patio' }
];

const GallerySection = ({ filter = 'all', onFilterChange }) => {
  const sectionRef = useRef(null);
  const trackRef = useRef(null);
  const viewportRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);
  const [dragLimit, setDragLimit] = useState(0);

  const visible = useMemo(
    () => (filter === 'all' ? photos : photos.filter((p) => p.room === filter)),
    [filter]
  );

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setHasEntered(true);
      },
      { threshold: 0.3 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  // Constrain the drag to the real width of the strip
  useEffect(() => {
    const measure = () => {
      if (!trackRef.current || !viewportRef.current) return;
      const overflow = trackRef.current.scrollWidth - viewportRef.current.offsetWidth;
      setDragLimit(Math.max(0, overflow));
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [visible]);

  return (
    <section ref={sectionRef} className="gallery-section">
      <div className="gallery-content">
        <motion.div
          className="gallery-header"
          initial={{ opacity: 0, y: 32 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="gallery-heading">
            <p className="annotation gallery-eyebrow">
              06 <span className="tick">/</span> 08 — Gallery
            </p>
            <h2 className="gallery-title">
              Real homes, <em>real stories</em>.
            </h2>
          </div>

          <div className="gallery-filters" role="tablist" aria-label="Filter photos by room">
            {filters.map((f) => (
              <button
                key={f.id}
                role="tab"
                aria-selected={filter === f.id}
                className={`gallery-filter annotation ${filter === f.id ? 'active' : ''}`}
                onClick={() => onFilterChange?.(f.id)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="gallery-viewport"
          ref={viewportRef}
          initial={{ opacity: 0, y: 40 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={filter}
              className="gallery-track"
              ref={trackRef}
              drag="x"
              dragConstraints={{ left: -dragLimit, right: 0 }}
              dragElastic={0.06}
              initial={{ opacity: 0, x: 60 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            >
              {visible.map((photo, i) => (
                <figure className="gallery-card" key={photo.src}>
                  <img src={photo.src} alt={photo.label} loading="lazy" draggable={false} />
                  <figcaption className="annotation gallery-caption">
                    {photo.label} — Fig. {String(i + 1).padStart(2, '0')}
                  </figcaption>
                </figure>
              ))}
            </motion.div>
          </AnimatePresence>
        </motion.div>

        <motion.p
          className="annotation gallery-hint"
          initial={{ opacity: 0 }}
          animate={hasEntered ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.8 }}
          aria-hidden="true"
        >
          Drag to explore <span className="tick">→</span> Every detail considered, every space lived in
        </motion.p>
      </div>
    </section>
  );
};

export default GallerySection;
