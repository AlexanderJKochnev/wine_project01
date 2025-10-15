// src/types/schema.ts

export type FieldType =
  | 'string'
  | 'number'
  | 'boolean'
  | 'select'        // одиночный выбор по ID
  | 'multiselect'   // массив ID
  | 'image';

export interface FieldConfig {
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  options?: { value: number; label: string }[]; // для select/multiselect
  path?: string; // путь к вложенному полю (например, 'subcategory.name')
}