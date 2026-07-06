import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer-section">
      <div className="footer-content">

        <div className="footer-invite">
          <p className="annotation footer-eyebrow">
            08 <span className="tick">/</span> 08 — Start a project
          </p>
          <h2 className="footer-headline">
            Every home here started<br />as a sketch. <em>Let's draw yours.</em>
          </h2>
          <a href="mailto:hello@betterhomes.in" className="footer-email">
            hello@betterhomes.in
          </a>
        </div>

        <div className="footer-grid">
          <div className="footer-column">
            <h4 className="annotation">Services</h4>
            <ul>
              <li><a href="#services">Modular Kitchen</a></li>
              <li><a href="#services">Living Room</a></li>
              <li><a href="#services">Bedroom</a></li>
              <li><a href="#services">Full Home</a></li>
              <li><a href="#services">Commercial Interiors</a></li>
            </ul>
          </div>

          <div className="footer-column">
            <h4 className="annotation">Studio</h4>
            <ul>
              <li><a href="#hero">About</a></li>
              <li><a href="#portfolio">Portfolio</a></li>
              <li><a href="#gallery">Gallery</a></li>
              <li><a href="#rooms">The spaces</a></li>
              <li><a href="#estimate">Free estimate</a></li>
            </ul>
          </div>

          <div className="footer-column">
            <h4 className="annotation">Locations</h4>
            <ul>
              <li>Whitefield</li>
              <li>Koramangala</li>
              <li>Indiranagar</li>
              <li>HSR Layout</li>
              <li>Electronic City</li>
            </ul>
          </div>

          <div className="footer-column">
            <h4 className="annotation">Visit</h4>
            <ul>
              <li>100 Feet Road, Indiranagar</li>
              <li>Bangalore 560038</li>
              <li><a href="tel:+919876543210">+91 98765 43210</a></li>
              <li>Mon–Sat, 10AM–7PM</li>
            </ul>
          </div>

          <div className="footer-column">
            <h4 className="annotation">Follow</h4>
            <ul>
              <li><a href="https://instagram.com" target="_blank" rel="noreferrer">Instagram</a></li>
              <li><a href="https://pinterest.com" target="_blank" rel="noreferrer">Pinterest</a></li>
              <li><a href="https://linkedin.com" target="_blank" rel="noreferrer">LinkedIn</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom annotation">
          <span>&copy; 2026 Better Homes — Crafting Better Living</span>
          <span>Drawn at blue hour</span>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
