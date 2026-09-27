import { WhatsAppIcon, PhoneIcon } from '../icons';
import {
  ESTIMATE_LINK,
  PHONE_NUMBER,
  PHONE_DISPLAY,
  WHATSAPP_DISPLAY,
  EMAIL,
  STUDIO_HOURS
} from '../../data/contact';
import { MaskReveal } from '../motion';
import './Footer.css';
import { sheetNumber } from '../../data/journey';

const sheet = sheetNumber('footer');

const Footer = () => {
  return (
    <footer className="footer-section">
      <div className="footer-content">

        <div className="footer-invite">
          <p className="annotation footer-eyebrow">
            {sheet.n} <span className="tick">/</span> {sheet.total} — Start a project
          </p>
          <MaskReveal className="footer-headline">
            Every home here started as a sketch.<br />
            <span className="accent">Let's draw yours</span><span className="dot">.</span>
          </MaskReveal>
          <div className="footer-reach">
            <a href={`mailto:${EMAIL}`} className="footer-email">
              {EMAIL}
            </a>
            <a
              className="footer-wa"
              href={ESTIMATE_LINK}
              target="_blank"
              rel="noreferrer"
            >
              <WhatsAppIcon size={20} />
              <span>Message us on WhatsApp</span>
            </a>
          </div>
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
              <li><a href="#stories">Client stories</a></li>
              <li><a href="#/gallery">Gallery</a></li>
              <li><a href="#living">Walk the house</a></li>
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
              <li>170 2nd Block, Banashankari 6th Stage 1st Block</li>
              <li>Channasandra, Bengaluru, Karnataka 560098</li>
              <li>
                <a className="footer-contact" href={`tel:${PHONE_NUMBER}`}>
                  <PhoneIcon size={14} />
                  {PHONE_DISPLAY}
                </a>
              </li>
              <li>
                <a
                  className="footer-contact is-whatsapp"
                  href={ESTIMATE_LINK}
                  target="_blank"
                  rel="noreferrer"
                >
                  <WhatsAppIcon size={15} />
                  {WHATSAPP_DISPLAY}
                </a>
              </li>
              <li>{STUDIO_HOURS}</li>
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
          <span>Designed &amp; built in Bengaluru</span>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
