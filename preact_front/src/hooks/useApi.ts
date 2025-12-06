// src/hooks/useApi.ts
import { useState, useEffect } from 'preact/hooks';
import { apiClient, getCurrentLanguage } from '../lib/apiClient';

type Method = 'GET' | 'POST' | 'PATCH' | 'DELETE';

// Вспомогательная функция для построения URL с query-параметрами
function buildUrl(endpoint: string, params?: Record<string, any>): string {
  if (!params) {
    // If no params, add lang as default
    const lang = getCurrentLanguage();
    return `${endpoint}?lang=${lang}`;
  }
  
  const url = new URL(endpoint, 'http://temp');
  Object.keys(params).forEach(key => {
    const value = params[key];
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, String(value));
    }
  });
  
  // Add language parameter if it's not already there
  if (!url.searchParams.has('lang')) {
    url.searchParams.append('lang', getCurrentLanguage());
  }
  
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
      console.log(`useApi making request to: ${url}`, { endpoint, method, params });
      const result = await apiClient<T>(url, { method, body }, false); // Don't include lang again since we built it into URL
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