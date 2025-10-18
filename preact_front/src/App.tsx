// src/App.tsx
import { EditDrinkForm } from './components/EditDrinkForm';
import { h, useState, useEffect } from 'preact/hooks';
import { getAuthToken } from './lib/apiClient';
import { LoginForm } from './components/LoginForm';
import { DrinkCreateForm } from './components/DrinkCreateForm';
import { DrinkView } from './components/DrinkView';
import { ItemTable } from './components/ItemTable';
import { useNotification } from './hooks/useNotification';
import { Notification } from './components/Notification';
import { apiClient } from './lib/apiClient';

interface ReferenceData {
  subcategories: any[];
  subregions: any[];
  sweetnesses: any[];
  foods: any[];
  varietals: any[];
}

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState<'drinks' | 'items'>('drinks');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null); // ← добавлено!
  const [references, setReferences] = useState<ReferenceData | null>(null);
  const { notifications, showNotification } = useNotification();

  // Загружаем справочники один раз при старте
  useEffect(() => {
    const loadReferences = async () => {
      try {
        const [
          subcategories,
          subregions,
          sweetnesses,
          foods,
          varietals
        ] = await Promise.all([
          apiClient<any[]>('/subcategories/all'),
          apiClient<any[]>('/subregions/all'),
          apiClient<any[]>('/sweetnesses/all'),
          apiClient<any[]>('/foods/all'),
          apiClient<any[]>('/varietals/all'),
        ]);
        setReferences({ subcategories, subregions, sweetnesses, foods, varietals });
      } catch (err) {
        console.error('Failed to load reference data', err);
      }
    };
    loadReferences();
  }, []);

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

  const handleEdit = (id: number) => {
    if (!references) {
      // alert('Загрузка данных...');
      console.warn('Справочники ещё не загружены');
      return;
    }
    setEditingId(id); // ← теперь определено
  };

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  if (!references) {
    return <p>Загрузка справочников...</p>;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Dashboard</h1>

      {/* Верхнее меню */}
      <div style={{ marginBottom: '16px', display: 'flex', gap: '12px' }}>
        <button
          onClick={() => {
            setActiveTab('drinks');
            setShowForm(false);
            setEditingId(null); // ← закрываем форму редактирования
          }}
          style={{
            padding: '8px 16px',
            backgroundColor: activeTab === 'drinks' ? '#007bff' : 'white',
            color: activeTab === 'drinks' ? 'white' : '#000',
            border: '1px solid #ccc',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Напитки
        </button>
        <button
          onClick={() => {
            setActiveTab('items');
            setShowForm(false);
            setEditingId(null);
          }}
          style={{
            padding: '8px 16px',
            backgroundColor: activeTab === 'items' ? '#007bff' : 'white',
            color: activeTab === 'items' ? 'white' : '#000',
            border: '1px solid #ccc',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Позиции
        </button>
      </div>

      {/* Кнопка "Добавить" */}
      {activeTab === 'drinks' && !showForm && !editingId && (
        <button
          onClick={() => setShowForm(true)}
          style={{
            marginBottom: '16px',
            padding: '8px 16px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          + Добавить напиток
        </button>
      )}

      {/* Форма или таблица */}
      {showForm ? (
        <DrinkCreateForm
          references={references}
          onCreated={() => {
            showNotification('Напиток создан!', 'success');
            setShowForm(false);
          }}
          onCancel={() => setShowForm(false)}
        />
      ) : editingId ? (
        <EditDrinkForm
          id={editingId}
          references={references}
          onClose={() => setEditingId(null)}
          onEdited={() => {
            showNotification('Напиток обновлён!', 'success');
            setEditingId(null);
          }}
        />
      ) : activeTab === 'drinks' ? (
        <DrinkView references={references} onEdit={handleEdit} />
      ) : (
        <ItemTable />
      )}

      {/* Уведомления */}
      {notifications.map(n => (
        <Notification
          key={n.id}
          message={n.message}
          type={n.type}
          onClose={() => {}}
        />
      ))}
    </div>
  );
}