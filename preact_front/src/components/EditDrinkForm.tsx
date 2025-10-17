// src/components/EditDrinkForm.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { apiClient } from '../lib/apiClient';
import { SmartForm } from './SmartForm';
import { getDrinkCreateSchema } from '../lib/schemaMapper';

interface EditDrinkFormProps {
  id: number;
  onClose: () => void;
  onEdited: () => void;
}

export const EditDrinkForm = ({ id, onClose, onEdited }: EditDrinkFormProps) => {
  const [initialData, setInitialData] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchDrink = async () => {
      try {
        // Используем /api — возвращает вложенные объекты с id
        const drink = await apiClient<any>(`/drinks/${id}/api`);
        const data = {
          title: drink.title || '',
          subcategory_id: drink.subcategory?.id,
          subregion_id: drink.subregion?.id,
          sweetness_id: drink.sweetness?.id,
          alc: drink.alc ? parseFloat(drink.alc) : undefined,
          sugar: drink.sugar ? parseFloat(drink.sugar) : undefined,
          age: drink.age || '',
          sparkling: drink.sparkling || false,
          // foods и varietals — пока не редактируем
        };
        setInitialData(data);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchDrink();
  }, [id]);

  const handleSubmit = async (data: Record<string, any>) => {
    setLoading(true);
    try {
      await apiClient(`/drinks/${id}`, {
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

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1500, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', maxWidth: '600px', width: '90%', maxHeight: '80vh', overflowY: 'auto' }}>
        <h2>Редактировать напиток</h2>
        <SmartForm
          schema={getDrinkCreateSchema()}
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