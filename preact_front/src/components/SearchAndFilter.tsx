// src/components/SearchAndFilter.tsx
import { h } from 'preact';
import { useState } from 'preact/hooks';

interface SearchAndFilterProps {
  onSearch: (params: Record<string, any>) => void;
}

export const SearchAndFilter = ({ onSearch }: SearchAndFilterProps) => {
  const [search, setSearch] = useState('');

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    const params: Record<string, any> = {};
    if (search.trim()) {
      params.search = search.trim();
    }
    onSearch(params);
  };

  return (
    <div style={{ marginBottom: '24px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="🔍 Поиск по названию, описанию..."
          value={search}
          onChange={e => setSearch(e.currentTarget.value)}
          style={{
            padding: '10px 14px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            fontSize: '14px',
            minWidth: '250px',
            flex: 1,
          }}
        />
        <button
          type="submit"
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Найти
        </button>
      </form>
    </div>
  );
};