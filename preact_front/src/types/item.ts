// src/types/item.ts
import { BaseRead } from './base';

export interface LangFields {
  title?: string;
  subtitle?: string;
  description?: string;
  recommendation?: string;
  madeof?: string;
  alc?: string;    // "13%"
  sugar?: string;  // "5%"
  age?: string;
  sparkling?: boolean;
  pairing?: string[];
  varietal?: string[];
}

export interface ItemRead extends BaseRead {
  vol?: number;
  price?: number;
  count?: number;
  image_id?: string; // ← ID изображения в MongoDB
  category: string;
  country: string;
  en: LangFields;
  ru: LangFields;
  fr: LangFields;
}