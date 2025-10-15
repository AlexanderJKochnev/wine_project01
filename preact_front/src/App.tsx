// src/App.tsx
import { h } from 'preact';
import { useState, useEffect } from 'preact/hooks';
import { getAuthToken } from './lib/apiClient';
import { LoginForm } from './components/LoginForm';
import { DrinkCreateForm } from './components/DrinkCreateForm';
import { DrinkTable } from './components/DrinkTable';

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Dashboard</h1>
      <DrinkCreateForm />
      <hr />
      <h2>Список напитков</h2>
      <DrinkTable />
    </div>
  );
}