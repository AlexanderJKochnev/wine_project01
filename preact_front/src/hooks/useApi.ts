// src/hooks/useApi.ts
import { useState, useEffect } from 'preact/hooks';
import { apiClient } from '../lib/apiClient';

type Method = 'GET' | 'POST' | 'PATCH' | 'DELETE';

// Вспомогательная функция для построения URL с query-параметрами
function buildUrl(endpoint: string, params?: Record<string, any>): string {
  if (!params) return endpoint;
  const url = new URL(endpoint, 'http://temp');
  Object.keys(params).forEach(key => {
    const value = params[key];
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, String(value));
    }
  });
  return url.pathname + url.search;
}

export function useApi<T>(
  endpoint: string,
  method: Method = 'GET',
  body?: any,
  params?: Record<string, any>, // ← добавлено
  autoFetch: boolean = true
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const url = buildUrl(endpoint, params);
      const result = await apiClient<T>(url, { method, body });
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (autoFetch && method === 'GET') {
      fetchData();
    }
  }, [endpoint, JSON.stringify(params)]); // ← зависимость от params

  return { data, loading, error, refetch: fetchData };
}