// src/components/Sidebar.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';
import { Link } from './Link';

interface SidebarProps {
  onClose?: () => void;
}

export const Sidebar = ({ onClose }: SidebarProps) => {
  const { url } = useLocation();

  return (
    <aside className="navbar">
      <div>
        <div className="sidebar-header">
          <h2>Navigation</h2>
          {/* Close button for mobile */}
          <button 
            className="close-sidebar-btn lg:hidden"
            onClick={onClose}
            aria-label="Close navigation menu"
          >
            ×
          </button>
        </div>
        <ul className="nav-menu">
          <li><Link href="/" className={url === '/' ? 'active' : ''}>Home</Link></li>
          <li><Link href="/items" className={url === '/items' ? 'active' : ''}>Items</Link></li>
          <li><Link href="/handbooks" className={url === '/handbooks' ? 'active' : ''}>Handbooks</Link></li>
        </ul>
      </div>
    </aside>
  );
};