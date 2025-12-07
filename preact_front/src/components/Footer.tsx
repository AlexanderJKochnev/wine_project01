// src/components/Footer.tsx
import { h } from 'preact';

export const Footer = () => {
  return (
    <footer className="bg-base-200 text-base-content p-4 border-t">
      <div className="container mx-auto text-center">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-2 md:mb-0">
            <p>&copy; {new Date().getFullYear()} Wine App. All rights reserved.</p>
          </div>
          <div className="flex flex-wrap justify-center gap-4">
            <a href="/contacts" className="link link-hover">Contacts</a>
            <a href="/sitemap" className="link link-hover">Sitemap</a>
            <a href="/about" className="link link-hover">About</a>
          </div>
        </div>
      </div>
    </footer>
  );
};