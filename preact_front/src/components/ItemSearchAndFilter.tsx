// src/components/ItemSearchAndFilter.tsx
import { h } from 'preact';
import { useState, useEffect } from 'preact/hooks';
import { useApi } from '../hooks/useApi';

interface ItemSearchAndFilterProps {
  onSearch: (params: Record<string, any>) => void;
}

export const ItemSearchAndFilter = ({ onSearch }: ItemSearchAndFilterProps) => {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string | ''>('');
  const [country, setCountry] = useState<string | ''>('');

  // Загружаем категории и страны для фильтров
  const { data: categories } = useApi<any[]>(`/categories/all`);
  const { data: countries } = useApi<any[]>(`/countries/all`);

  useEffect(() => {
    const params: Record<string, any> = {};
    if (search) params.search = search;
    if (category) params.category = category;
    if (country) params.country = country;
    onSearch(params);
  }, [search, category, country]);

  return (
    <div style={{ marginBottom: '16px', padding: '12px', border: '1px solid #eee', borderRadius: '4px' }}>
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Поиск по названию..."
          value={search}
          onChange={e => setSearch(e.currentTarget.value)}
          style={{ padding: '6px', minWidth: '200px' }}
        />

        <select
          value={category}
          onChange={e => setCategory(e.currentTarget.value || '')}
          style={{ padding: '6px' }}
        >
          <option value="">Любая категория</option>
          {categories?.map(cat => (
            <option key={cat.id} value={cat.name}>
              {cat.name}
            </option>
          ))}
        </select>

        <select
          value={country}
          onChange={e => setCountry(e.currentTarget.value || '')}
          style={{ padding: '6px' }}
        >
          <option value="">Любая страна</option>
          {countries?.map(c => (
            <option key={c.id} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};