// src/hooks/useApi.ts
import { useState, useEffect } from 'preact/hooks';
import { apiClient } from '../lib/apiClient';

type Method = 'GET' | 'POST' | 'PATCH' | 'DELETE';

export function useApi<T>(
  endpoint: string,
  method: Method = 'GET',
  body?: any,
  autoFetch: boolean = true
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient<T>(endpoint, { method, body });
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Автоматическая загрузка при монтировании (для GET)
  useEffect(() => {
    if (autoFetch && method === 'GET') {
      fetchData();
    }
  }, [endpoint]);

  return { data, loading, error, refetch: fetchData };
}