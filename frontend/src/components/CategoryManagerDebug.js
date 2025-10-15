import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Box
} from '@mui/material';
import { apiService } from '../services/api';

const CategoryManagerDebug = () => {
  const [categories, setCategories] = React.useState([]);
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(false);

  const loadCategories = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('🔄 Загрузка категорий...');
      const data = await apiService.categories.getAll();
      console.log('📦 Получены данные:', data);
      setCategories(data.items || data);
    } catch (err) {
      console.error('❌ Ошибка загрузки:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadCategories();
  }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          🐛 Отладка CategoryManager
        </Typography>

        <Button
          variant="outlined"
          onClick={loadCategories}
          disabled={loading}
          sx={{ mb: 2 }}
        >
          {loading ? 'Загрузка...' : 'Перезагрузить категории'}
        </Button>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            ❌ Ошибка: {error}
          </Alert>
        )}

        <Typography variant="h6">Статус:</Typography>
        <Alert severity={error ? 'error' : categories.length > 0 ? 'success' : 'info'}>
          {error ? 'Ошибка загрузки' :
           categories.length > 0 ? `Загружено категорий: ${categories.length}` : 'Нет данных'}
        </Alert>

        {categories.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6">Первая категория (пример):</Typography>
            <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '4px' }}>
              {JSON.stringify(categories[0], null, 2)}
            </pre>
          </Box>
        )}

        <Box sx={{ mt: 2 }}>
          <Typography variant="h6">Все данные:</Typography>
          <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '4px', maxHeight: '300px', overflow: 'auto' }}>
            {JSON.stringify(categories, null, 2)}
          </pre>
        </Box>
      </CardContent>
    </Card>
  );
};

export default CategoryManagerDebug;