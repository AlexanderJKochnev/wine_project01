import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Tabs,
  Tab,
  Box,
  CssBaseline,
  Button,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// Импортируем только РАБОЧАЮЩИЙ компонент
import CategoryManager from './components/CategoryManager';

const theme = createTheme({
  palette: {
    primary: {
      main: '#8B0000',
    },
    secondary: {
      main: '#4CAF50',
    },
  },
});

function TabPanel({ children, value, index, ...other }) {
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// Простой компонент для отображения роутов
function RoutesList() {
  const routes = [
    { path: '/categories', name: 'Категории', component: 'CategoryManager' },
    { path: '/countries', name: 'Страны', component: 'CountryManager' },
    { path: '/regions', name: 'Регионы', component: 'RegionManager' },
    { path: '/subregions', name: 'Субрегионы', component: 'SubregionManager' }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Доступные роуты
      </Typography>
      <Grid container spacing={2}>
        {routes.map((route) => (
          <Grid item xs={12} sm={6} md={3} key={route.path}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {route.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Компонент: {route.component}
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => window.location.href = route.path}
                >
                  Перейти
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

function App() {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🍷 Wine Collection Manager
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="📊 Все роуты" />
            <Tab label="📁 Категории" />
            {/* Временно закомментировал проблемные вкладки */}
            {/* <Tab label="🌍 Страны" /> */}
            {/* <Tab label="🗺️ Регионы" /> */}
            {/* <Tab label="📍 Субрегионы" /> */}
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <RoutesList />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <CategoryManager />
        </TabPanel>
        {/* Временно закомментировал проблемные табпанели */}
        {/* <TabPanel value={tabValue} index={2}>
          <CountryManager />
        </TabPanel>
        <TabPanel value={tabValue} index={3}>
          <RegionManager />
        </TabPanel>
        <TabPanel value={tabValue} index={4}>
          <SubregionManager />
        </TabPanel> */}
      </Container>
    </ThemeProvider>
  );
}

export default App;