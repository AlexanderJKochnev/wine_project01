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
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center">Вход</h2>
      {error && <p className="text-red-500 text-center">{error}</p>}
      <div>
        <input
          type="text"
          placeholder="Логин"
          value={username}
          onChange={e => setUsername(e.currentTarget.value)}
          required
          className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
      <div>
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={e => setPassword(e.currentTarget.value)}
          required
          className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
      <button 
        type="submit" 
        className="w-full btn btn-primary"
      >
        Войти
      </button>
    </form>
  );
};