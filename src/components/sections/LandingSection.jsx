import { motion } from 'framer-motion';
import { ESTIMATE_LINK } from '../../data/contact';
import { EASE, MaskReveal, RotatingWord } from '../motion';
import './LandingSection.css';

/*
  The landing plate.

  A golden-hour render of the house fills the screen (the hero backdrop, in
  HouseJourney). Over it, low on the left: one line in heavy Jost whose
  ending keeps changing, set upright in red, closed with the red
  full stop that runs through the site. A glass fact bar sits centred at the
  foot, after the client's first reference.

  Everything is held until the splash has lifted (`revealed`), so the
  entrance is actually seen.
*/
const ENDINGS = ['lived in', 'come home to', 'remembered', 'handed down', 'grown into'];

const facts = [
  { value: '500+', label: 'Homes delivered' },
  { value: '45', unit: 'days', label: 'Average handover' },
  { value: '50+', label: 'Designers & makers' }
];

const fade = (delay, revealed) => ({
  initial: { opacity: 0, y: 20 },
  animate: revealed ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 },
  transition: { duration: 1.1, delay: revealed ? delay : 0, ease: EASE }
});

const LandingSection = ({ onNavigate, revealed = true }) => (
  <section className="landing-section">
    <div className="landing-plate">
      <motion.p className="landing-eyebrow" {...fade(0.3, revealed)}>
        <span className="landing-eyebrow-dot" aria-hidden="true" />
        <span className="landing-eyebrow-brand">Better Homes <span className="landing-eyebrow-sep">/</span></span> Turnkey interiors &amp; construction, Bengaluru
      </motion.p>

      <h1 className="landing-title">
        <MaskReveal as="span" className="landing-title-line" show={revealed} delay={0.45} stagger={0.07}>
          Homes made to be
        </MaskReveal>
        <motion.span className="landing-title-line landing-title-turn" {...fade(0.85, revealed)}>
          <RotatingWord
            words={ENDINGS}
            interval={3000}
            paused={!revealed}
            className="accent"
            suffix={<span className="dot">.</span>}
          />
        </motion.span>
      </h1>

      <motion.p className="landing-lede" {...fade(1.0, revealed)}>
        Interiors designed end to end and built by one team. Walk through a
        home we designed before you commit to a single panel.
      </motion.p>

      <motion.div className="landing-cta" {...fade(1.12, revealed)}>
        <a className="btn-primary" href={ESTIMATE_LINK} target="_blank" rel="noreferrer">
          Get a free estimate
          <span className="arrow" aria-hidden="true">→</span>
        </a>
        <button className="btn-quiet" onClick={() => onNavigate?.('living')}>
          Walk the home
          <span aria-hidden="true">↓</span>
        </button>
      </motion.div>
    </div>

    <motion.dl className="landing-facts" {...fade(1.3, revealed)}>
      {facts.map((f) => (
        <div className="landing-fact" key={f.label}>
          {/* dt must precede dd; the label is lifted above it in CSS */}
          <dt>
            {f.value}
            {f.unit && <span className="landing-fact-unit">{f.unit}</span>}
          </dt>
          <dd>{f.label}</dd>
        </div>
      ))}
    </motion.dl>
  </section>
);

export default LandingSection;
