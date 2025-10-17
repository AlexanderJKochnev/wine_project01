// src/components/DrinkCreateForm.tsx
import { h, useState } from 'preact/hooks';
import { SmartForm } from './SmartForm';
import { getDrinkCreateSchema } from '../lib/schemaMapper';
import { apiClient } from '../lib/apiClient';

interface DrinkCreateFormProps {
  onCreated?: () => void;
}

export const DrinkCreateForm = ({ onCreated }: DrinkCreateFormProps) => {
  const [submitStatus, setSubmitStatus] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: Record<string, any>) => {
    setIsSubmitting(true);
    setSubmitStatus(null);
    try {
      await apiClient('/drinks', {
        method: 'POST',
        body: data,
      });
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
      <SmartForm
        schema={getDrinkCreateSchema()}
        onSubmit={handleSubmit}
        disabled={isSubmitting}
      />
    </div>
  );
};