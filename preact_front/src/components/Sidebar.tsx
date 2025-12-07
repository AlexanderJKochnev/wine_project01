// src/components/Sidebar.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';
import { Link } from './Link';

export const Sidebar = () => {
  const { url } = useLocation();

  return (
    <aside className="navbar">
      <div>
        <h2>Navigation</h2>
        <ul className="nav-menu">
          <li><Link href="/" className={url === '/' ? 'active' : ''}>Home</Link></li>
          <li><Link href="/items" className={url === '/items' ? 'active' : ''}>Items</Link></li>
          <li><Link href="/handbooks" className={url === '/handbooks' ? 'active' : ''}>Handbooks</Link></li>
        </ul>
      </div>
    </aside>
  );
};