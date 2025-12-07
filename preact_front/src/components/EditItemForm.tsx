// src/components/EditItemForm.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { apiClient } from '../lib/apiClient';
import { MUIForm } from './MUIForm';
import { useLanguage } from '../contexts/LanguageContext';

interface EditItemFormProps {
  id: number;
  onClose: () => void;
  onEdited: () => void;
}

export const EditItemForm = ({ id, onClose, onEdited }: EditItemFormProps) => {
  const [initialData, setInitialData] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { language } = useLanguage();
  
  useEffect(() => {
    const fetchItem = async () => {
      try {
        const item = await apiClient<any>(`/items_view/detail/${language}/${id}`);
        const data = {
          drink_id: item.drink_id, // ← исправлено: не item.drink.id
          vol: item.vol || undefined,
          price: item.price || undefined,
          count: item.count || 0,
        };
        setInitialData(data);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchItem();
  }, [id, language]);

  const handleSubmit = async (data: Record<string, any>) => { // ← исправлено: добавлено имя "data"
    setLoading(true);
    try {
      await apiClient(`/items/${id}`, {
        method: 'PATCH',
        body: data,
      });
      onEdited();
      onClose();
    } catch (err: any) {
      alert(`Ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (error) return <p>Ошибка загрузки: {error}</p>;
  if (!initialData) return <p>Загрузка...</p>;

  const schema = [
    { name: 'drink_id', label: 'Напиток (ID)', type: 'number', required: true },
    { name: 'vol', label: 'Объём (мл)', type: 'number' },
    { name: 'price', label: 'Цена', type: 'number' },
    { name: 'count', label: 'Количество', type: 'number' },
  ];

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1500, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', maxWidth: '600px', width: '90%', maxHeight: '80vh', overflowY: 'auto' }}>
        <h2>Редактировать позицию</h2>
        <MUIForm
          schema={schema}
          onSubmit={handleSubmit}
          initialValues={initialData}
          disabled={loading}
        />
        <div style={{ marginTop: '16px', textAlign: 'right' }}>
          <button onClick={onClose} style={{ marginRight: '10px' }}>Отмена</button>
        </div>
      </div>
    </div>
  );
};