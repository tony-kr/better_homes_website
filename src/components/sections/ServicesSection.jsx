import { motion } from 'framer-motion';
import { MaskReveal, rise } from '../motion';
import './ServicesSection.css';
import { sheetNumber } from '../../data/journey';

const sheet = sheetNumber('services');

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

const ServicesSection = ({ onNavigate }) => (
  <section className="services-section">
    <div className="services-content">
      <div className="services-header">
        <motion.p className="annotation services-eyebrow" {...rise(0)}>
          {sheet.n} <span className="tick">/</span> {sheet.total} — Services
        </motion.p>
        <MaskReveal className="services-title">
          Everything a home needs, <span className="accent">under one roof</span><span className="dot">.</span>
        </MaskReveal>
        <motion.p className="services-lede" {...rise(0.2)}>
          One team from the first measurement to the last cushion: design,
          joinery, lighting and finishing, managed end to end.
        </motion.p>
        <motion.div {...rise(0.3)}>
          <button className="btn-primary" onClick={() => onNavigate?.('estimate')}>
            Get a free estimate <span className="arrow" aria-hidden="true">→</span>
          </button>
        </motion.div>
      </div>

      <ol className="services-list">
        {services.map((s, i) => (
          <motion.li className="service-row" key={s.title} {...rise(0.05 + i * 0.05, 16)}>
            <span className="annotation service-index">{String(i + 1).padStart(2, '0')}</span>
            <h3 className="service-name">{s.title}</h3>
            <p className="service-description">{s.description}</p>
          </motion.li>
        ))}
      </ol>
    </div>
  </section>
);

export default ServicesSection;
