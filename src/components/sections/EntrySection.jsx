import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { EASE } from '../motion';
import './EntrySection.css';

/*
  The hall, before the living room's doors. Deliberately almost empty: the
  Services sheet lifts off two closed walnut doors, and scrolling on slides
  them apart and walks you through (HouseJourney.jsx). One quiet line says
  so, and steps aside the moment the doors start to part.
*/
const EntrySection = () => {
  const ref = useRef(null);
  // Only while the hall has (nearly) the whole screen
  const holding = useInView(ref, { amount: 0.9 });
  return (
    <section ref={ref} className="entry-section" aria-label="Entering the home">
      <motion.div
        className="entry-cue"
        initial={{ opacity: 0, y: 16 }}
        animate={holding ? { opacity: 1, y: 0 } : { opacity: 0, y: -10 }}
        transition={{ duration: 0.55, ease: EASE }}
      >
        <span className="entry-cue-title">
          Step inside<span className="dot">.</span>
        </span>
        <span className="entry-cue-line" aria-hidden="true" />
        <span className="annotation entry-cue-hint">Scroll to open</span>
      </motion.div>
    </section>
  );
};

export default EntrySection;
