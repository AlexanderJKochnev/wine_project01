// src/hooks/useNotification.ts
import { useState, useEffect } from 'preact/hooks';

interface Notification {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

export const useNotification = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  return { notifications, showNotification };
};