// src/App.tsx
import { h } from 'preact';
import { useEffect } from 'preact/hooks'; // если используете useEffect
import { DrinkCreateForm } from './components/DrinkCreateForm';
import { DrinkTable } from './components/DrinkTable';

export function App() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Dashboard</h1>
      <DrinkCreateForm />
    </div>
  );
}