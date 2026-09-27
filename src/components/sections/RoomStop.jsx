import { useState } from 'react';
import { motion } from 'framer-motion';
import ConceptsOverlay from '../ConceptsOverlay';
import { MaskReveal } from '../motion';
import './RoomStop.css';

/*
  One stop on the walk. The section itself is transparent — the 3D house is
  the background — so this is only the plate of copy and the two ways out:
  the delivered work for this room, and the concept boards behind it.
*/
const RoomStop = ({ room, index, total, isActive }) => {
  const [conceptsOpen, setConceptsOpen] = useState(false);

  const rise = {
    hidden: { opacity: 0, y: 26 },
    show: (i = 0) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.75, delay: 0.1 + i * 0.08, ease: [0.22, 1, 0.36, 1] }
    })
  };

  return (
    <section className="room-stop" style={{ '--room-accent': room.accent }}>
      <div className="room-stop-plate">
        {room.chapter && (
          <motion.div
            className="room-chapter"
            variants={rise}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, amount: 0.4 }}
            custom={0}
          >
            <span className="room-chapter-label">{room.chapter.label}</span>
            <span className="room-chapter-rule" aria-hidden="true" />
            <span className="room-chapter-title">{room.chapter.title}</span>
          </motion.div>
        )}
        <motion.p
          className="annotation room-stop-counter"
          variants={rise}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
          custom={0}
        >
          Stop {String(index + 1).padStart(2, '0')}{' '}
          <span className="tick">/</span> {String(total).padStart(2, '0')} — {room.kicker}
        </motion.p>

        <MaskReveal className="room-stop-title" delay={0.12} amount={0.6}>
          {room.label}<span className="dot">.</span>
        </MaskReveal>

        <motion.p
          className="room-stop-description"
          variants={rise}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
          custom={2}
        >
          {room.description}
        </motion.p>

        <motion.p
          className="annotation room-stop-note"
          variants={rise}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
          custom={3}
        >
          {room.note}
        </motion.p>

        <motion.div
          className="room-stop-actions"
          variants={rise}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.4 }}
          custom={5}
        >
          <a className="btn-primary" href={`#/gallery?room=${room.galleryFilter}`}>
            {`Explore ${room.label.toLowerCase()} projects`}
            <span className="arrow">→</span>
          </a>
          {room.concepts.length > 0 && <button className="btn-ghost room-stop-concepts" onClick={() => setConceptsOpen(true)}>
            Concept ideas
            <span className="arrow">→</span>
          </button>}
        </motion.div>
      </div>

      {/* Which stop you are on, drawn as a row of ticks down the right */}
      <div className="room-stop-ticks" aria-hidden="true">
        {Array.from({ length: total }, (_, i) => (
          <span key={i} className={`room-tick ${i === index ? 'on' : ''}`} />
        ))}
      </div>

      {index < total - 1 && (
        <div className={`room-stop-next annotation ${isActive ? 'visible' : ''}`} aria-hidden="true">
          <span>Keep scrolling</span>
          <span className="room-stop-next-line" />
        </div>
      )}

      <ConceptsOverlay room={room} open={conceptsOpen} onClose={() => setConceptsOpen(false)} />
    </section>
  );
};

export default RoomStop;
