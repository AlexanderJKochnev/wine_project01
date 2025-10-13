import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Card,
  CardContent,
  Button,
  Grid,
  Paper,
  Box
} from '@mui/material';

// Основной компонент приложения
function WineApp() {
  const [stats, setStats] = React.useState({ wines: 0, images: 0 });
  const [wines, setWines] = React.useState([]);

  // Загружаем статистику с бэкенда
  const loadStats = async () => {
    try {
      // Замени на реальные эндпоинты твоего FastAPI
      const response = await fetch('http://localhost:8000/api/statistics');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.log('Используем демо-данные');
      setStats({ wines: 42, images: 156 }); // Демо-данные
    }
  };

  // Загружаем список вин
  const loadWines = async () => {
    try {
      const response = await fetch('http://localhost:8000/api');
      const data = await response.json();
      setWines(data);
    } catch (error) {
      console.log('Используем демо-вина');
      setWines([
        { id: 1, name: 'Cabernet Sauvignon', type: 'red', year: 2018, region: 'Бордо' },
        { id: 2, name: 'Chardonnay', type: 'white', year: 2020, region: 'Бургундия' }
      ]);
    }
  };

  React.useEffect(() => {
    loadStats();
    loadWines();
  }, []);

  return (
    <div>
      {/* Шапка */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🍷 Wine Collection Manager
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Основной контент */}
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {/* Статистика */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e3f2fd' }}>
              <Typography variant="h4" color="primary">
                {stats.wines}
              </Typography>
              <Typography variant="body1">Всего вин</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#f3e5f5' }}>
              <Typography variant="h4" color="secondary">
                {stats.images}
              </Typography>
              <Typography variant="body1">Изображений</Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Управление винами */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Управление винами
            </Typography>
            <Button variant="contained" sx={{ mr: 2 }}>
              Добавить вино
            </Button>
            <Button variant="outlined">
              Загрузить изображение
            </Button>
          </CardContent>
        </Card>

        {/* Список вин */}
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Коллекция вин ({wines.length})
            </Typography>
            {wines.map(wine => (
              <Box key={wine.id} sx={{
                p: 2,
                mb: 1,
                border: '1px solid',
                borderColor: 'grey.300',
                borderRadius: 1
              }}>
                <Typography variant="h6">{wine.name}</Typography>
                <Typography variant="body2">
                  Тип: {wine.type} | Год: {wine.year} | Регион: {wine.region}
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Container>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<WineApp />);