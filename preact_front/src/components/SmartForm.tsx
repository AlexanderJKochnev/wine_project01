// src/components/SmartForm.tsx
import { h } from 'preact';
import { useState, useEffect } from 'preact/hooks';
import { FieldConfig } from '../types/schema';
import { FieldRenderer } from './FieldRenderer';

interface SmartFormProps {
  schema: FieldConfig[];
  onSubmit: (data: Record<string, any>) => void; // ← исправлено: добавлено имя "data"
  initialValues?: Record<string, any>;
  disabled?: boolean;
}

export const SmartForm = ({ schema, onSubmit, initialValues = {}, disabled = false }: SmartFormProps) => {
  const [values, setValues] = useState<Record<string, any>>(initialValues);

  useEffect(() => {
    setValues(initialValues);
  }, [initialValues]);

  const handleChange = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    onSubmit(values);
  };

  return (
    <form onSubmit={handleSubmit}>
      {schema.map(field => (
        <FieldRenderer
          key={field.name}
          field={field}
          value={values[field.name]}
          onChange={value => handleChange(field.name, value)}
        />
      ))}
      <button type="submit" disabled={disabled}>
        {disabled ? 'Отправка...' : 'Сохранить'}
      </button>
    </form>
  );
};