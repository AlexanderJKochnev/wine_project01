import { createContext, useState, useContext, ReactNode } from 'preact/compat';
import { useEffect } from 'preact/hooks';

// Define the supported languages
export type Language = 'en' | 'ru';

// Define the context type
interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

// Create the context with default values
const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
});

// Translation dictionary
const translations = {
  en: {
    // Add English translations here
  },
  ru: {
    // Add Russian translations here
  }
};

// Provider component
export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [language, setLanguage] = useState<Language>(() => {
    // Check for saved language preference in localStorage
    const savedLang = localStorage.getItem('language') as Language;
    if (savedLang && ['en', 'ru'].includes(savedLang)) {
      return savedLang;
    }
    
    // Fallback to browser language or default to 'en'
    const browserLang = navigator.language.startsWith('ru') ? 'ru' : 'en';
    return browserLang as Language;
  });

  // Save language preference to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  // Translation function
  const t = (key: string): string => {
    const translation = translations[language][key];
    return translation || key; // Return the key itself if no translation found
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Custom hook to use the language context
export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};