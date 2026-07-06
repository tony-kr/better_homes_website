import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getLenis } from '../../lib/scroll';
import './RoomCarousel.css';

// Each room carries the palette of its own photograph:
// bg is sampled from the image, ink is a deep shade of the same hue.
// concepts are the mood/inspiration boards; delivered work lives in the Gallery.
const rooms = [
  {
    id: 'living-room',
    title: 'Living room',
    description: 'The room the evening belongs to. Low light, deep seating, and sightlines that pull everyone toward the same corner.',
    image: '/living_room_broll.jpeg',
    bg: '#c4b1cf',
    ink: '#2e2139',
    projects: 12,
    concepts: ['/living_room/living-01.webp', '/living_room/living-02.jpg', '/living_room/living-03.webp', '/living_room/living-04.avif', '/living_room/living-05.jpg', '/living_room/living-06.jpg']
  },
  {
    id: 'bedroom',
    title: 'Bedroom',
    description: 'The quietest room in the home. We shape bedrooms around morning light and evening stillness, in that order.',
    image: '/bedroon_brol.jpg',
    bg: '#c2cdb8',
    ink: '#28331e',
    projects: 15,
    concepts: ['/bedroom/bedroom-01.jpg', '/bedroom/bedroom-02.jpg', '/bedroom/bedroom-03.avif', '/bedroom/bedroom-04.jpeg', '/bedroom/bedroom-05.jpeg', '/bedroom/bedroom-06.webp', '/bedroom/bedroom-07.webp']
  },
  {
    id: 'kitchen',
    title: 'Kitchen',
    description: 'Where the home actually lives. Working surfaces, honest materials, and a lamp left on over the island.',
    image: '/kitchen_broll.jpg',
    bg: '#e8e6e3',
    ink: '#2b2825',
    projects: 8,
    concepts: ['/kitchen/kitchen-01.jpg', '/kitchen/kitchen-02.jpg', '/kitchen/kitchen-03.webp', '/kitchen/kitchen-04.jpg', '/kitchen/kitchen-05.jpeg', '/kitchen/kitchen-06.jpg']
  },
  {
    id: 'dining',
    title: 'Dining',
    description: 'One long table, light centered above it, and room enough for the conversation to run late.',
    image: '/dining_broll.jpg',
    bg: '#d4937a',
    ink: '#3d1a0e',
    projects: 10,
    concepts: ['/dining_space/dining-01.avif', '/dining_space/dining-02.jpg', '/dining_space/dining-03.jpeg', '/dining_space/dining-04.jpg', '/dining_space/dining-05.jpg', '/dining_space/dining-06.jpg']
  },
  {
    id: 'patio',
    title: 'Patio',
    description: 'The room without a roof. We treat outdoor space as floor plan, not leftover garden.',
    image: '/patio_broll.jpg',
    bg: '#d9c88e',
    ink: '#3a2f10',
    projects: 6,
    concepts: ['/patio/patio-01.webp', '/patio/patio-02.jpeg', '/patio/patio-03.jpg', '/patio/patio-04.jpg', '/patio/patio-05.jpg', '/patio/patio-06.avif']
  }
];

const slideVariants = {
  enter: (direction) => ({
    x: direction > 0 ? 320 : -320,
    opacity: 0,
    scale: 0.92
  }),
  center: {
    x: 0,
    opacity: 1,
    scale: 1
  },
  exit: (direction) => ({
    x: direction > 0 ? -320 : 320,
    opacity: 0,
    scale: 0.92
  })
};

const infoVariants = {
  enter: (direction) => ({
    x: direction > 0 ? 48 : -48,
    opacity: 0
  }),
  center: {
    x: 0,
    opacity: 1
  },
  exit: (direction) => ({
    x: direction > 0 ? -48 : 48,
    opacity: 0
  })
};

