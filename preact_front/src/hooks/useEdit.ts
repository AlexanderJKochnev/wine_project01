// src/hooks/useEdit.ts
import { useState } from 'preact/hooks';
import { apiClient } from '../lib/apiClient';

export const useEdit = (endpoint: string) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const editItem = async (data: Record<string, any>) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient(endpoint, {
        method: 'PATCH',
        body: data,
      });
      return result;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { editItem, loading, error };
};