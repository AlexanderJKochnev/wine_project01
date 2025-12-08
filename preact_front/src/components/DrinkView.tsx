// src/components/DrinkView.tsx
import { h } from 'preact';
import { useState } from 'preact/hooks';
import { useApi } from '../hooks/useApi';
import { deleteItem } from '../lib/apiClient';
import { PaginatedResponse } from '../types/base';
import { DrinkReadFlat } from '../types/drink';
import { LangExpandable } from './LangExpandable';
import { ConfirmDialog } from './ConfirmDialog';
import { EditDrinkForm } from './EditDrinkForm';
import { DrinkCard } from './DrinkCard'; // ← новый компонент
import { SearchAndFilter } from './SearchAndFilter';

interface DrinkViewProps {
  references: any;
  onEdit: (id: number) => void;
}

export const DrinkView = ({ references, onEdit }: DrinkViewProps) => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [confirmDelete, setConfirmDelete] = useState<{ id: number; name: string } | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table'); // ← новое состояние
  const pageSize = 12;

  const endpoint = filters.search ? '/drinks/search' : '/drinks';
  const params = { ...filters, page, page_size: pageSize };

  const { data, loading, error, refetch } = useApi<PaginatedResponse<DrinkReadFlat>>(
    endpoint,
    'GET',
    undefined,
    params
  );

  const handleDelete = async (id: number) => {
    const success = await deleteItem(`/drinks/${id}`);
    if (success) {
      refetch();
    }
    setConfirmDelete(null);
  };

  const handleSearch = (newFilters: Record<string, any>) => {
    setFilters(newFilters);
    setPage(1);
  };

  if (loading) return <p>Загрузка напитков...</p>;
  if (error) return <p>Ошибка: {error}</p>;

  return (
    <div>
      {/* Переключатель режима */}
      <div style={{ marginBottom: '16px', textAlign: 'right' }}>
        <button
          onClick={() => setViewMode('table')}
          style={{
            padding: '6px 12px',
            backgroundColor: viewMode === 'table' ? '#007bff' : 'white',
            color: viewMode === 'table' ? 'white' : '#000',
            border: '1px solid #ccc',
            borderRadius: '4px',
            marginRight: '8px'
          }}
        >
          Таблица
        </button>
        <button
          onClick={() => setViewMode('grid')}
          style={{
            padding: '6px 12px',
            backgroundColor: viewMode === 'grid' ? '#007bff' : 'white',
            color: viewMode === 'grid' ? 'white' : '#000',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
        >
          Плитки
        </button>
      </div>

      <SearchAndFilter onSearch={handleSearch} />

      {/* Отображение в зависимости от режима */}
      {viewMode === 'table' ? (
        <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Категория</th>
              <th>Страна</th>
              <th>Крепость</th>
              <th>Игристое</th>
              <th>Действия</th>
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
                <td>
                  <button
                    onClick={() => onEdit(drink.id)}
                    style={{ padding: '4px 8px', backgroundColor: '#007bff', color: 'white', border: 'none', marginRight: '8px' }}
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => setConfirmDelete({
                      id: drink.id,
                      name: drink.en?.title || 'Без названия'
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
      ) : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', marginTop: '16px' }}>
          {data?.items.map(drink => (
            <DrinkCard
              key={drink.id}
              drink={drink}
              onEdit={() => onEdit(drink.id)}
              onDelete={() => setConfirmDelete({
                id: drink.id,
                name: drink.en?.title || 'Без названия'
              })}
            />
          ))}
        </div>
      )}

      {/* Пагинация */}
      <div style={{ marginTop: '16px', textAlign: 'center', display: 'flex', justifyContent: 'center', gap: '8px' }}>
        <button onClick={() => setPage(1)} disabled={page <= 1}>Первая</button>
        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}>Назад</button>
        <span>Стр. {page} из {Math.ceil((data?.total || 0) / pageSize)}</span>
        <button onClick={() => setPage(p => p + 1)} disabled={!data?.has_next}>Вперёд</button>
        <button onClick={() => setPage(Math.ceil((data?.total || 0) / pageSize))} disabled={page >= Math.ceil((data?.total || 0) / pageSize)}>Последняя</button>
      </div>

      {/* Модальные окна */}
      {confirmDelete && (
        <ConfirmDialog
          open={true}
          title="Подтверждение удаления"
          message={`Вы уверены, что хотите удалить "${confirmDelete.name}"?`}
          onConfirm={() => handleDelete(confirmDelete.id)}
          onCancel={() => setConfirmDelete(null)}
        />
      )}

      {editingId && (
        <EditDrinkForm
          id={editingId}
          references={references}
          onClose={() => setEditingId(null)}
          onEdited={() => {
            refetch();
            setEditingId(null);
          }}
        />
      )}
    </div>
  );
};