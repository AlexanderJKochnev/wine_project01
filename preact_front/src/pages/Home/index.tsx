// src/pages/Home.tsx
import { h } from 'preact';
import { Link } from '../../components/Link';

export function Home() {
  return (
    <div className="hero min-h-96 bg-base-200 rounded-box">
      <div className="hero-content text-center">
        <div className="max-w-md">
          <h1 className="text-5xl font-bold">Welcome to Wine App</h1>
          <p className="py-6">
            Discover and manage wine items and reference data with our intuitive interface.
          </p>
          <div className="flex flex-col gap-4">
            <Link href="/items" variant="primary">
              Browse Items
            </Link>
            <Link href="/handbooks" variant="secondary">
              Manage Handbooks
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
