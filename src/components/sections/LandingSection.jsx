import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './LandingSection.css';

const rotatingWords = ['breathe', 'gather', 'glow', 'endure'];

const LandingSection = ({ onNavigate }) => {
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setWordIndex((prev) => (prev + 1) % rotatingWords.length);
    }, 3200);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="landing-section">
      <div className="landing-content">
        <motion.p
          className="annotation landing-eyebrow"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 1.6 }}
        >
          Better Homes <span className="tick">·</span> Crafting Better Living <span className="tick">·</span> Bangalore
        </motion.p>

        <motion.h1
          className="landing-title"
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, delay: 1.9, ease: [0.22, 1, 0.36, 1] }}
        >
          <span className="title-line">Homes that</span>
          <span className="title-line rotating-wrapper">
            <AnimatePresence mode="wait">
              <motion.em
                key={rotatingWords[wordIndex]}
                className="rotating-word"
                initial={{ y: '80%', opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: '-70%', opacity: 0 }}
                transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
              >
                {rotatingWords[wordIndex]}.
              </motion.em>
            </AnimatePresence>
          </span>
        </motion.h1>

        <motion.p
          className="landing-lede"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 2.5 }}
        >
          Bangalore's premier interior design studio. We design for the hour
          you come home — when the sky turns blue and the windows turn warm.
        </motion.p>

        <motion.div
          className="landing-cta"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 2.9 }}
        >
          <a className="btn-primary" href="#/gallery">
            See our work
            <span className="arrow">→</span>
          </a>
          <button className="btn-ghost" onClick={() => onNavigate?.('footer')}>
            Start a project
          </button>
        </motion.div>
      </div>

      {/* Drawing-sheet annotation pinned to the model */}
      <motion.div
        className="landing-plate annotation"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2, delay: 3.2 }}
        aria-hidden="true"
      >
        <span>Model H-014</span>
        <span className="plate-rule"></span>
        <span>Dusk elevation · 1:100</span>
      </motion.div>

      <motion.div
        className="landing-scroll annotation"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 3.4 }}
        aria-hidden="true"
      >
        <span>Scroll</span>
        <span className="scroll-line"></span>
      </motion.div>
    </section>
  );
};

export default LandingSection;
