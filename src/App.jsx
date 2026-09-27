import { useEffect, useState, useRef, useCallback } from 'react';
import Lenis from 'lenis';
import { useProgress } from '@react-three/drei';
import { setLenis } from './lib/scroll';
import { useLoading } from './context/LoadingContext';
import HouseJourney, { JOURNEY_IDS, heroImageFor } from './components/HouseJourney';
import LaserPointer from './components/LaserPointer';
import GalleryPage from './components/GalleryPage';
import Loading from './components/sections/Loading';
import LandingSection from './components/sections/LandingSection';
import HeroSection from './components/sections/HeroSection';
import ServicesSection from './components/sections/ServicesSection';
import EntrySection from './components/sections/EntrySection';
import RoomStop from './components/sections/RoomStop';
import PortfolioSection from './components/sections/PortfolioSection';
import StoriesSection from './components/sections/StoriesSection';
import EstimateSection from './components/sections/EstimateSection';
import Footer from './components/sections/Footer';
import StaggeredMenu from './components/sections/StaggeredMenu';
import { walkRooms } from './data/rooms';
import './App.css';

/*
  Scroll order is the walk through the house. It comes from the Blender build
  (houseAnchors.json, via JOURNEY_IDS) so the page and the camera can never
  disagree about what a section is called.
*/
const SECTION_IDS = JOURNEY_IDS;

/* Sections that sit on a dark photographic ground; the header and the fixed
   page counter switch to light type over these. */
const DARK_SECTIONS = new Set(['landing', 'hero', 'entry', ...walkRooms.map((r) => r.id)]);

