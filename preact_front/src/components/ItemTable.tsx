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

      <table className="table table-zebra">
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
                  className="btn btn-primary btn-sm mr-2"
                >
                  Редактировать
                </button>
                <button
                  onClick={() => setConfirmDelete({
                    id: item.id,
                    name: item.en?.title || 'Без названия'
                  })}
                  className="btn btn-error btn-sm"
                >
                  Удалить
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-4 text-center flex justify-center gap-2">
          <button
            onClick={() => setPage(1)}
            disabled={page <= 1}
            className="btn btn-outline"
          >
            Первая
          </button>
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="btn btn-outline"
          >
            Назад
          </button>
          <span className="m-0 p-3 self-center">
            Страница {page} из {Math.ceil((data?.total || 0) / pageSize)}
          </span>
          <button
            onClick={() => setPage(p => {
              const last = Math.ceil((data?.total || 0) / pageSize);
              return Math.min(last, p + 1);
            })}
            disabled={!data?.has_next}
            className="btn btn-outline"
          >
            Вперёд
          </button>
          <button
            onClick={() => setPage(Math.ceil((data?.total || 0) / pageSize))}
            disabled={page >= Math.ceil((data?.total || 0) / pageSize)}
            className="btn btn-outline"
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