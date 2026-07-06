import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './StoriesSection.css';

/*
  Client stories — "What Our Clients Say" from betterhomesindia.in,
  retold in the site's voice. Priya's story is verbatim from the
  current website.
*/
const stories = [
  {
    name: 'Priya Sharma',
    project: '3BHK · Whitefield',
    quote:
      'Better Homes transformed our 3BHK into a dream space. The modular kitchen is stunning, and the team delivered everything on time. The 3D visualization helped us make confident decisions.'
  },
  {
    name: 'Rajesh & Kavitha Menon',
    project: 'Full home · Koramangala',
    quote:
      'From the first sketch to the final handover, everything was transparent — budget, timeline, materials. The wardrobes and TV unit look exactly like the design we approved.'
  },
  {
    name: 'Ananya Iyer',
    project: 'Modular kitchen · HSR Layout',
    quote:
      'They understood how we actually cook. The kitchen is beautiful, but more importantly it works — every shelf, every drawer is where our hands expect it to be.'
  },
  {
    name: 'Mohammed Faisal',
    project: '2BHK · Electronic City',
    quote:
      'We handed over an empty flat and got back a home. The pooja unit they designed is the first thing every guest asks about.'
  }
];

const AUTO_ADVANCE_MS = 6500;

const StoriesSection = () => {
  const sectionRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);
  const [active, setActive] = useState(0);

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

  // Rotate stories once the section is on screen
  useEffect(() => {
    if (!hasEntered) return;
    const id = setInterval(() => {
      setActive((prev) => (prev + 1) % stories.length);
    }, AUTO_ADVANCE_MS);
    return () => clearInterval(id);
  }, [hasEntered]);

  const story = stories[active];

  return (
    <section ref={sectionRef} className="stories-section">
      <div className="stories-content">
        <motion.div
          className="stories-header"
          initial={{ opacity: 0, y: 36 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="annotation stories-eyebrow">
            06 <span className="tick">/</span> 08 — Client stories
          </p>
          <h2 className="stories-title">
            What our clients <em>say</em>.
          </h2>
        </motion.div>

        <motion.figure
          className="stories-stage"
          initial={{ opacity: 0, y: 40 }}
          animate={hasEntered ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.9, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
        >
          <span className="stories-mark" aria-hidden="true">&ldquo;</span>
          <AnimatePresence mode="wait">
            <motion.div
              key={story.name}
              initial={{ opacity: 0, y: 26 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -18 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            >
              <blockquote className="stories-quote">{story.quote}</blockquote>
              <figcaption className="stories-byline">
                <span className="stories-name">{story.name}</span>
                <span className="annotation stories-project">{story.project}</span>
              </figcaption>
            </motion.div>
          </AnimatePresence>
        </motion.figure>

        <motion.div
          className="stories-nav"
          initial={{ opacity: 0 }}
          animate={hasEntered ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          {stories.map((s, i) => (
            <button
              key={s.name}
              className={`stories-dot ${i === active ? 'active' : ''}`}
              onClick={() => setActive(i)}
              aria-label={`Story from ${s.name}`}
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default StoriesSection;
