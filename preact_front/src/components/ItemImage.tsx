// src/components/ItemImage.tsx
import { h } from 'preact';
import { IMAGE_BASE_URL } from '../config/api';

interface ItemImageProps {
  image_id?: string | null;
  alt?: string;
  size?: 'small' | 'medium' | 'large';
}

export const ItemImage = ({ image_id, alt = 'Item', size = 'medium' }: ItemImageProps) => {
  if (!image_id) {
    return (
      <div style={{
        width: size === 'small' ? '60px' : size === 'medium' ? '120px' : '240px',
        height: size === 'small' ? '60px' : size === 'medium' ? '120px' : '240px',
        backgroundColor: '#f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#999',
        fontSize: '12px',
        borderRadius: '4px',
        border: '1px solid #ddd',
      }}>
        Нет изображения
      </div>
    );
  }

  const sizeClasses = {
    small: { width: 60, height: 60 },
    medium: { width: 120, height: 120 },
    large: { width: 240, height: 240 },
  };

  const { width, height } = sizeClasses[size];
  const imageUrl = `${IMAGE_BASE_URL}/mongodb/images/${image_id}`;

  return (
    <img
      src={imageUrl}
      alt={alt}
      loading="lazy"
      style={{
        width: `${width}px`,
        height: `${height}px`,
        objectFit: 'contain',
        borderRadius: '4px',
        border: '1px solid #ddd',
      }}
      onError={(e) => {
        (e.target as HTMLImageElement).style.display = 'none';
        // Можно показать placeholder, но для простоты — скрываем
      }}
    />
  );
};