const RoomCarousel = () => {
  const [[activeIndex, direction], setState] = useState([0, 0]);
  const [conceptsOpen, setConceptsOpen] = useState(false);

  // While the boards are open, the page behind holds still
  useEffect(() => {
    if (!conceptsOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') setConceptsOpen(false);
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
  }, [conceptsOpen]);

  const paginate = (newDirection) => {
    const newIndex = activeIndex + newDirection;
    if (newIndex >= 0 && newIndex < rooms.length) {
      setState([newIndex, newDirection]);
    }
  };

  const goTo = (index) => {
    setState([index, index > activeIndex ? 1 : -1]);
  };

  const room = rooms[activeIndex];

  return (
    <section className="room-carousel" style={{ '--room-ink': room.ink }}>
      {/* The whole section takes on the palette of the active photograph */}
      <motion.div
        className="carousel-bg"
        animate={{ backgroundColor: room.bg }}
        transition={{ duration: 0.9, ease: 'easeInOut' }}
        aria-hidden="true"
      />

      <div className="carousel-layout">
        {/* Left: Room info */}
        <div className="carousel-info-side">
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div
              key={room.id}
              className="carousel-info"
              custom={direction}
              variants={infoVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
            >
              <span className="annotation carousel-counter">
                04 <span className="tick">/</span> 08 — The spaces
              </span>
              <h2 className="carousel-title"><em>{room.title}</em></h2>
              <p className="carousel-description">{room.description}</p>
              <div className="carousel-meta annotation">
                <span>{String(room.projects).padStart(2, '0')} projects delivered</span>
              </div>
              <button
                className="btn-primary carousel-btn"
                onClick={() => setConceptsOpen(true)}
              >
                See {room.title.toLowerCase()} concepts
                <span className="arrow">→</span>
              </button>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Right: Room image */}
        <div className="carousel-card-side">
          <AnimatePresence mode="wait" custom={direction}>
            <motion.figure
              key={room.id}
              className="carousel-card"
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
            >
              <img src={room.image} alt={room.title} draggable={false} />
              <figcaption className="annotation card-caption">
                Fig. {String(activeIndex + 1).padStart(2, '0')} — {room.title}, concept
              </figcaption>
            </motion.figure>
          </AnimatePresence>
        </div>
      </div>

      {/* Navigation */}
      <div className="carousel-nav">
        <button
          className="carousel-arrow"
          onClick={() => paginate(-1)}
          disabled={activeIndex === 0}
          aria-label="Previous room"
        >
          &larr;
        </button>

        <div className="carousel-dots">
          {rooms.map((r, i) => (
            <button
              key={r.id}
              className={`carousel-dot ${i === activeIndex ? 'active' : ''}`}
              onClick={() => goTo(i)}
              aria-label={r.title}
            />
          ))}
        </div>

        <button
          className="carousel-arrow"
          onClick={() => paginate(1)}
          disabled={activeIndex === rooms.length - 1}
          aria-label="Next room"
        >
          &rarr;
        </button>
      </div>

      {/* Concept boards — inspiration imagery; the Gallery holds delivered work */}
      <AnimatePresence>
        {conceptsOpen && (
          <motion.div
            className="concepts-overlay"
            role="dialog"
            aria-modal="true"
            aria-label={`${room.title} concepts`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.35 }}
          >
            <div className="concepts-scroll" data-lenis-prevent>
              <div className="concepts-header">
                <div>
                  <p className="annotation concepts-eyebrow">
                    Concept boards <span className="tick">/</span> {room.title}
                  </p>
                  <h3 className="concepts-title">
                    {room.title} <em>concepts</em>.
                  </h3>
                  <p className="annotation concepts-note">
                    Inspiration boards — for the homes we actually built, visit the{' '}
                    <a href="#/gallery">gallery</a>
                  </p>
                </div>
                <button
                  className="concepts-close"
                  onClick={() => setConceptsOpen(false)}
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
                    transition={{ duration: 0.5, delay: 0.08 + i * 0.06, ease: [0.22, 1, 0.36, 1] }}
                  >
                    <img src={src} alt={`${room.title} concept ${i + 1}`} loading="lazy" draggable={false} />
                    <figcaption className="annotation concepts-caption">
                      Concept {String(i + 1).padStart(2, '0')} — {room.title}
                    </figcaption>
                  </motion.figure>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
};

export default RoomCarousel;
