import { motion } from 'framer-motion';
import { MaskReveal, rise } from '../motion';
import './ServicesSection.css';
import { sheetNumber } from '../../data/journey';

const sheet = sheetNumber('services');

// The trades Better Homes delivers under one roof (client brief,
// September 2026): turnkey interiors, modular work, construction and every
// service trade a home needs.
const services = [
  {
    title: 'Turnkey Interiors',
    description: 'Design to handover under one contract: we plan, build and furnish, then hand you the keys.'
  },
  {
    title: 'Modular Kitchens & Wardrobes',
    description: 'Kitchens, wardrobes and storage modules in BWR and marine-grade ply, made to fit and finished to last.'
  },
  {
    title: 'Construction',
    description: 'New builds and extensions, from foundation and structure through to a finished shell.'
  },
  {
    title: 'Renovation',
    description: 'A kitchen, a bathroom or the whole home, opened up and rebuilt around how you live now.'
  },
  {
    title: 'Electrical',
    description: 'Wiring, points and lighting circuits, planned with the interior layout rather than after it.'
  },
  {
    title: 'False Ceiling',
    description: 'Gypsum and POP ceilings with coves, profiles and concealed lighting.'
  },
  {
    title: 'Plumbing',
    description: 'Concealed supply and drainage for kitchens and bathrooms, laid before a single tile goes down.'
  },
  {
    title: 'Tiling & Flooring',
    description: 'Floors, walls and bathrooms in vitrified tile, marble and natural stone.'
  },
  {
    title: 'Painting',
    description: 'Interior and exterior finishes and textures, from primer to the final coat.'
  },
  {
    title: 'Metal Fabrication',
    description: 'Gates, grills, railings, staircases and custom steelwork, fabricated to drawing.'
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
          Every trade a home needs, from structure and services to the
          last coat of paint, managed by one team so nothing falls between
          contractors.
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
