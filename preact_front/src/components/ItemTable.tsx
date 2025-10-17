// src/components/ItemTable.tsx
import { h } from 'preact';
import { useState } from 'preact/hooks';
import { useApi } from '../hooks/useApi';
import { deleteItem } from '../lib/apiClient';
import { PaginatedResponse } from '../types/base';
import { ItemRead } from '../types/item';
import { ItemImage } from './ItemImage';
import { LangExpandable } from './LangExpandable';
import { SearchAndFilter } from './SearchAndFilter';
import { ConfirmDialog } from './ConfirmDialog';
import { EditItemForm } from './EditItemForm';

export const ItemTable = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [confirmDelete, setConfirmDelete] = useState<{ id: number; name: string } | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const pageSize = 5;

  const endpoint = filters.search ? '/items/search' : '/items';
  const params = { ...filters, page, page_size: pageSize };

  const { data, loading, error, refetch } = useApi<PaginatedResponse<ItemRead>>(
    endpoint,
    'GET',
    undefined,
    params
  );

  const handleDelete = async (id: number) => {
    const success = await deleteItem(`/items/${id}`);
    if (success) {
      refetch();
    }
    setConfirmDelete(null);
  };

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
            <th>Действия</th>
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
              <td>{item.vol ? `${item.vol} мл` : '—'}</td>
              <td>{item.country || '—'}</td>
              <td>
                <button
                  onClick={() => setEditingId(item.id)}
                  style={{ padding: '4px 8px', backgroundColor: '#007bff', color: 'white', border: 'none', marginRight: '8px' }}
                >
                  Редактировать
                </button>
                <button
                  onClick={() => setConfirmDelete({
                    id: item.id,
                    name: item.en?.title || 'Без названия'
                  })}
                  style={{ padding: '4px 8px', backgroundColor: '#dc3545', color: 'white', border: 'none' }}
                >
                  Удалить
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: '16px', textAlign: 'center', display: 'flex', justifyContent: 'center', gap: '8px' }}>
          <button
            onClick={() => setPage(1)}
            disabled={page <= 1}
            style={{ padding: '6px 12px' }}
          >
            Первая
          </button>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page <= 1}
            style={{ padding: '6px 12px' }}
          >
            Назад
          </button>
          <span style={{ margin: '0 16px', alignSelf: 'center' }}>
            Страница {page} из {Math.ceil((data?.total || 0) / pageSize)}
          </span>
          <button
            onClick={() => setPage(p => {
              const last = Math.ceil((data?.total || 0) / pageSize);
              return Math.min(last, p + 1);
            })}
            disabled={!data?.has_next}
            style={{ padding: '6px 12px' }}
          >
            Вперёд
          </button>
          <button
            onClick={() => setPage(Math.ceil((data?.total || 0) / pageSize))}
            disabled={page >= Math.ceil((data?.total || 0) / pageSize)}
            style={{ padding: '6px 12px' }}
          >
            Последняя
          </button>
      </div>

      {confirmDelete && (
        <ConfirmDialog
          title="Подтверждение удаления"
          message={`Вы уверены, что хотите удалить "${confirmDelete.name}"?`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}

      {editingId && (
        <EditItemForm
          id={editingId}
          onClose={() => setEditingId(null)}
          onEdited={refetch}
        />
      )}
    </div>
  );
};