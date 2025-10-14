// Для разработки внутри Docker
const API_BASE = 'http://app:8091/api';

// Или для доступа с хоста
// const API_BASE = 'http://localhost:8091/api';;

// Базовые CRUD операции
export const apiService = {
  // Категории
  categories: {
    getAll: () => fetch(`${API_BASE}/categories`).then(r => r.json()),
    getOne: (id) => fetch(`${API_BASE}/categories/${id}`).then(r => r.json()),
    create: (data) => fetch(`${API_BASE}/categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    update: (id, data) => fetch(`${API_BASE}/categories/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    delete: (id) => fetch(`${API_BASE}/categories/${id}`, {
      method: 'DELETE'
    }).then(r => r.json()),
    search: (query) => fetch(`${API_BASE}/categories/search?search=${query}`).then(r => r.json())
  },

  // Страны
  countries: {
    getAll: () => fetch(`${API_BASE}/countries`).then(r => r.json()),
    getOne: (id) => fetch(`${API_BASE}/countries/${id}`).then(r => r.json()),
    create: (data) => fetch(`${API_BASE}/countries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    update: (id, data) => fetch(`${API_BASE}/countries/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    search: (query) => fetch(`${API_BASE}/countries/search?search=${query}`).then(r => r.json())
  },

  // Регионы
  regions: {
    getAll: () => fetch(`${API_BASE}/regions`).then(r => r.json()),
    getOne: (id) => fetch(`${API_BASE}/regions/${id}`).then(r => r.json()),
    create: (data) => fetch(`${API_BASE}/regions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    update: (id, data) => fetch(`${API_BASE}/regions/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    search: (query) => fetch(`${API_BASE}/regions/search?search=${query}`).then(r => r.json())
  },

  // Субрегионы
  subregions: {
    getAll: () => fetch(`${API_BASE}/subregions`).then(r => r.json()),
    getOne: (id) => fetch(`${API_BASE}/subregions/${id}`).then(r => r.json()),
    create: (data) => fetch(`${API_BASE}/subregions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    update: (id, data) => fetch(`${API_BASE}/subregions/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    search: (query) => fetch(`${API_BASE}/subregions/search?search=${query}`).then(r => r.json())
  }
};