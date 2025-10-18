// src/components/DrinkCreateForm.tsx
import { h, useState } from 'preact/hooks';
import { MUIForm } from './MUIForm';
import { getDrinkCreateSchema } from '../lib/schemaMapper';

interface ReferenceData {
  subcategories: any[];
  subregions: any[];
  sweetnesses: any[];
  foods: any[];
  varietals: any[];
}

interface DrinkCreateFormProps {
  references: ReferenceData;
  onCreated?: () => void;
  onCancel?: () => void;
}

export const DrinkCreateForm = ({ references, onCreated, onCancel }: DrinkCreateFormProps) => {
  const [submitStatus, setSubmitStatus] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: Record<string, any>) => {
    setIsSubmitting(true);
    setSubmitStatus(null);
    try {
      // Отправка данных
      const response = await fetch('/proxy-api/drinks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(await response.text());
      setSubmitStatus('✅ Напиток создан!');
      if (onCreated) onCreated();
    } catch (err: any) {
      setSubmitStatus(`❌ Ошибка: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h2>Добавить напиток</h2>
      {submitStatus && <p>{submitStatus}</p>}
      <MUIForm
        schema={getDrinkCreateSchema()}
        onSubmit={handleSubmit}
        disabled={isSubmitting}
        references={references} // ← передаём справочники
      />
      <div style={{ marginTop: '16px' }}>
        <button onClick={onCancel} style={{ marginRight: '10px' }}>
          Отмена
        </button>
      </div>
    </div>
  );
};