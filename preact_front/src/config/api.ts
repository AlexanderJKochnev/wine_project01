// src/config/api.ts

// Определяем базовый URL в зависимости от среды
export const API_BASE_URL = import.meta.env.DEV
  ? '/proxy-api' // будет проксироваться через Vite → http://app:8091
  : 'http://83.167.126.4:18091'; // внешний URL

export const IMAGE_BASE_URL = `${API_BASE_URL}`;