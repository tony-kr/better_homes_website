import { useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './RoomSection.css';

const RoomSection = ({ id, title, description, image, projects, index }) => {
  const sectionRef = useRef(null);
  const [hasEntered, setHasEntered] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasEntered) {
          setHasEntered(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, [hasEntered]);

  // Alternate layout for visual interest
  const isReversed = index % 2 !== 0;

  return (
    <section ref={sectionRef} className={`room-section ${isReversed ? 'reversed' : ''}`} id={id}>
      <motion.div
        className="room-content"
        initial={{ opacity: 0 }}
        animate={hasEntered ? { opacity: 1 } : {}}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >

        {/* Room Visual Area - kept for spacing, but transparent for HouseCanvas */}
        <motion.div
          className="room-visual"
        >
          {/* Empty transparent container */}
          <div className="room-image-spacer" style={{ height: '100%', width: '100%' }}></div>
        </motion.div>

        {/* Room Info */}
        <motion.div
          className="room-info"
          initial={{ x: isReversed ? 100 : -100, opacity: 0 }}
          animate={hasEntered ? { x: 0, opacity: 1 } : {}}
          transition={{ duration: 1, delay: 0.4, ease: "easeOut" }}
        >
          <div className="room-number">
            {String(index + 1).padStart(2, '0')}
          </div>

          <h2 className="room-title">{title}</h2>

          <p className="room-description">{description}</p>

          <div className="room-meta">
            <span className="project-count">{projects} Projects</span>
            <div className="meta-divider"></div>
            <span className="room-tag">Premium Collection</span>
          </div>

          <motion.a
            href={`/gallery/${id}`}
            className="btn-primary explore-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Explore {title} Projects
            <span className="arrow">→</span>
          </motion.a>

          {/* Additional features list */}
          <motion.div
            className="room-features"
            initial={{ y: 20, opacity: 0 }}
            animate={hasEntered ? { y: 0, opacity: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <div className="feature">
              <span className="feature-icon">✓</span>
              <span>Custom Design</span>
            </div>
            <div className="feature">
              <span className="feature-icon">✓</span>
              <span>Premium Materials</span>
            </div>
            <div className="feature">
              <span className="feature-icon">✓</span>
              <span>3D Visualization</span>
            </div>
          </motion.div>
        </motion.div>

      </motion.div>

      {/* Section divider */}
      <div className="section-divider"></div>
    </section>
  );
};

// Room-specific visual components removed in favor of HouseCanvas
export default RoomSection;
