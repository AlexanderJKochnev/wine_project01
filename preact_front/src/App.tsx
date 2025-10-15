// src/App.tsx
import { TestCategories } from './components/TestCategories';

export function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Dashboard</h1>
      <TestCategories />
    </div>
  );
}