// src/components/SmartForm.tsx
import { h } from 'preact'; // ← h из preact
import { useState } from 'preact/hooks'; // ← useState из hooks
import { FieldConfig } from '../types/schema';
import { FieldRenderer } from './FieldRenderer';

interface SmartFormProps {
  schema: FieldConfig[];
  onSubmit: (data: Record<string, any>) => void;
  initialValues?: Record<string, any>;
}

export const SmartForm = ({ schema, onSubmit, initialValues = {} }: SmartFormProps) => {
  const [values, setValues] = useState<Record<string, any>>(initialValues);

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
      <button type="submit">Сохранить</button>
    </form>
  );
};