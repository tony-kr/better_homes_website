import { useEffect, useState, useRef, useCallback } from 'react';
import Lenis from 'lenis';
import { setLenis } from './lib/scroll';
import House3D from './components/House3D';
import LaserPointer from './components/LaserPointer';
import GalleryPage from './components/GalleryPage';
import LandingSection from './components/sections/LandingSection';
import HeroSection from './components/sections/HeroSection';
import ServicesSection from './components/sections/ServicesSection';
import RoomCarousel from './components/sections/RoomCarousel';
import PortfolioSection from './components/sections/PortfolioSection';
import StoriesSection from './components/sections/StoriesSection';
import EstimateSection from './components/sections/EstimateSection';
import Footer from './components/sections/Footer';
import StaggeredMenu from './components/sections/StaggeredMenu';
import './App.css';

// Home-page sections, in scroll order. The gallery lives on its own page (#/gallery).
const SECTION_IDS = ['landing', 'hero', 'services', 'rooms', 'portfolio', 'stories', 'estimate', 'footer'];

const menuItems = [
  { label: 'Home', ariaLabel: 'Go to landing', link: '#landing' },
  { label: 'About', ariaLabel: 'Learn about us', link: '#hero' },
  { label: 'Services', ariaLabel: 'What we design', link: '#services' },
  { label: 'Experience', ariaLabel: 'Explore the spaces', link: '#rooms' },
  { label: 'Portfolio', ariaLabel: 'Featured projects', link: '#portfolio' },
  { label: 'Client Stories', ariaLabel: 'What our clients say', link: '#stories' },
  { label: 'Gallery', ariaLabel: 'Real homes gallery', link: '#/gallery' },
  { label: 'Free Estimate', ariaLabel: 'Get a free estimate', link: '#estimate' },
  { label: 'Contact', ariaLabel: 'Get in touch', link: '#footer' }
];

const socialItems = [
  { label: 'Instagram', link: 'https://instagram.com' },
  { label: 'Pinterest', link: 'https://pinterest.com' },
  { label: 'LinkedIn', link: 'https://linkedin.com' }
];

const routeFromHash = () => (window.location.hash.startsWith('#/gallery') ? 'gallery' : 'home');

