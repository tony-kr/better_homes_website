import { useEffect, useState, useRef, useCallback } from 'react';
import House3D from './components/House3D';
import LandingSection from './components/sections/LandingSection';
import HeroSection from './components/sections/HeroSection';
import ServicesSection from './components/sections/ServicesSection';
import RoomCarousel from './components/sections/RoomCarousel';
import PortfolioSection from './components/sections/PortfolioSection';
import GallerySection from './components/sections/GallerySection';
import EstimateSection from './components/sections/EstimateSection';
import Footer from './components/sections/Footer';
import StaggeredMenu from './components/sections/StaggeredMenu';
import './App.css';

// Definitions required for the menu and scroll logic
const SECTION_IDS = ['landing', 'hero', 'services', 'rooms', 'portfolio', 'gallery', 'estimate', 'footer'];
const SCROLL_COOLDOWN = 1000;

const menuItems = [
  { label: 'Home', ariaLabel: 'Go to landing', link: '#landing' },
  { label: 'About', ariaLabel: 'Learn about us', link: '#hero' },
  { label: 'Services', ariaLabel: 'What we design', link: '#services' },
  { label: 'Experience', ariaLabel: 'Explore the spaces', link: '#rooms' },
  { label: 'Portfolio', ariaLabel: 'Featured projects', link: '#portfolio' },
  { label: 'Gallery', ariaLabel: 'Real homes gallery', link: '#gallery' },
  { label: 'Free Estimate', ariaLabel: 'Get a free estimate', link: '#estimate' },
  { label: 'Contact', ariaLabel: 'Get in touch', link: '#footer' }
];

const socialItems = [
  { label: 'Instagram', link: 'https://instagram.com' },
  { label: 'Pinterest', link: 'https://pinterest.com' },
  { label: 'LinkedIn', link: 'https://linkedin.com' }
];

function App() {
  const [currentPage, setCurrentPage] = useState(0);
  const [galleryFilter, setGalleryFilter] = useState('all');
  const currentPageRef = useRef(0);
  const isScrolling = useRef(false);
  const sectionRefs = useRef({});
  const appRef = useRef(null);

  const activeSection = SECTION_IDS[currentPage];

  const goToPage = useCallback((pageIndex) => {
    if (pageIndex < 0 || pageIndex >= SECTION_IDS.length) return;
    if (pageIndex === currentPageRef.current) return;

    isScrolling.current = true;
    currentPageRef.current = pageIndex;
    setCurrentPage(pageIndex);

    const target = sectionRefs.current[SECTION_IDS[pageIndex]];
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    setTimeout(() => {
      isScrolling.current = false;
    }, SCROLL_COOLDOWN);
  }, []);

  const goToSection = useCallback((id) => {
    goToPage(SECTION_IDS.indexOf(id));
  }, [goToPage]);

  // Start at the top on load — browser scroll restoration can land mid-section
  useEffect(() => {
    if (appRef.current) appRef.current.scrollTop = 0;
  }, []);

  useEffect(() => {
    const container = appRef.current;
    if (!container) return;

    const handleWheel = (e) => {
      e.preventDefault();
      if (isScrolling.current) return;
      const direction = e.deltaY > 0 ? 1 : -1;
      goToPage(currentPageRef.current + direction);
    };

    const handleKeyDown = (e) => {
      if (isScrolling.current) return;
      if (e.key === 'ArrowDown' || e.key === 'PageDown') {
        e.preventDefault();
        goToPage(currentPageRef.current + 1);
      } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
        e.preventDefault();
        goToPage(currentPageRef.current - 1);
      }
    };

    // Keep page state in sync with any in-page anchor (menu links etc.)
    const handleAnchorClick = (e) => {
      const anchor = e.target.closest('a[href^="#"]');
      if (!anchor) return;
      const id = anchor.getAttribute('href').slice(1);
      if (!SECTION_IDS.includes(id)) return;
      e.preventDefault();
      goToPage(SECTION_IDS.indexOf(id));
    };

    container.addEventListener('wheel', handleWheel, { passive: false });
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('click', handleAnchorClick);

    return () => {
      container.removeEventListener('wheel', handleWheel);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('click', handleAnchorClick);
    };
  }, [goToPage]);

  // Sync state on native scrolling (touch devices use scroll-snap, not wheel paging)
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (isScrolling.current) return;
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const index = SECTION_IDS.indexOf(entry.target.id);
            if (index !== -1 && index !== currentPageRef.current) {
              currentPageRef.current = index;
              setCurrentPage(index);
            }
          }
        });
      },
      { root: appRef.current, threshold: 0.6 }
    );
    SECTION_IDS.forEach((id) => {
      const el = sectionRefs.current[id];
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="app" ref={appRef}>
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

      <div
        className={`sheet-indicator ${activeSection === 'rooms' ? 'on-light' : ''}`}
        style={{ '--sheet-progress': (currentPage + 1) / SECTION_IDS.length }}
        aria-hidden="true"
      >
        <span className="sheet-current">{String(currentPage + 1).padStart(2, '0')}</span>
        <span className="sheet-rule"></span>
        <span>{String(SECTION_IDS.length).padStart(2, '0')}</span>
      </div>

      <div className="page-section" ref={el => sectionRefs.current['landing'] = el} id="landing">
        <LandingSection onNavigate={goToSection} />
      </div>

      <div className="page-section" ref={el => sectionRefs.current['hero'] = el} id="hero">
        <HeroSection />
      </div>

      <div className="page-section" ref={el => sectionRefs.current['services'] = el} id="services">
        <ServicesSection onNavigate={goToSection} />
      </div>

      <div className="page-section" ref={el => sectionRefs.current['rooms'] = el} id="rooms">
        <RoomCarousel
          onSeeProjects={(roomId) => {
            setGalleryFilter(roomId);
            goToSection('gallery');
          }}
        />
      </div>

      <div className="page-section" ref={el => sectionRefs.current['portfolio'] = el} id="portfolio">
        <PortfolioSection />
      </div>

      <div className="page-section" ref={el => sectionRefs.current['gallery'] = el} id="gallery">
        <GallerySection filter={galleryFilter} onFilterChange={setGalleryFilter} />
      </div>

      <div className="page-section" ref={el => sectionRefs.current['estimate'] = el} id="estimate">
        <EstimateSection />
      </div>

      <div className="page-section" ref={el => sectionRefs.current['footer'] = el} id="footer">
        <Footer />
      </div>
    </div>
  );
}

export default App;
