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
      <h2 className="text-2xl font-bold text-center mb-4">Вход</h2>
      {error && <div className="alert alert-error mb-4"><p className="text-center">{error}</p></div>}
      <div className="form-control">
        <input
          type="text"
          placeholder="Логин"
          value={username}
          onChange={e => setUsername(e.currentTarget.value)}
          required
          className="input input-bordered w-full"
        />
      </div>
      <div className="form-control">
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={e => setPassword(e.currentTarget.value)}
          required
          className="input input-bordered w-full"
        />
      </div>
      <button 
        type="submit" 
        className="btn btn-primary w-full mt-4"
      >
        Войти
      </button>
    </form>
  );
};