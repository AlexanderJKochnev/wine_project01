// src/components/ConfirmDialog.tsx
import { h } from 'preact';

interface ConfirmDialogProps {
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog = ({ title, message, onConfirm, onCancel }: ConfirmDialogProps) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 2000,
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        maxWidth: '400px',
        width: '90%',
      }}>
        <h3>{title}</h3>
        <p>{message}</p>
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '16px' }}>
          <button onClick={onCancel} style={{ padding: '6px 12px' }}>
            Отмена
          </button>
          <button
            onClick={onConfirm}
            style={{ padding: '6px 12px', backgroundColor: '#dc3545', color: 'white', border: 'none' }}
          >
            Удалить
          </button>
        </div>
      </div>
    </div>
  );
};