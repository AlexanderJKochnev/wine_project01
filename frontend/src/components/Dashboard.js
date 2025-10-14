import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  LinearProgress
} from '@mui/material';
import { apiService } from '../services/api';

const StatCard = ({ title, value, color }) => (
  <Paper sx={{ p: 3, textAlign: 'center', bgcolor: color }}>
    <Typography variant="h4" fontWeight="bold">
      {value}
    </Typography>
    <Typography variant="h6" color="text.secondary">
      {title}
    </Typography>
  </Paper>
);

export default function Dashboard() {
  const [stats, setStats] = React.useState({
    categories: 0,
    countries: 0,
    regions: 0,
    subregions: 0
  });
  const [loading, setLoading] = React.useState(true);

  const loadStats = async () => {
    try {
      setLoading(true);
      const [categories, countries, regions, subregions] = await Promise.all([
        apiService.categories.getAll(),
        apiService.countries.getAll(),
        apiService.regions.getAll(),
        apiService.subregions.getAll()
      ]);

      setStats({
        categories: categories.items?.length || 0,
        countries: countries.items?.length || 0,
        regions: regions.items?.length || 0,
        subregions: subregions.items?.length || 0
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadStats();
  }, []);

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Обзор коллекции
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Категории"
            value={stats.categories}
            color="#e3f2fd"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Страны"
            value={stats.countries}
            color="#f3e5f5"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Регионы"
            value={stats.regions}
            color="#e8f5e8"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Субрегионы"
            value={stats.subregions}
            color="#fff3e0"
          />
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Быстрые действия
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Используйте вкладки выше для управления различными сущностями винной коллекции.
            Каждая сущность поддерживает полный CRUD функционал.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}