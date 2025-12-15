// src/pages/ItemCreatePage.tsx
import { h } from 'preact';
import { route } from 'preact-iso';
import { ItemCreateForm } from '../components/ItemCreateForm';

export const ItemCreatePage = () => {
  const handleClose = () => {
    route('/items', true); // Navigate back to items list
  };

  const handleCreated = () => {
    // Optionally show success notification
    route('/items', true); // Navigate back to items list after creation
  };

  return (
    <ItemCreateForm onClose={handleClose} onCreated={handleCreated} />
  );
};