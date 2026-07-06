import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './PortfolioSection.css';

// Featured projects from betterhomesindia.in — real names, areas, neighbourhoods
const projects = [
  {
    id: 'modern-minimalist-kitchen',
    name: 'Modern Minimalist Kitchen',
    category: 'Kitchen',
    area: '180 sq ft',
    location: 'Whitefield',
    image: '/kitchen/kitchen-02.jpg'
  },
  {
    id: 'luxe-living-room',
    name: 'Luxe Living Room',
    category: 'Living room',
    area: '320 sq ft',
    location: 'Indiranagar',
    image: '/living_room/living-02.jpg'
  },
  {
    id: 'contemporary-3bhk',
    name: 'Contemporary 3BHK',
    category: 'Full home',
    area: '1,400 sq ft',
    location: 'Koramangala',
    image: '/dining_space/dining-02.jpg'
  },
  {
    id: 'serene-master-suite',
    name: 'Serene Master Suite',
    category: 'Bedroom',
    area: '220 sq ft',
    location: 'HSR Layout',
    image: '/bedroom/bedroom-01.jpg'
  },
  {
    id: 'scandinavian-kitchen',
    name: 'Scandinavian Kitchen',
    category: 'Kitchen',
    area: '150 sq ft',
    location: 'Sarjapur Road',
    image: '/kitchen/kitchen-04.jpg'
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
            05 <span className="tick">/</span> 08 — Featured projects
          </motion.p>

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
            05 of 12 completed projects, across Bangalore
          </motion.p>
        </div>

        <div className="portfolio-image-side" aria-hidden="true">
          <AnimatePresence mode="wait">
            <motion.figure
              key={active.id}
              className="portfolio-figure"
              initial={{ opacity: 0, scale: 1.04 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
            >
              <img src={active.image} alt={active.name} draggable={false} />
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
