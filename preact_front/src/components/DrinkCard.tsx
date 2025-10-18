// src/components/DrinkCard.tsx
import { h } from 'preact';
import { DrinkReadFlat } from '../types/drink';
import { LangExpandable } from './LangExpandable';

interface DrinkCardProps {
  drink: DrinkReadFlat;
  onEdit: () => void;
  onDelete: () => void;
}

export const DrinkCard = ({ drink, onEdit, onDelete }: DrinkCardProps) => {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '16px',
      width: '280px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }}>
      <div>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem' }}>
          <LangExpandable en={drink.en} ru={drink.ru} fr={drink.fr} field="title" label="Название" />
        </h3>
        <p style={{ margin: '0', color: '#555', fontSize: '0.9rem' }}>
          <strong>Категория:</strong> {drink.category || '—'}<br />
          <strong>Страна:</strong> {drink.country || '—'}<br />
          <strong>Крепость:</strong> {drink.en?.alc || '—'}
        </p>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
        <button
          onClick={onEdit}
          style={{
            padding: '6px 12px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }}
        >
          Редактировать
        </button>
        <button
          onClick={onDelete}
          style={{
            padding: '6px 12px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }}
        >
          Удалить
        </button>
      </div>
    </div>
  );
};