// src/components/FieldRenderer.tsx
import { h } from 'preact';
import { useEffect } from 'preact/hooks'; // если используете useEffect
import { FieldConfig } from '../types/schema';
import { useSelectOptions } from '../lib/schemaMapper';

interface FieldRendererProps {
  field: FieldConfig;
  value: any;
  onChange: (value: any) => void;
}

export const FieldRenderer = ({ field, value, onChange }: FieldRendererProps) => {
  const { options, loading } = field.type === 'select' || field.type === 'multiselect'
    ? useSelectOptions(`/${field.name.replace('_id', '')}s/all`)
    : { options: [], loading: false };

  if (loading) return <div>Загрузка {field.label}...</div>;

  switch (field.type) {
    case 'string':
    case 'number':
      return (
        <div>
          <label>{field.label}:</label>
          <input
            type={field.type}
            value={value ?? ''}
            onChange={e => onChange(e.currentTarget.value)}
            required={field.required}
          />
        </div>
      );
    case 'boolean':
      return (
        <div>
          <label>
            <input
              type="checkbox"
              checked={!!value}
              onChange={e => onChange(e.currentTarget.checked)}
            />
            {field.label}
          </label>
        </div>
      );
    case 'select':
      return (
        <div>
          <label>{field.label}:</label>
          <select
            value={value ?? ''}
            onChange={e => onChange(Number(e.currentTarget.value) || null)}
            required={field.required}
          >
            <option value="">— Выберите —</option>
            {options.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      );
    case 'multiselect':
      return (
        <div>
          <label>{field.label}:</label>
          {options.map(opt => (
            <label key={opt.value}>
              <input
                type="checkbox"
                checked={Array.isArray(value) && value.includes(opt.value)}
                onChange={e => {
                  const newVal = e.currentTarget.checked
                    ? [...(value || []), opt.value]
                    : (value || []).filter((v: number) => v !== opt.value);
                  onChange(newVal);
                }}
              />
              {opt.label}
            </label>
          ))}
        </div>
      );
    default:
      return <div>Неизвестное поле: {field.name}</div>;
  }
};