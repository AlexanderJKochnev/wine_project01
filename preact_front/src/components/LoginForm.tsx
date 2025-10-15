// src/components/LoginForm.tsx
import { h } from 'preact'; // ← h из 'preact'
import { useState } from 'preact/hooks'; // ← useState из 'preact/hooks'
import { apiClient, setAuthToken } from '../lib/apiClient';

export const LoginForm = ({ onLogin }: { onLogin: () => void }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('grant_type', 'password'); // ← обязательно

    try {
      const response = await fetch('/proxy-api/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Неверный логин или пароль');
      }

      const data = await response.json();
      setAuthToken(data.access_token);
      onLogin();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Вход</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <input
        type="text"
        placeholder="Логин"
        value={username}
        onChange={e => setUsername(e.currentTarget.value)}
        required
      />
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={e => setPassword(e.currentTarget.value)}
        required
      />
      <button type="submit">Войти</button>
    </form>
  );
};