// src/components/DrinkTable.tsx
import { h } from 'preact'; // ← h из 'preact'
import { useEffect, useState } from 'preact/hooks'; // ← useState из 'preact/hooks'
import { apiClient } from '../lib/apiClient';
import { DrinkReadFlat } from '../types/drink';

export const DrinkTable = () => {
  const [drinks, setDrinks] = useState<DrinkReadFlat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDrinks = async () => {
      try {
        const data = await apiClient<DrinkReadFlat[]>('/drinks/all');
        setDrinks(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDrinks();
  }, []);

  if (loading) return <p>Загрузка напитков...</p>;
  if (error) return <p>Ошибка: {error}</p>;

  return (
    <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          <th>ID</th>
          <th>Название</th>
          <th>Подкатегория</th>
          <th>Регион</th>
          <th>Крепость</th>
          <th>Игристое</th>
        </tr>
      </thead>
      <tbody>
        {drinks.map(drink => (
          <tr key={drink.id}>
            <td>{drink.id}</td>
            <td>{drink.title}</td>
            <td>{drink.subcategory?.name || '—'}</td>
            <td>{drink.subregion?.region?.country?.name}, {drink.subregion?.name}</td>
            <td>{drink.alc}%</td>
            <td>{drink.sparkling ? '✅' : '❌'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};