// src/components/DrinkTable.tsx
import { h } from 'preact';
import { useState } from 'preact/hooks';
import { useApi } from '../hooks/useApi';
import { PaginatedResponse } from '../types/base';
import { DrinkReadFlat } from '../types/drink';
import { LangExpandable } from './LangExpandable';
import { SearchAndFilter } from './SearchAndFilter';

export const DrinkTable = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Record<string, any>>({});
  const pageSize = 20;

  const endpoint = filters.search ? '/drinks/search' : '/drinks';
  const params = { ...filters, page, page_size: pageSize };

  const { data, loading, error } = useApi<PaginatedResponse<DrinkReadFlat>>(
    endpoint,
    'GET',
    undefined,
    params
  );

  if (loading) return <p>Загрузка напитков...</p>;
  if (error) return <p>Ошибка: {error}</p>;

  return (
    <div>
      <SearchAndFilter onSearch={setFilters} />

      <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Категория</th>
            <th>Страна</th>
            <th>Крепость</th>
            <th>Игристое</th>
          </tr>
        </thead>
        <tbody>
          {data?.items.map(drink => (
            <tr key={drink.id}>
              <td>{drink.id}</td>
              <td>
                <LangExpandable
                  en={drink.en}
                  ru={drink.ru}
                  fr={drink.fr}
                  field="title"
                  label="Название"
                />
              </td>
              <td>{drink.category || '—'}</td>
              <td>{drink.country || '—'}</td>
              <td>{drink.en?.alc || '—'}</td>
              <td>{drink.sparkling ? '✅' : '❌'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: '16px', textAlign: 'center' }}>
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page <= 1}
        >
          Назад
        </button>
        <span style={{ margin: '0 16px' }}>
          Страница {page} из {Math.ceil((data?.total || 0) / pageSize)}
        </span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={!data?.has_next}
        >
          Вперёд
        </button>
      </div>
    </div>
  );
};