import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { WhatsAppIcon, PhoneIcon, MailIcon, PinIcon } from '../icons';
import {
  ESTIMATE_LINK,
  PHONE_NUMBER,
  PHONE_DISPLAY,
  WHATSAPP_DISPLAY,
  EMAIL,
  STUDIO_ADDRESS,
  STUDIO_HOURS
} from '../../data/contact';
import { MaskReveal } from '../motion';
import './EstimateSection.css';
import { sheetNumber } from '../../data/journey';

const sheet = sheetNumber('estimate');

/*
  Free estimate — no form. One button opens WhatsApp with the enquiry already
  written out, so the conversation starts where the studio actually answers.
*/
const steps = [
  {
    n: '01',
    title: 'Send the message',
    body: 'The button drafts it for you — fill in the blanks and hit send.'
  },
  {
    n: '02',
    title: 'We call you back',
    body: 'A designer calls within a day to understand the home and the budget.'
  },
  {
    n: '03',
    title: 'You get the estimate',
    body: 'A written scope and price, with no obligation and no site-visit fee.'
  }
];

const EstimateSection = () => {
  const sectionRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setHasEntered(true);
      },
      { threshold: 0.25 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  const rise = (delay = 0) => ({
    initial: { opacity: 0, y: 34 },
    animate: hasEntered ? { opacity: 1, y: 0 } : {},
    transition: { duration: 0.85, delay, ease: [0.22, 1, 0.36, 1] }
  });

  return (
    <section ref={sectionRef} className="estimate-section">
      <div className="estimate-content">
        <motion.div className="estimate-intro" {...rise(0)}>
          <p className="annotation estimate-eyebrow">
            {sheet.n} <span className="tick">/</span> {sheet.total} — Free estimate
          </p>
          <MaskReveal className="estimate-title">
            Tell us about the home. <span className="accent">The estimate is on us</span><span className="dot">.</span>
          </MaskReveal>
          <p className="estimate-lede">
            No forms, no waiting on an email. Tap below and WhatsApp opens with
            the enquiry already written — you only fill in the blanks.
          </p>
        </motion.div>

        <motion.div className="estimate-action" {...rise(0.12)}>
          <a
            className="btn-whatsapp"
            href={ESTIMATE_LINK}
            target="_blank"
            rel="noreferrer"
          >
            <WhatsAppIcon size={22} />
            <span>Get my free estimate on WhatsApp</span>
            <span className="arrow">→</span>
          </a>
          <p className="annotation estimate-reassure">
            Replies within a day <span className="tick">·</span> {STUDIO_HOURS}
          </p>
        </motion.div>

        <motion.ol className="estimate-steps" {...rise(0.2)}>
          {steps.map((s, i) => (
            <motion.li
              className="estimate-step"
              key={s.n}
              initial={{ opacity: 0, y: 26 }}
              animate={hasEntered ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.3 + i * 0.1, ease: [0.22, 1, 0.36, 1] }}
            >
              <span className="annotation estimate-step-n">{s.n}</span>
              <h3 className="estimate-step-title">{s.title}</h3>
              <p className="estimate-step-body">{s.body}</p>
            </motion.li>
          ))}
        </motion.ol>

        <motion.ul className="estimate-details" {...rise(0.36)}>
          <li>
            <span className="annotation">Call</span>
            <a className="contact-link" href={`tel:${PHONE_NUMBER}`}>
              <PhoneIcon size={15} />
              {PHONE_DISPLAY}
            </a>
          </li>
          <li>
            <span className="annotation">WhatsApp</span>
            <a
              className="contact-link is-whatsapp"
              href={ESTIMATE_LINK}
              target="_blank"
              rel="noreferrer"
            >
              <WhatsAppIcon size={17} />
              {WHATSAPP_DISPLAY}
            </a>
          </li>
          <li>
            <span className="annotation">Write</span>
            <a className="contact-link" href={`mailto:${EMAIL}`}>
              <MailIcon size={15} />
              {EMAIL}
            </a>
          </li>
          <li>
            <span className="annotation">Visit</span>
            <span className="contact-link is-static">
              <PinIcon size={15} />
              {STUDIO_ADDRESS}
            </span>
          </li>
        </motion.ul>
      </div>
    </section>
  );
};

export default EstimateSection;
