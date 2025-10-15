// src/components/DrinkCreateForm.tsx
import { h } from 'preact'; // ← h из 'preact'
import { useState } from 'preact/hooks'; // ← useState из 'preact/hooks'
import { SmartForm } from './SmartForm';
import { getDrinkCreateSchema } from '../lib/schemaMapper';
import { apiClient } from '../lib/apiClient';

export const DrinkCreateForm = () => {
  const [submitStatus, setSubmitStatus] = useState<string | null>(null);

  const handleSubmit = async (data: Record<string, any>) => {
    setSubmitStatus('Отправка...');
    try {
      // Преобразуем many-to-many поля в массив ID
      const payload = {
        ...data,
        // foods: data.foods — уже массив ID (благодаря SmartForm)
        // varietals: data.varietals — тоже массив ID
      };

      // Отправляем в FastAPI
      const result = await apiClient('/drinks', {
        method: 'POST',
        body: payload,
      });

      console.log('Успешно создано:', result);
      setSubmitStatus('✅ Напиток создан!');
    } catch (err: any) {
      console.error('Ошибка создания:', err);
      setSubmitStatus(`❌ Ошибка: ${err.message}`);
    }
  };

  return (
    <div>
      <h2>Добавить напиток</h2>
      {submitStatus && <p>{submitStatus}</p>}
      <SmartForm schema={getDrinkCreateSchema()} onSubmit={handleSubmit} />
    </div>
  );
};