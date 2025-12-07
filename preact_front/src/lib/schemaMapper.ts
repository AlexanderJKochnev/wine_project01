// src/lib/schemaMapper.ts
import { FieldConfig } from '../types/schema';
import { useApi } from '../hooks/useApi';

// Маппинг: имя поля → путь к /all эндпоинту
const FIELD_TO_ENDPOINT: Record<string, string> = {
  // Связи по ID
  category_id: '/categories/all',
  subcategory_id: '/subcategories/all',
  country_id: '/countries/all',
  region_id: '/regions/all',
  subregion_id: '/subregions/all',
  sweetness_id: '/sweetness/all',

  // Many-to-many списки
  foods: '/foods/all',
  varietals: '/varietals/all',
};

export const useSelectOptions = (fieldName: string) => {
  const endpoint = FIELD_TO_ENDPOINT[fieldName];
  if (!endpoint) {
    console.warn(`⚠️ No endpoint mapping for field: ${fieldName}`);
    return { options: [], loading: false, error: 'No endpoint' };
  }

  const { data, loading, error } = useApi<any[]>(endpoint);
  const options = data?.map(item => ({
    value: item.id,
    label: item.name || item.title || String(item.id),
  })) || [];
  return { options, loading, error };
};

// Схема для DrinkCreate
export const getDrinkCreateSchema = (): FieldConfig[] => [
  { name: 'title', label: 'Название', type: 'string', required: true },
  { name: 'subcategory_id', label: 'Подкатегория', type: 'select', required: true, optionsEndpoint: '/subcategories/all' },
  { name: 'subregion_id', label: 'Субрегион', type: 'select', required: true, optionsEndpoint: '/subregions/all' },
  { name: 'sweetness_id', label: 'Сладость', type: 'select', optionsEndpoint: '/sweetness/all' },
  { name: 'alc', label: 'Крепость (%)', type: 'number' },
  { name: 'sugar', label: 'Сахар (%)', type: 'number' },
  { name: 'age', label: 'Выдержка', type: 'string' },
  { name: 'sparkling', label: 'Игристое', type: 'boolean' },
  { name: 'foods', label: 'Еда (пайринг)', type: 'multiselect', optionsEndpoint: '/foods/all' },
  { name: 'varietals', label: 'Сорта винограда', type: 'multiselect', optionsEndpoint: '/varietals/all' },
];