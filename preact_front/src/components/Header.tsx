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
          <Link href="/" className="text-xl font-bold normal-case">THE VERY GOOD SITE</Link>
        </div>
        
        {/* Right: Auth Controls */}
        <div className="navbar-end flex-1 flex justify-end items-center gap-2">
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <span className="hidden md:inline">Welcome, User</span>
              <button 
                className="inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-purple-600 hover:bg-purple-700 text-white border-purple-700 text-sm px-3 py-1.5"
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
                  className="border rounded px-3 py-1.5 text-sm w-24 md:w-32 mr-1 border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="form-control">
                <input
                  type="password"
                  placeholder="Password"
                  className="border rounded px-3 py-1.5 text-sm w-24 md:w-32 mr-1 border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button className="inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-blue-600 hover:bg-blue-700 text-white border-blue-700 text-sm px-3 py-1.5">
                Login
              </button>
            </div>
          )}
          
          {/* Language Selector */}
          <div className="dropdown dropdown-end ml-2 relative">
            <label tabIndex={0} className="inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-transparent hover:bg-gray-200 text-gray-700 border-transparent text-sm px-3 py-1.5">
              {currentLang ? currentLang.toUpperCase() : 'EN'}
            </label>
            <ul tabIndex={0} className="dropdown-content z-[1] p-2 bg-white shadow-lg rounded-md w-24 absolute mt-1 min-w-max">
              {languages.map(lang => (
                <li key={lang.code}>
                  <button 
                    className={`block w-full text-left px-4 py-2 text-sm ${currentLang === lang.code ? 'bg-gray-100' : 'hover:bg-gray-100'}`}
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
