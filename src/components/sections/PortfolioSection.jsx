import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { featuredPhoto } from '../../data/projectPhotos';
import { EASE, MaskReveal } from '../motion';
import './PortfolioSection.css';
import { sheetNumber } from '../../data/journey';

const sheet = sheetNumber('portfolio');

// Featured projects — real names, areas, neighbourhoods, shot on site
const projects = [
  {
    id: 'modern-minimalist-kitchen',
    name: 'Modern Minimalist Kitchen',
    category: 'Kitchen',
    area: '180 sq ft',
    location: 'Whitefield',
    image: featuredPhoto(34)
  },
  {
    id: 'luxe-living-room',
    name: 'Luxe Living Room',
    category: 'Living room',
    area: '320 sq ft',
    location: 'Indiranagar',
    image: featuredPhoto(46)
  },
  {
    id: 'contemporary-3bhk',
    name: 'Contemporary 3BHK',
    category: 'Full home',
    area: '1,400 sq ft',
    location: 'Koramangala',
    image: featuredPhoto(44)
  },
  {
    id: 'serene-master-suite',
    name: 'Serene Master Suite',
    category: 'Bedroom',
    area: '220 sq ft',
    location: 'HSR Layout',
    image: featuredPhoto(43)
  },
  {
    id: 'scandinavian-kitchen',
    name: 'Scandinavian Kitchen',
    category: 'Kitchen',
    area: '150 sq ft',
    location: 'Sarjapur Road',
    image: featuredPhoto(18)
  }
];

const PortfolioSection = () => {
  const sectionRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

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

  const active = projects[activeIndex];

  return (
    <section ref={sectionRef} className="portfolio-section">
      <div className="portfolio-content">
        <div className="portfolio-list-side">
          <motion.p
            className="annotation portfolio-eyebrow"
            initial={{ opacity: 0, y: 24 }}
            animate={hasEntered ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            {sheet.n} <span className="tick">/</span> {sheet.total} — Featured projects
          </motion.p>

          <MaskReveal className="portfolio-title">
            Homes we have <span className="accent">handed over</span><span className="dot">.</span>
          </MaskReveal>

          <ul className="portfolio-list">
            {projects.map((p, i) => (
              <motion.li
                key={p.id}
                initial={{ opacity: 0, y: 30 }}
                animate={hasEntered ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.7, delay: 0.2 + i * 0.1, ease: [0.22, 1, 0.36, 1] }}
              >
                <button
                  className={`portfolio-row ${i === activeIndex ? 'active' : ''}`}
                  onMouseEnter={() => setActiveIndex(i)}
                  onFocus={() => setActiveIndex(i)}
                  onClick={() => setActiveIndex(i)}
                >
                  <span className="annotation portfolio-row-index">
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <span className="portfolio-row-name">{p.name}</span>
                  <span className="annotation portfolio-row-meta">
                    {p.category} · {p.area} · {p.location}
                  </span>
                </button>
              </motion.li>
            ))}
          </ul>

          <motion.p
            className="annotation portfolio-note"
            initial={{ opacity: 0 }}
            animate={hasEntered ? { opacity: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.9 }}
          >
            05 featured works, across Bengaluru <span className="tick">/</span>{' '}
            <a href="#/gallery" className="portfolio-gallery-link">see the full gallery →</a>
          </motion.p>
        </div>

        <div className="portfolio-image-side" aria-hidden="true">
          <AnimatePresence mode="wait">
            <motion.figure
              key={active.id}
              className="portfolio-figure"
              initial={{ clipPath: 'inset(100% 0% 0% 0%)' }}
              animate={{ clipPath: 'inset(0% 0% 0% 0%)' }}
              exit={{ clipPath: 'inset(0% 0% 100% 0%)', transition: { duration: 0.45, ease: [0.5, 0, 0.75, 0] } }}
              transition={{ duration: 0.8, ease: EASE }}
            >
              <motion.img
                src={active.image}
                alt={active.name}
                draggable={false}
                initial={{ scale: 1.12 }}
                animate={{ scale: 1 }}
                transition={{ duration: 1.2, ease: EASE }}
              />
              <figcaption className="annotation portfolio-caption">
                {active.location} — {active.area}
              </figcaption>
            </motion.figure>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

export default PortfolioSection;
