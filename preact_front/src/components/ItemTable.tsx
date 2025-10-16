// src/components/ItemTable.tsx
import { h } from 'preact';
import { useState } from 'preact/hooks';
import { useApi } from '../hooks/useApi';
import { PaginatedResponse } from '../types/base';
import { ItemRead } from '../types/item';
import { ItemImage } from './ItemImage';
import { LangExpandable } from './LangExpandable';
import { SearchAndFilter } from './SearchAndFilter';

export const ItemTable = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Record<string, any>>({});
  const pageSize = 20;

  const endpoint = filters.search ? '/items/search' : '/items';
  const params = { ...filters, page, page_size: pageSize };

  const { data, loading, error } = useApi<PaginatedResponse<ItemRead>>(
    endpoint,
    'GET',
    undefined,
    params
  );

  if (loading) return <p>Загрузка позиций...</p>;
  if (error) return <p>Ошибка: {error}</p>;

  return (
    <div>
      <SearchAndFilter onSearch={setFilters} />

      <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>Изображение</th>
            <th>Название</th>
            <th>Объём</th>
            <th>Страна</th>
          </tr>
        </thead>
        <tbody>
          {data?.items.map(item => (
            <tr key={item.id}>
              <td><ItemImage image_id={item.image_id} size="small" /></td>
              <td>
                <LangExpandable
                  en={item.en}
                  ru={item.ru}
                  fr={item.fr}
                  field="title"
                  label="Название"
                />
              </td>
              <td>{item.vol} мл</td>
              <td>{item.country || '—'}</td>
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