const menuItems = [
  { label: 'Home', ariaLabel: 'Go to landing', link: '#landing' },
  { label: 'About', ariaLabel: 'Learn about us', link: '#hero' },
  { label: 'Services', ariaLabel: 'What we design', link: '#services' },
  { label: 'Walk the house', ariaLabel: 'Start the walkthrough', link: '#living' },
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

  const { isLoading } = useLoading();
  const { active, progress, total } = useProgress();
  const [percent, setPercent] = useState(0);
  const loaderStarted = useRef(false);

  // The house model drives the splash screen's progress.
  useEffect(() => {
    if (total > 0) {
      loaderStarted.current = true;
      setPercent((p) => Math.max(p, Math.round(progress)));
    }
  }, [progress, total]);

  // Finished loading: go straight to 100 rather than waiting out a timer.
  useEffect(() => {
    if (loaderStarted.current && !active) setPercent(100);
  }, [active]);

  // The splash lifts onto the landing render, so wait until it is decoded
  // (with the same ceiling as the model, below) rather than reveal a blank.
  const [heroReady, setHeroReady] = useState(false);
  useEffect(() => {
    const img = new Image();
    img.src = heroImageFor(window);
    const ok = () => setHeroReady(true);
    (img.decode ? img.decode() : Promise.reject()).then(ok, () => { img.onload = ok; img.onerror = ok; });
    const ceiling = setTimeout(ok, 14000);
    return () => clearTimeout(ceiling);
  }, []);

  useEffect(() => {
    // Nothing ever registered with the loader — the model was cached, or WebGL
    // is unavailable — so don't hold the door shut.
    const quick = setTimeout(() => {
      if (!loaderStarted.current) setPercent(100);
    }, 2500);
    // And a ceiling, so a slow network can never trap anyone on the splash.
    const ceiling = setTimeout(() => setPercent(100), 14000);
    return () => {
      clearTimeout(quick);
      clearTimeout(ceiling);
    };
  }, []);

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

  // Lets CSS start the landing's entrance as the splash lifts, not behind it
  useEffect(() => {
    document.documentElement.dataset.splash = isLoading ? 'on' : 'off';
  }, [isLoading]);

  // Hold the page still behind the splash screen
  useEffect(() => {
    const lenis = lenisRef.current;
    if (!lenis) return;
    if (isLoading) {
      lenis.stop();
      lenis.scrollTo(0, { immediate: true });
    } else {
      lenis.start();
    }
  }, [isLoading]);

  const scrollToSection = useCallback((id, immediate = false) => {
    const target = sectionRefs.current[id];
    if (!target || !lenisRef.current) return;
    lenisRef.current.scrollTo(target, { immediate, offset: 0 });
  }, []);

  // Track which section owns the viewport centre (home page only)
  useEffect(() => {
    if (route !== 'home') return;
    const lenis = lenisRef.current;

    // Flip on the section reaching the top of the viewport, which is the same
    // rule the camera uses. Using the viewport centre made the copy and the
    // scrim change half a screen before the camera arrived.
    const update = () => {
      const probe = window.scrollY + 4;
      let current = SECTION_IDS[0];
      for (const id of SECTION_IDS) {
        const el = sectionRefs.current[id];
        if (el && el.offsetTop <= probe) current = id;
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

  // Where you were on the home page when you left it for the gallery, so
  // coming back (the gallery's back link, or the browser's) puts you in the
  // same room rather than at the top
  const lastHomeSection = useRef(null);
  useEffect(() => {
    if (route === 'home' && activeSection !== 'gallery') lastHomeSection.current = activeSection;
  }, [route, activeSection]);

  // Entering a page: gallery starts at the top; home honours a pending anchor,
  // else returns you to where you left it
  useEffect(() => {
    if (route === 'gallery') {
      lenisRef.current?.scrollTo(0, { immediate: true });
      setActiveSection('gallery');
      return;
    }
    const id = pendingSection.current || lastHomeSection.current;
    pendingSection.current = null;
    if (id && id !== 'landing') {
      // After the sections have mounted and laid out. Lenis still holds the
      // gallery's shorter page height, which would clamp the jump: re-measure
      // it first.
      requestAnimationFrame(() => requestAnimationFrame(() => {
        lenisRef.current?.resize();
        scrollToSection(id, true);
      }));
    } else {
      lenisRef.current?.scrollTo(0, { immediate: true });
      setActiveSection('landing');
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
      if (e.target.matches('input, textarea, select, button')) return;
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
  const darkTone = route === 'home' && DARK_SECTIONS.has(activeSection);

  useEffect(() => {
    document.body.dataset.tone = darkTone ? 'dark' : 'light';
  }, [darkTone]);

  return (
    <div className="app">
      {isLoading && <Loading percent={percent} ready={heroReady} />}

      <LaserPointer />

      <StaggeredMenu
        isFixed={true}
        position="right"
        items={menuItems}
        socialItems={socialItems}
        displaySocials={true}
        displayItemNumbering={true}
        menuButtonColor={darkTone ? '#ffffff' : '#14171b'}
        openMenuButtonColor="#14171b"
        changeMenuColorOnOpen={true}
        colors={['#f6f5f3', '#d7141e']}
        accentColor="#d7141e"
        logoUrl="/bh-logo.png"
      />

      <HouseJourney activeSection={route === 'gallery' ? 'gallery' : activeSection} />

      {route === 'gallery' ? (
        <GalleryPage />
      ) : (
        <>
          <div
            className="sheet-indicator"
            style={{ '--sheet-progress': (sectionIndex + 1) / SECTION_IDS.length }}
            aria-hidden="true"
          >
            <span className="sheet-current">{String(sectionIndex + 1).padStart(2, '0')}</span>
            <span className="sheet-rule"></span>
            <span>{String(SECTION_IDS.length).padStart(2, '0')}</span>
          </div>

          <div className="page-section" ref={(el) => (sectionRefs.current['landing'] = el)} id="landing">
            <LandingSection onNavigate={scrollToSection} revealed={!isLoading} />
          </div>

          <div className="page-section" ref={(el) => (sectionRefs.current['hero'] = el)} id="hero">
            <HeroSection />
          </div>

          <div className="page-section" ref={(el) => (sectionRefs.current['services'] = el)} id="services">
            <ServicesSection onNavigate={scrollToSection} />
          </div>

          {/* The hall: Services lifts off the living room's doors, which open as you scroll */}
          <div className="page-section" ref={(el) => (sectionRefs.current['entry'] = el)} id="entry">
            <EntrySection />
          </div>

          {/* The walk: one section per room, all transparent over the 3D house.
              Only the five walk rooms are shown; the others stay in the model. */}
          {walkRooms.map((room, i) => (
            <div
              key={room.id}
              className="page-section"
              ref={(el) => (sectionRefs.current[room.id] = el)}
              id={room.id}
            >
              <RoomStop
                room={room}
                index={i}
                total={walkRooms.length}
                isActive={activeSection === room.id}
              />
            </div>
          ))}

          <div className="page-section" ref={(el) => (sectionRefs.current['portfolio'] = el)} id="portfolio">
            <PortfolioSection />
          </div>

          <div className="page-section" ref={(el) => (sectionRefs.current['stories'] = el)} id="stories">
            <StoriesSection />
          </div>

          <div className="page-section" ref={(el) => (sectionRefs.current['estimate'] = el)} id="estimate">
            <EstimateSection />
          </div>

          <div className="page-section" ref={(el) => (sectionRefs.current['footer'] = el)} id="footer">
            <Footer />
          </div>
        </>
      )}
    </div>
  );
}

export default App;
