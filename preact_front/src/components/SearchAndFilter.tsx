// src/components/SearchAndFilter.tsx
import { h } from 'preact';
import { useState } from 'preact/hooks';

interface SearchAndFilterProps {
  onSearch: (params: Record<string, any>) => void;
}

export const SearchAndFilter = ({ onSearch }: SearchAndFilterProps) => {
  const [search, setSearch] = useState('');

  const handleSubmit = (e: Event) => {
    e.preventDefault(); // ← предотвращает перезагрузку!
    const params: Record<string, any> = {};
    if (search.trim()) {
      params.search = search.trim();
    }
    onSearch(params);
  };

  return (
    <div style={{ marginBottom: '16px', padding: '12px', border: '1px solid #eee', borderRadius: '4px' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Поиск по названию, описанию..."
          value={search}
          onChange={e => setSearch(e.currentTarget.value)}
          style={{ padding: '6px', minWidth: '200px' }}
        />
        <button type="submit" style={{ padding: '6px 12px' }}>
          Поиск
        </button>
      </form>
    </div>
  );
};