// src/components/Sidebar.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { Link } from './Link';

export const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { url } = useLocation();

// Close sidebar when route changes on mobile
useEffect(() => {
  setIsOpen(false);
  }, [url]);
  return (
    <>
      {/* Mobile menu button - only visible on small screens */}
      <button
        className="btn btn-square btn-ghost md:hidden fixed top-20 right-4 z-50"
        onClick={() => setIsOpen(!isOpen)}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar - fixed position on mobile, static on desktop */}
      <aside className={`fixed md:static top-20 right-0 z-40 h-[calc(100vh-5rem)] w-64 bg-base-200 text-base-content transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : 'translate-x-full'} md:translate-x-0 md:w-64 md:z-auto`}>
        <div className="p-4">
          <h2 className="text-lg font-semibold mb-4">Navigation</h2>
          <ul className="menu menu-compact">
            <li><Link href="/" variant="ghost" onClick={() => setIsOpen(false)}>Home</Link></li>
            <li><Link href="/items" variant="ghost" onClick={() => setIsOpen(false)}>Items</Link></li>
            <li><Link href="/handbooks" variant="ghost" onClick={() => setIsOpen(false)}>Handbooks</Link></li>
            <li><Link href="/handbooks/types" variant="ghost" onClick={() => setIsOpen(false)}>Handbook Types</Link></li>
          </ul>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </>
  );
};