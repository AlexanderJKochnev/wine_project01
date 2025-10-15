import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import { apiService } from '../services/api';

const DebugConnection = () => {
  const [results, setResults] = React.useState({});
  const [loading, setLoading] = React.useState(false);

  const testAllEndpoints = async () => {
    setLoading(true);
    const testResults = {};

    try {
      // Тест 1: Базовое соединение
      const baseTest = await fetch('http://localhost:8091/api/categories');
      testResults.connection = {
        status: baseTest.status,
        ok: baseTest.ok,
        headers: Object.fromEntries(baseTest.headers.entries())
      };
    } catch (error) {
      testResults.connection = { error: error.message };
    }

    // Тест 2: Все эндпоинты
    const endpoints = [
      { name: 'categories', method: apiService.categories.getAll },
      { name: 'countries', method: apiService.countries.getAll },
      { name: 'regions', method: apiService.regions.getAll },
      { name: 'subregions', method: apiService.subregions.getAll }
    ];

    for (const endpoint of endpoints) {
      try {
        const data = await endpoint.method();
        testResults[endpoint.name] = {
          success: true,
          count: data.items?.length || data.length || 0,
          sample: data.items?.[0] || data[0] || null
        };
      } catch (error) {
        testResults[endpoint.name] = {
          success: false,
          error: error.message,
          fullError: error
        };
      }
    }

    setResults(testResults);
    setLoading(false);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          🔧 Диагностика соединения с FastAPI
        </Typography>

        <Button
          variant="contained"
          onClick={testAllEndpoints}
          disabled={loading}
          sx={{ mb: 3 }}
        >
          {loading ? 'Тестируем...' : 'Запустить диагностику'}
        </Button>

        {results.connection && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6">Соединение с FastAPI:</Typography>
            {results.connection.error ? (
              <Alert severity="error">
                ❌ Ошибка: {results.connection.error}
              </Alert>
            ) : (
              <Alert severity={results.connection.ok ? 'success' : 'warning'}>
                {results.connection.ok ? '✅ Соединение установлено' : '⚠ Проблемы с соединением'}
                <br />
                Status: {results.connection.status}
              </Alert>
            )}
          </Box>
        )}

        <Typography variant="h6" gutterBottom>Результаты по эндпоинтам:</Typography>
        <List>
          {Object.keys(results).filter(key => key !== 'connection').map(endpoint => (
            <ListItem key={endpoint} divider>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1" fontWeight="bold">
                      /api/{endpoint}
                    </Typography>
                    <Chip
                      label={results[endpoint].success ? '✅ Успех' : '❌ Ошибка'}
                      color={results[endpoint].success ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  results[endpoint].success ? (
                    `Данных: ${results[endpoint].count} | Пример: ${JSON.stringify(results[endpoint].sample)}`
                  ) : (
                    `Ошибка: ${results[endpoint].error}`
                  )
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default DebugConnection;