// src/App.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { getAuthToken } from './lib/apiClient';
import { LoginForm } from './components/LoginForm';
import { DrinkCreateForm } from './components/DrinkCreateForm';
import { DrinkTable } from './components/DrinkTable';
import { ItemTable } from './components/ItemTable';
import { useNotification } from './hooks/useNotification';
import { Notification } from './components/Notification';

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState<'drinks' | 'items'>('drinks');
  const { notifications, showNotification } = useNotification();

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    showNotification('Добро пожаловать!', 'success');
  };

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Dashboard</h1>
      <div style={{ marginBottom: '16px' }}>
        <button onClick={() => setActiveTab('drinks')}>Напитки</button>
        <button onClick={() => setActiveTab('items')}>Позиции</button>
      </div>

      {activeTab === 'drinks' ? (
        <DrinkCreateForm onCreated={() => showNotification('Напиток создан!', 'success')} />
      ) : null}

      {activeTab === 'drinks' ? <DrinkTable /> : <ItemTable />}

      {/* Уведомления */}
      {notifications.map(n => (
        <Notification
          key={n.id}
          message={n.message}
          type={n.type}
          onClose={() => {
            const updated = notifications.filter(nn => nn.id !== n.id);
            // Обновление через замыкание — для простоты
            // В реальном проекте лучше использовать context или store
          }}
        />
      ))}
    </div>
  );
}