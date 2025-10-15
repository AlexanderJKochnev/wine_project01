// src/types/subcategory.ts
import { ReadSchema, CreateSchema, UpdateSchema } from './base';
import { CategoryRead } from './category';

// Для Create с вложенной моделью — передаём объект
export interface SubcategoryCreateRelation extends CreateSchema {
  category: CategoryCreate;
}

// Для Create с ID — упрощённый вариант (альтернатива)
export interface SubcategoryCreate extends CreateSchema {
  category_id: number;
}

// Для Read — вложенная модель целиком
export interface SubcategoryRead extends ReadSchema {
  category: CategoryRead;
}

// Для Update — опционально
export interface SubcategoryUpdate extends UpdateSchema {
  category?: CategoryCreate;
  category_id?: number;
}