function App() {
  const [route, setRoute] = useState(routeFromHash);
  const [activeSection, setActiveSection] = useState('landing');
  const sectionRefs = useRef({});
  const lenisRef = useRef(null);
  const pendingSection = useRef(null);

  // One Lenis instance drives the whole document — continuous, fluid scroll
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      touchMultiplier: 1.6
    });
    lenisRef.current = lenis;
    setLenis(lenis);

    let raf;
    const loop = (time) => {
      lenis.raf(time);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(raf);
      lenis.destroy();
      lenisRef.current = null;
      setLenis(null);
    };
  }, []);

  const scrollToSection = useCallback((id, immediate = false) => {
    const target = sectionRefs.current[id];
    if (!target || !lenisRef.current) return;
    lenisRef.current.scrollTo(target, { immediate, offset: 0 });
  }, []);

  // Track which section owns the viewport centre (home page only)
  useEffect(() => {
    if (route !== 'home') return;
    const lenis = lenisRef.current;

    const update = () => {
      const centre = window.scrollY + window.innerHeight / 2;
      let current = SECTION_IDS[0];
      for (const id of SECTION_IDS) {
        const el = sectionRefs.current[id];
        if (el && el.offsetTop <= centre) current = id;
      }
      setActiveSection(current);
    };

    update();
    lenis?.on('scroll', update);
    window.addEventListener('resize', update);
    return () => {
      lenis?.off('scroll', update);
      window.removeEventListener('resize', update);
    };
  }, [route]);

  // Hash routing: '#/gallery' is a page, '#section' is an anchor on home
  useEffect(() => {
    const onHashChange = () => setRoute(routeFromHash());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  // Entering a page: gallery starts at the top; home honours a pending anchor
  useEffect(() => {
    if (route === 'gallery') {
      lenisRef.current?.scrollTo(0, { immediate: true });
      setActiveSection('gallery');
    } else if (pendingSection.current) {
      const id = pendingSection.current;
      pendingSection.current = null;
      requestAnimationFrame(() => scrollToSection(id, true));
    } else {
      lenisRef.current?.scrollTo(0, { immediate: true });
    }
  }, [route, scrollToSection]);

  // Intercept in-page anchors so Lenis animates them (works from both pages)
  useEffect(() => {
    const handleAnchorClick = (e) => {
      const anchor = e.target.closest('a[href^="#"]');
      if (!anchor) return;
      const href = anchor.getAttribute('href');
      if (href.startsWith('#/')) return; // page routes go through hashchange

      const id = href.slice(1);
      if (!SECTION_IDS.includes(id)) return;
      e.preventDefault();

      if (routeFromHash() !== 'home') {
        pendingSection.current = id;
        window.location.hash = '/';
      } else {
        scrollToSection(id);
      }
    };

    document.addEventListener('click', handleAnchorClick);
    return () => document.removeEventListener('click', handleAnchorClick);
  }, [scrollToSection]);

  // Arrow/page keys glide through Lenis instead of jumping natively
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target.matches('input, textarea, select')) return;
      const lenis = lenisRef.current;
      if (!lenis) return;
      const page = window.innerHeight * 0.88;
      if (e.key === 'ArrowDown' || e.key === 'PageDown') {
        e.preventDefault();
        lenis.scrollTo(lenis.scroll + (e.key === 'ArrowDown' ? page * 0.55 : page));
      } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
        e.preventDefault();
        lenis.scrollTo(lenis.scroll - (e.key === 'ArrowUp' ? page * 0.55 : page));
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const sectionIndex = SECTION_IDS.indexOf(activeSection);

  return (
    <div className="app">
      <LaserPointer />

      <StaggeredMenu
        isFixed={true}
        position="right"
        items={menuItems}
        socialItems={socialItems}
        displaySocials={true}
        displayItemNumbering={true}
        menuButtonColor={activeSection === 'rooms' ? '#1d1626' : '#f4f1ec'}
        openMenuButtonColor="#101823"
        changeMenuColorOnOpen={true}
        colors={['#17212e', '#d50000']}
        accentColor="#d50000"
        logoUrl="/bh-logo.png"
      />

      <House3D activeSection={activeSection} />

      {route === 'gallery' ? (
        <GalleryPage />
      ) : (
        <>
          <div
            className={`sheet-indicator ${activeSection === 'rooms' ? 'on-light' : ''}`}
            style={{ '--sheet-progress': (sectionIndex + 1) / SECTION_IDS.length }}
            aria-hidden="true"
          >
            <span className="sheet-current">{String(sectionIndex + 1).padStart(2, '0')}</span>
            <span className="sheet-rule"></span>
            <span>{String(SECTION_IDS.length).padStart(2, '0')}</span>
          </div>

          <div className="page-section" ref={el => sectionRefs.current['landing'] = el} id="landing">
            <LandingSection onNavigate={scrollToSection} />
          </div>

          <div className="page-section" ref={el => sectionRefs.current['hero'] = el} id="hero">
            <HeroSection />
          </div>

          <div className="page-section" ref={el => sectionRefs.current['services'] = el} id="services">
            <ServicesSection onNavigate={scrollToSection} />
          </div>

          <div className="page-section" ref={el => sectionRefs.current['rooms'] = el} id="rooms">
            <RoomCarousel />
          </div>

          <div className="page-section" ref={el => sectionRefs.current['portfolio'] = el} id="portfolio">
            <PortfolioSection />
          </div>

          <div className="page-section" ref={el => sectionRefs.current['stories'] = el} id="stories">
            <StoriesSection />
          </div>

          <div className="page-section" ref={el => sectionRefs.current['estimate'] = el} id="estimate">
            <EstimateSection />
          </div>

          <div className="page-section" ref={el => sectionRefs.current['footer'] = el} id="footer">
            <Footer />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
