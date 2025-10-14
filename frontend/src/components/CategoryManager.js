import React from 'react';
import GenericManager from './GenericManager';
import { apiService } from '../services/api';

const CategoryManager = () => {
  const categoryFields = [
    { name: 'name', label: 'Название категории', required: true },
    { name: 'description', label: 'Описание', multiline: true, rows: 3 }
  ];

  return (
    <GenericManager
      title="Категории"
      apiService={apiService.categories}
      fields={categoryFields}
      initialFormData={{ name: '', description: '' }}
      columns={['ID', 'Название', 'Описание', 'Действия']}
    />
  );
};

export default CategoryManager;