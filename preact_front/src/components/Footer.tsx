// src/components/Footer.tsx
import { h } from 'preact';

export const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div>
          <p>&copy; {new Date().getFullYear()} THE VERY GOOD SITE. All rights reserved.</p>
        </div>
        <div className="footer-links">
          <a href="/contacts" className="footer-link">Contacts</a>
          <a href="/sitemap" className="footer-link">Sitemap</a>
          <a href="/about" className="footer-link">About</a>
        </div>
      </div>
    </footer>
  );
};