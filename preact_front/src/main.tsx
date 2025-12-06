// src/main.tsx
import { render } from 'preact';
import { LocationProvider } from 'preact-iso';
import { App } from './App';
import { LanguageProvider } from './contexts/LanguageContext';
import './style.css'; // Подключаем стили

//render(<App />, document.getElementById('app')!);
render(
  <LanguageProvider>
    <LocationProvider>
      <App />
    </LocationProvider>
  </LanguageProvider>,
  document.getElementById('app')!
);