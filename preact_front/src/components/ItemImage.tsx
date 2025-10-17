// src/components/ItemImage.tsx
import { h } from 'preact';
import { API_BASE_URL } from '../config/api'; // ← базовый URL FastAPI

interface ItemImageProps {
  image_id?: string | null;
  alt?: string;
  size?: 'small' | 'medium' | 'large';
}

export const ItemImage = ({ image_id, alt = 'Item', size = 'medium' }: ItemImageProps) => {
  if (!image_id) return null;

  const sizeClasses = {
    small: { width: 60, height: 60 },
    medium: { width: 120, height: 120 },
    large: { width: 240, height: 240 },
  };

  const { width, height } = sizeClasses[size];

  // Формируем URL: /mongodb/images/{image_id}
  const imageUrl = `${API_BASE_URL}/mongodb/images/${image_id}`;

  return (
    <img
      src={imageUrl}
      alt={alt}
      loading="lazy" // ← lazy loading
      style={{
        width: `${width}px`,
        height: `${height}px`,
        objectFit: 'cover',
        borderRadius: '4px',
        border: '1px solid #ddd',
      }}
      onError={(e) => {
        console.error('Image load error:', imageUrl);
        (e.target as HTMLImageElement).style.display = 'none';
      }}
    />
  );
};