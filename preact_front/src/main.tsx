// src/main.tsx
import { render } from 'preact';
import { App } from './App';
import './style.css'; // Подключаем стили

render(<App />, document.getElementById('app')!);
