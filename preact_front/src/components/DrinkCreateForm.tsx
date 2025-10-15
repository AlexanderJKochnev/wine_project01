// src/components/DrinkCreateForm.tsx
import { h } from 'preact';
import { SmartForm } from './SmartForm';
import { getDrinkCreateSchema } from '../lib/schemaMapper';

export const DrinkCreateForm = () => {
  const handleSubmit = (data: Record<string, any>) => {
    console.log('Отправка данных:', data);
    // TODO: вызвать POST /drinks
  };

  return (
    <div>
      <h2>Добавить напиток</h2>
      <SmartForm schema={getDrinkCreateSchema()} onSubmit={handleSubmit} />
    </div>
  );
};