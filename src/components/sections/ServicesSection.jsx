import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import './ServicesSection.css';

// Full service list from betterhomesindia.in
const services = [
  {
    title: 'Modular Kitchen',
    description: 'Sleek, functional kitchens with premium finishes — from BWR plywood to marine-grade materials.'
  },
  {
    title: 'Living Room Design',
    description: 'Curated living spaces that balance comfort and aesthetics with custom furniture and lighting.'
  },
  {
    title: 'Bedroom Interiors',
    description: 'Personalized bedrooms with designer wardrobes, false ceilings, and ambient lighting.'
  },
  {
    title: 'Bathroom Design',
    description: 'Spa-inspired bathrooms with premium tiles, fixtures, and waterproof finishes.'
  },
  {
    title: 'Color Consultation',
    description: 'Expert guidance on color schemes tuned to your space, its light, and your taste.'
  },
  {
    title: 'Smart Lighting',
    description: 'IoT-enabled lighting scenes — day to evening ambiance with automated smart controls.'
  },
  {
    title: 'Wall Treatments',
    description: 'Textured walls, accent panels, and decorative finishes that define each space.'
  },
  {
    title: 'Space Planning',
    description: 'Optimal layout design maximizing every square foot with 3D spatial analysis.'
  }
];

const ServicesSection = ({ onNavigate }) => {
  const sectionRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);

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

  return (
    <section ref={sectionRef} className="services-section">
      <div className="services-content">
        <motion.div
          className="services-header"
          initial={{ opacity: 0, y: 40 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="annotation services-eyebrow">
            03 <span className="tick">/</span> 08 — Services
          </p>
          <h2 className="services-title">
            Everything a home needs, <em>under one roof</em>.
          </h2>
        </motion.div>

        <div className="services-grid">
          {services.map((s, i) => (
            <motion.article
              className="service-card"
              key={s.title}
              initial={{ opacity: 0, y: 28 }}
              animate={hasEntered ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.25 + i * 0.08, ease: [0.22, 1, 0.36, 1] }}
            >
              <span className="annotation service-index">
                {String(i + 1).padStart(2, '0')}
              </span>
              <h3 className="service-name">{s.title}</h3>
              <p className="service-description">{s.description}</p>
            </motion.article>
          ))}
        </div>

        <motion.div
          className="services-cta"
          initial={{ opacity: 0 }}
          animate={hasEntered ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 1.0 }}
        >
          <button className="btn-ghost" onClick={() => onNavigate?.('estimate')}>
            Get a free estimate <span className="arrow">→</span>
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default ServicesSection;
