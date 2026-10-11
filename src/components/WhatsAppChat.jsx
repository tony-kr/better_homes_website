import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { WhatsAppIcon } from './icons';
import { whatsappLink, STUDIO_HOURS } from '../data/contact';
import { EASE } from './motion';
import './WhatsAppChat.css';

/*
  "Chat on WhatsApp", on every page (after the client's reference,
  mellowdesigns.co). A red pill with a live dot sits bottom-right; it opens
  a small chat card: the studio's mark, "Online", a moment of typing, then a
  greeting bubble on a WhatsApp-style ground, and one button that opens the
  conversation with a first line already written.

  It waits for the splash to lift, closes on Escape or a click elsewhere,
  and keeps its own red so it reads as part of the site, not a plug-in.
*/
const GREETING_MESSAGE = 'Hello Better Homes! I would like to talk about my home.';

const timeNow = () =>
  new Date().toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit' });

export default function WhatsAppChat({ hidden = false }) {
  const [open, setOpen] = useState(false);
  const [typing, setTyping] = useState(true);
  const [time, setTime] = useState(timeNow);
  const rootRef = useRef(null);
  const reduce = useReducedMotion();

  // Each opening shows the studio "typing" for a beat before the greeting
  useEffect(() => {
    if (!open) return undefined;
    setTime(timeNow());
    setTyping(!reduce);
    const id = setTimeout(() => setTyping(false), 1100);
    return () => clearTimeout(id);
  }, [open, reduce]);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => e.key === 'Escape' && setOpen(false);
    const onDown = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('mousedown', onDown);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('mousedown', onDown);
    };
  }, [open]);

  if (hidden) return null;

  return (
    <motion.div
      ref={rootRef}
      className="wa-chat"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.9, delay: 0.8, ease: EASE }}
    >
      <AnimatePresence>
        {open && (
          <motion.div
            className="wa-card"
            role="dialog"
            aria-label="Chat with Better Homes on WhatsApp"
            initial={{ opacity: 0, y: 16, scale: 0.94 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.96, transition: { duration: 0.22 } }}
            transition={{ duration: 0.5, ease: EASE }}
          >
            <header className="wa-card-head">
              <span className="wa-avatar">
                <img src="/bh-logo.png" alt="" draggable={false} />
                <span className="wa-avatar-dot" aria-hidden="true" />
              </span>
              <span className="wa-card-who">
                <span className="wa-card-name">Better Homes</span>
                <span className="wa-card-status">{typing ? 'typing…' : 'Online'}</span>
              </span>
              <button className="wa-close" onClick={() => setOpen(false)} aria-label="Close chat">
                <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
                  <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
              </button>
            </header>

            <div className="wa-card-body" aria-live="polite">
              <AnimatePresence mode="wait" initial={false}>
                {typing ? (
                  <motion.span
                    key="typing"
                    className="wa-bubble wa-typing"
                    aria-label="Better Homes is typing"
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, transition: { duration: 0.12 } }}
                  >
                    <i /><i /><i />
                  </motion.span>
                ) : (
                  <motion.div
                    key="msg"
                    className="wa-bubble"
                    initial={{ opacity: 0, y: 8, scale: 0.97 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.4, ease: EASE }}
                  >
                    <p>Hi there 👋</p>
                    <p>
                      Planning a new home, a renovation or a modular kitchen? Tell us
                      about it and a designer will get back to you within a day.
                    </p>
                    <span className="wa-bubble-time">{time}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <footer className="wa-card-foot">
              <a
                className="wa-start"
                href={whatsappLink(GREETING_MESSAGE)}
                target="_blank"
                rel="noreferrer"
              >
                <WhatsAppIcon size={18} />
                <span>Start WhatsApp chat</span>
              </a>
              <span className="wa-hours">{STUDIO_HOURS}</span>
            </footer>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        className={`wa-pill ${open ? 'is-open' : ''}`}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={open ? 'Close WhatsApp chat' : 'Chat on WhatsApp'}
      >
        <WhatsAppIcon size={20} />
        <span className="wa-pill-text">Chat on WhatsApp</span>
        <span className="wa-live" aria-hidden="true" />
      </button>
    </motion.div>
  );
}
