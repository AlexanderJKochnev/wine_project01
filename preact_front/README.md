# `create-preact`

<h2 align="center">
  <img height="256" width="256" src="./src/assets/preact.svg">
</h2>

<h3 align="center">Get started using Preact and Vite!</h3>

## Getting Started

-   `npm run dev` - Starts a dev server at http://localhost:5173/

-   `npm run build` - Builds for production, emitting to `dist/`

-   `npm run preview` - Starts a server at http://localhost:4173/ to test production build locally

## Language Context

This project includes a Language Context for managing internationalization (i18n) with support for English and Russian languages.

### Features

- Automatic language detection based on browser language
- Persistent language preference using localStorage
- Comprehensive translation dictionary with common UI terms
- Easy-to-use translation function

### Usage

The Language Context provides:

1. `LanguageProvider` - Wraps your application to provide language context
2. `useLanguage` hook - Access language and translation functions in components
3. `t` function - Translate keys to the current language

Example usage in a component:

```tsx
import { useLanguage } from './contexts/LanguageContext';

const MyComponent = () => {
  const { t, language, setLanguage } = useLanguage();
  
  return (
    <div>
      <h1>{t('welcome')}</h1>
      <p>{t('description')}</p>
      <button onClick={() => setLanguage(language === 'en' ? 'ru' : 'en')}>
        {t('language')}: {language}
      </button>
    </div>
  );
};
```

### Supported Languages

- English ('en')
- Russian ('ru')

### Adding New Translations

To add new translations, extend the `translations` object in `LanguageContext.tsx` with new key-value pairs for both languages.
