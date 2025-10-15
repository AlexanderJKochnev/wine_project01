// src/lib/schemaMapper.ts

import { FieldConfig } from '../types/schema';
import { useApi } from '../hooks/useApi';

// Вспомогательная функция: получить опции для select из /all
export const useSelectOptions = (endpoint: string) => {
  const { data, loading, error } = useApi<any[]>(endpoint);
  const options = data?.map(item => ({
    value: item.id,
    label: item.name || item.title || String(item.id),
  })) || [];
  return { options, loading, error };
};

// Схема для DrinkCreate (в Create-режиме)
export const getDrinkCreateSchema = (): FieldConfig[] => [
  { name: 'title', label: 'Название', type: 'string', required: true },
  { name: 'subcategory_id', label: 'Подкатегория', type: 'select', required: true },
  { name: 'subregion_id', label: 'Субрегион', type: 'select', required: true },
  { name: 'sweetness_id', label: 'Сладость', type: 'select', required: false },
  { name: 'alc', label: 'Крепость (%)', type: 'number' },
  { name: 'sugar', label: 'Сахар (%)', type: 'number' },
  { name: 'age', label: 'Выдержка', type: 'string' },
  { name: 'sparkling', label: 'Игристое', type: 'boolean' },
  { name: 'foods', label: 'Еда (пайринг)', type: 'multiselect' },
  { name: 'varietals', label: 'Сорта винограда', type: 'multiselect' },
];