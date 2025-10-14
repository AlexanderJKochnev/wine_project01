import React from 'react';
import GenericManager from './GenericManager';
import { apiService } from '../services/api';

const RegionManager = () => {
  const regionFields = [
    { name: 'name', label: 'Название региона', required: true },
    { name: 'country_id', label: 'ID страны', type: 'number' },
    { name: 'description', label: 'Описание', multiline: true, rows: 3 }
  ];

  return (
    <GenericManager
      title="Регионы"
      apiService={apiService.regions}
      fields={regionFields}
      initialFormData={{ name: '', country_id: '', description: '' }}
      columns={['ID', 'Название', 'ID страны', 'Описание', 'Действия']}
    />
  );
};

export default RegionManager;