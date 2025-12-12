// src/components/Header.tsx
import { h } from 'preact';
import { useLocation } from 'preact-iso';
import { Link } from './Link';
import { useLanguage } from '../contexts/LanguageContext';
import { getAuthToken, removeAuthToken } from '../lib/apiClient';
import Logo from '../logo.png';

interface HeaderProps {
  sidebarVisible: boolean;
  setSidebarVisible: (visible: boolean) => void;
}

export const Header = ({ sidebarVisible, setSidebarVisible }: HeaderProps) => {
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

  const toggleSidebar = () => {
    if (typeof setSidebarVisible === 'function') {
      setSidebarVisible(!sidebarVisible);
    } else {
      console.error('setSidebarVisible is not a function:', typeof setSidebarVisible);
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        {/* Left: Hamburger menu and Logo */}
        <div className="header-left">
          <div className="flex items-center">
            {/* Hamburger menu button - only visible on mobile */}
            <button 
              className="hamburger-menu mr-4 lg:hidden"
              onClick={toggleSidebar}
              aria-label="Toggle navigation menu"
            >
              <span className="hamburger-line"></span>
              <span className="hamburger-line"></span>
              <span className="hamburger-line"></span>
            </button>
            <img src={Logo} alt="Логотип"
             className="logo-image"/>
          </div>
        </div>
        
        {/* Center: Site Name */}
        <div className="header-center">
          <Link href="/" className="header-site-name">THE VERY GOOD SITE</Link>
        </div>
        
        {/* Right: Auth Controls */}
        <div className="header-right">
          {isAuthenticated ? (
            <div className="auth-controls">
              <span className="hidden md:inline">Welcome, User</span>
              <button 
                className="btn btn-primary"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-controls">
              <input
                type="text"
                placeholder="Login"
                className="auth-input"
              />
              <input
                type="password"
                placeholder="Password"
                className="auth-input"
              />
              <button className="btn btn-primary">
                Login
              </button>
            </div>
          )}
          
          {/* Language Selector - dropdown */}
          <div className="relative">
            <select 
              value={currentLang} 
              onChange={(e) => handleLangChange(e.target.value)}
              className="btn btn-ghost bg-transparent border-none"
            >
              {languages.map(lang => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};
