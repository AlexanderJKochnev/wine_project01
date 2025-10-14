import React from 'react';
import GenericManager from './GenericManager';
import { apiService } from '../services/api';

const SubregionManager = () => {
  const subregionFields = [
    { name: 'name', label: 'Название субрегиона', required: true },
    { name: 'region_id', label: 'ID региона', type: 'number' },
    { name: 'description', label: 'Описание', multiline: true, rows: 3 }
  ];

  return (
    <GenericManager
      title="Субрегионы"
      apiService={apiService.subregions}
      fields={subregionFields}
      initialFormData={{ name: '', region_id: '', description: '' }}
      columns={['ID', 'Название', 'ID региона', 'Описание', 'Действия']}
    />
  );
};

export default SubregionManager;