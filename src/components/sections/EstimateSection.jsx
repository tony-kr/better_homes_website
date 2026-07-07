import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import './EstimateSection.css';

const projectTypes = [
  'Full Home Interior',
  'Kitchen Only',
  'Living Room',
  'Bedroom',
  'Bathroom',
  'Other'
];

const EstimateSection = () => {
  const sectionRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);
  const [sent, setSent] = useState(false);

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

  // The enquiry goes straight to the studio's WhatsApp, fully drafted
  const WHATSAPP_NUMBER = '918287633479';

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    const message = data.get('message')?.trim();
    const lines = [
      'Hello Better Homes!',
      'I would like a *free estimate* for my home. Here are my details:',
      '',
      `*Name:* ${data.get('name')}`,
      `*Mobile:* ${data.get('mobile')}`,
      `*Email:* ${data.get('email')}`,
      `*Project type:* ${data.get('projectType')}`,
      ...(message ? ['', `*About the space:* ${message}`] : []),
      '',
      'Please get back to me with the scope and estimate. Thank you!'
    ];
    window.open(
      `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`,
      '_blank',
      'noopener'
    );
    setSent(true);
  };

  return (
    <section ref={sectionRef} className="estimate-section">
      <div className="estimate-content">

        <motion.div
          className="estimate-intro"
          initial={{ opacity: 0, y: 40 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="annotation estimate-eyebrow">
            07 <span className="tick">/</span> 08 — Free estimate
          </p>
          <h2 className="estimate-title">
            Tell us about the home. <em>The estimate is on us.</em>
          </h2>
          <p className="estimate-lede">
            Share a few details and our design team will come back with a
            scope and estimate — no obligation, no site-visit fee.
          </p>

          <ul className="estimate-details">
            <li>
              <span className="annotation">Call</span>
              <a href="tel:+919876543210">+91 98765 43210</a>
            </li>
            <li>
              <span className="annotation">WhatsApp</span>
              <a href="https://wa.me/918287633479" target="_blank" rel="noreferrer">+91 82876 33479</a>
            </li>
            <li>
              <span className="annotation">Write</span>
              <a href="mailto:hello@betterhomes.in">hello@betterhomes.in</a>
            </li>
            <li>
              <span className="annotation">Visit</span>
              <span>170 2nd Block, Banashankari 6th Stage 1st Block, Channasandra, Bengaluru — Mon–Sat, 10AM–7PM</span>
            </li>
          </ul>
        </motion.div>

        <motion.form
          className="estimate-form"
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 40 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.9, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="form-row">
            <label className="form-field">
              <span className="annotation">Full name</span>
              <input type="text" name="name" required autoComplete="name" placeholder="Your name" />
            </label>
            <label className="form-field">
              <span className="annotation">Mobile number</span>
              <input type="tel" name="mobile" required autoComplete="tel" placeholder="+91" />
            </label>
          </div>

          <div className="form-row">
            <label className="form-field">
              <span className="annotation">Email address</span>
              <input type="email" name="email" required autoComplete="email" placeholder="you@example.com" />
            </label>
            <label className="form-field">
              <span className="annotation">Project type</span>
              <select name="projectType" required defaultValue="Full Home Interior">
                {projectTypes.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>
          </div>

          <label className="form-field">
            <span className="annotation">Message</span>
            <textarea
              name="message"
              rows={3}
              placeholder="Tell us about the space — size, rooms, when you'd like to start…"
            />
          </label>

          <div className="estimate-submit">
            <button type="submit" className="btn-primary">
              Get free estimate <span className="arrow">→</span>
            </button>
            {sent && (
              <span className="annotation estimate-sent">
                Opening WhatsApp — we reply within a day
              </span>
            )}
          </div>
        </motion.form>

      </div>
    </section>
  );
};

export default EstimateSection;
