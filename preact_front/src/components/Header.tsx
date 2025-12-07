// src/components/Header.tsx
import { h, useState } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { Link } from './Link';
import { useLanguage } from '../contexts/LanguageContext';

export const Header = () => {
  const { language: currentLang, setLanguage, availableLanguages } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { url } = useLocation();

  // Map available languages to the format expected by the UI
  const languages = availableLanguages.map(lang => ({
    code: lang,
    name: lang.toUpperCase()
  }));

  const handleLangChange = (lang: string) => {
    if (currentLang !== lang) {
      // Update the language in context, which will trigger saving to localStorage
      setLanguage(lang);
      // Reload the current page to fetch data with the new language
      window.location.reload();
    }
  };

  return (
    <header className="bg-primary text-primary-content shadow-md">
      <div className="navbar">
        <div className="navbar-start">
          <div className="dropdown">
            <label tabIndex={0} className="btn btn-ghost lg:hidden">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h8m-8 6h16" />
              </svg>
            </label>
            <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
              <li><Link href="/">Home</Link></li>
              <li><Link href="/items">Items</Link></li>
              <li><Link href="/handbooks">Handbooks</Link></li>
            </ul>
          </div>
          <Link href="/" className="btn btn-ghost normal-case text-xl">Wine App</Link>
        </div>
        <div className="navbar-center hidden md:flex">
          <ul className="menu menu-horizontal px-1">
            {/* ИСПРАВЛЕННЫЕ СТРОКИ: Добавлена проверка `url &&` */}
            <li><Link href="/" class={url === '/' ? 'active' : ''}>Home</Link></li>
            <li><Link href="/items" class={url && url.startsWith('/items') ? 'active' : ''}>Items</Link></li>
            <li><Link href="/handbooks" class={url && url.startsWith('/handbooks') ? 'active' : ''}>Handbooks</Link></li>
          </ul>
        </div>
        <div className="navbar-end flex items-center gap-4">
          {/* Language Selector */}
          <div className="dropdown dropdown-end">
            <label tabIndex={0} className="btn btn-sm btn-ghost">
              {currentLang ? currentLang.toUpperCase() : 'EN'}
            </label>
            <ul tabIndex={0} className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-24">
              {languages.map(lang => (
                <li key={lang.code}>
                  <button 
                    className={currentLang === lang.code ? 'active' : ''}
                    onClick={() => handleLangChange(lang.code)}
                  >
                    {lang.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>
          
          <button 
            className="btn btn-sm btn-error"
            onClick={() => {
              localStorage.removeItem('auth_token');
              window.location.reload();
            }}
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};
