// src/components/TestCategories.tsx
import { useApi } from '../hooks/useApi';
import { h } from 'preact';
import { useEffect } from 'preact/hooks'; // если используете useEffect
import { CategoryRead } from '../types/category';

export function TestCategories() {
  const { data, loading, error } = useApi<CategoryRead[]>('/categories/all');

  if (loading) return <p>Загрузка категорий...</p>;
  if (error) return <p>Ошибка: {error}</p>;

  return (
    <div>
      <h2>Категории ({data?.length})</h2>
      <ul>
        {data?.map((cat) => (
          <li key={cat.id}>
            {cat.name} {cat.name_ru && `(${cat.name_ru})`} {cat.name_fr && `(${cat.name_fr})`}
          </li>
        ))}
      </ul>
    </div>
  );
}