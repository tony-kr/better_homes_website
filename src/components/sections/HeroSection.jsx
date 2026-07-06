import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import './HeroSection.css';

const metrics = [
  { value: '500+', label: 'Homes transformed' },
  { value: '50+', label: 'Design experts' },
  { value: '98%', label: 'Client satisfaction' }
];

const disciplines = [
  'Full homes',
  'Modular kitchens',
  'Living rooms',
  'Bedrooms',
  'Smart lighting',
  'Space planning'
];

const HeroSection = () => {
  const sectionRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasEntered) {
          setHasEntered(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, [hasEntered]);

  return (
    <section ref={sectionRef} className="hero-section">
      <div className="hero-content">

        {/* Left side - the practice */}
        <motion.div
          className="hero-text"
          initial={{ opacity: 0, y: 50 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="annotation hero-eyebrow">
            02 <span className="tick">/</span> 08 — The studio
          </p>

          <h2 className="hero-title">
            Built for the hour you <em>come home</em>.
          </h2>

          <p className="hero-lede">
            Better Homes is Bangalore's trusted interior design studio —
            crafting beautiful homes since 2014, from cozy 1BHKs in
            Koramangala to luxury villas in Whitefield. Every project begins
            with an evening: how the light falls, where the family gathers,
            which room glows first.
          </p>

          <div className="hero-metrics">
            {metrics.map((m, i) => (
              <motion.div
                className="metric"
                key={m.label}
                initial={{ opacity: 0, y: 24 }}
                animate={hasEntered ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8, delay: 0.6 + i * 0.15, ease: [0.22, 1, 0.36, 1] }}
              >
                <span className="metric-value">{m.value}</span>
                <span className="metric-label annotation">{m.label}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Right side - what we design */}
        <motion.div
          className="hero-disciplines"
          initial={{ opacity: 0, y: 50 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, delay: 0.45, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="annotation disciplines-title">What we design</p>
          <ul className="disciplines-list">
            {disciplines.map((d) => (
              <li className="discipline-item" key={d}>{d}</li>
            ))}
          </ul>
        </motion.div>

      </div>
    </section>
  );
};

export default HeroSection;
