import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  IconButton,
  LinearProgress,
  Alert
} from '@mui/material';
import { Edit, Delete, Add, Search } from '@mui/icons-material';

const GenericManager = ({
  title,
  apiService,
  fields,
  initialFormData,
  columns = ['ID', 'Название', 'Действия']
}) => {
  const [items, setItems] = React.useState([]);
  const [openDialog, setOpenDialog] = React.useState(false);
  const [editingItem, setEditingItem] = React.useState(null);
  const [formData, setFormData] = React.useState(initialFormData);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [searchQuery, setSearchQuery] = React.useState('');

  const loadItems = async (search = '') => {
    try {
      setLoading(true);
      setError('');
      let response;
      if (search) {
        response = await apiService.search(search);
      } else {
        response = await apiService.getAll();
      }
      setItems(response.items || response || []);
    } catch (error) {
      console.error(`Error loading ${title}:`, error);
      setError(`Ошибка загрузки ${title}`);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadItems();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');
      if (editingItem) {
        await apiService.update(editingItem.id, formData);
      } else {
        await apiService.create(formData);
      }
      await loadItems();
      handleCloseDialog();
    } catch (error) {
      console.error(`Error saving ${title}:`, error);
      setError(`Ошибка сохранения ${title}`);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    // Автоматически заполняем форму данными элемента
    const filledFormData = { ...initialFormData };
    fields.forEach(field => {
      if (item[field.name] !== undefined) {
        filledFormData[field.name] = item[field.name];
      }
    });
    setFormData(filledFormData);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm(`Вы уверены, что хотите удалить этот ${title.toLowerCase()}?`)) {
      try {
        setError('');
        await apiService.delete(id);
        await loadItems();
      } catch (error) {
        console.error(`Error deleting ${title}:`, error);
        setError(`Ошибка удаления ${title}`);
      }
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setFormData(initialFormData);
    setError('');
  };

  const handleSearch = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (query.length === 0 || query.length >= 2) {
      loadItems(query);
    }
  };

  const renderTableRow = (item) => (
    <TableRow key={item.id}>
      <TableCell>{item.id}</TableCell>
      {fields.map(field => (
        <TableCell key={field.name}>
          {field.render ? field.render(item[field.name]) : item[field.name]}
        </TableCell>
      ))}
      <TableCell>
        <IconButton onClick={() => handleEdit(item)} color="primary">
          <Edit />
        </IconButton>
        <IconButton onClick={() => handleDelete(item.id)} color="error">
          <Delete />
        </IconButton>
      </TableCell>
    </TableRow>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
        <Typography variant="h4">{title}</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
        >
          Добавить
        </Button>
      </Box>

      {/* Поиск */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <TextField
            fullWidth
            variant="outlined"
            placeholder={`Поиск ${title.toLowerCase()}...`}
            value={searchQuery}
            onChange={handleSearch}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          {loading && <LinearProgress />}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  {columns.map(column => (
                    <TableCell key={column}>{column}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {items.map(renderTableRow)}
                {items.length === 0 && !loading && (
                  <TableRow>
                    <TableCell colSpan={columns.length} align="center">
                      Нет данных
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Диалог создания/редактирования */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? `Редактировать ${title.toLowerCase()}` : `Добавить ${title.toLowerCase()}`}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            {fields.map(field => (
              <TextField
                key={field.name}
                margin="dense"
                label={field.label}
                fullWidth
                variant="outlined"
                type={field.type || 'text'}
                multiline={field.multiline}
                rows={field.rows}
                required={field.required !== false}
                value={formData[field.name] || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  [field.name]: e.target.value
                })}
              />
            ))}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Отмена</Button>
            <Button type="submit" variant="contained">
              {editingItem ? 'Обновить' : 'Создать'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default GenericManager;