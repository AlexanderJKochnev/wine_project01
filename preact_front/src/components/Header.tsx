// src/components/Header.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';
import { Link } from './Link';
import { useLanguage } from '../contexts/LanguageContext';
import { getAuthToken, removeAuthToken } from '../lib/apiClient';

export const Header = () => {
  const { language: currentLang, setLanguage, availableLanguages } = useLanguage();
  const { url } = useLocation();
  const token = getAuthToken();
  const isAuthenticated = !!token;

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

  const handleLogout = () => {
    removeAuthToken();
    window.location.reload();
  };

  return (
    <header className="bg-primary text-primary-content shadow-md z-50 h-[15vh] min-h-[80px] max-h-[135px]">
      <div className="navbar h-full px-4">
        {/* Left: Logo */}
        <div className="navbar-start flex-1">
          <div className="flex items-center">
            <div className="text-xl font-bold">🍷</div>
          </div>
        </div>
        
        {/* Center: Site Name */}
        <div className="navbar-center flex-1">
          <Link href="/" className="text-xl font-bold normal-case">Wine App</Link>
        </div>
        
        {/* Right: Auth Controls */}
        <div className="navbar-end flex-1 flex justify-end items-center gap-2">
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <span className="hidden md:inline">Welcome, User</span>
              <button 
                className="btn btn-secondary btn-sm"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <div className="form-control">
                <input
                  type="text"
                  placeholder="Login"
                  className="input input-bordered input-sm w-24 md:w-32 mr-1"
                />
              </div>
              <div className="form-control">
                <input
                  type="password"
                  placeholder="Password"
                  className="input input-bordered input-sm w-24 md:w-32 mr-1"
                />
              </div>
              <button className="btn btn-primary btn-sm">
                Login
              </button>
            </div>
          )}
          
          {/* Language Selector */}
          <div className="dropdown dropdown-end ml-2">
            <label tabIndex={0} className="btn btn-ghost btn-sm">
              {currentLang ? currentLang.toUpperCase() : 'EN'}
            </label>
            <ul tabIndex={0} className="dropdown-content z-[1] p-2 menu shadow bg-base-100 text-base-content rounded-box w-24">
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
        </div>
      </div>
    </header>
  );
};
