// src/components/Sidebar.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';
import { Link } from './Link';

export const Sidebar = () => {
  const { url } = useLocation();

  return (
    <aside className="w-64 bg-base-200 text-base-content h-full border-l">
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4">Navigation</h2>
        <ul className="menu menu-compact">
          <li><Link href="/" variant="ghost">Home</Link></li>
          <li><Link href="/items" variant="ghost">Items</Link></li>
          <li><Link href="/handbooks" variant="ghost">Handbooks</Link></li>
          <li><Link href="/handbooks/types" variant="ghost">Handbook Types</Link></li>
        </ul>
      </div>
    </aside>
  );
};