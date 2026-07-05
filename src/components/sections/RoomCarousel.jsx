import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './RoomCarousel.css';

// Each room carries the palette of its own photograph:
// bg is sampled from the image, ink is a deep shade of the same hue.
const rooms = [
  {
    id: 'living-room',
    title: 'Living room',
    description: 'The room the evening belongs to. Low light, deep seating, and sightlines that pull everyone toward the same corner.',
    image: '/living_room_broll.jpeg',
    bg: '#c4b1cf',
    ink: '#2e2139',
    projects: 12
  },
  {
    id: 'bedroom',
    title: 'Bedroom',
    description: 'The quietest room in the home. We shape bedrooms around morning light and evening stillness, in that order.',
    image: '/bedroon_brol.jpg',
    bg: '#c2cdb8',
    ink: '#28331e',
    projects: 15
  },
  {
    id: 'kitchen',
    title: 'Kitchen',
    description: 'Where the home actually lives. Working surfaces, honest materials, and a lamp left on over the island.',
    image: '/kitchen_broll.jpg',
    bg: '#e8e6e3',
    ink: '#2b2825',
    projects: 8
  },
  {
    id: 'dining',
    title: 'Dining',
    description: 'One long table, light centered above it, and room enough for the conversation to run late.',
    image: '/dining_broll.jpg',
    bg: '#d4937a',
    ink: '#3d1a0e',
    projects: 10
  },
  {
    id: 'patio',
    title: 'Patio',
    description: 'The room without a roof. We treat outdoor space as floor plan, not leftover garden.',
    image: '/patio_broll.jpg',
    bg: '#d9c88e',
    ink: '#3a2f10',
    projects: 6
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
                03 <span className="tick">/</span> 04 — The spaces
              </span>
              <h2 className="carousel-title"><em>{room.title}</em></h2>
              <p className="carousel-description">{room.description}</p>
              <div className="carousel-meta annotation">
                <span>{String(room.projects).padStart(2, '0')} projects delivered</span>
              </div>
              <a href={`/gallery/${room.id}`} className="btn-primary carousel-btn">
                See {room.title.toLowerCase()} projects
                <span className="arrow">→</span>
              </a>
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
                Fig. {String(activeIndex + 1).padStart(2, '0')} — {room.title}, dusk
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
    </section>
  );
};

export default RoomCarousel;
