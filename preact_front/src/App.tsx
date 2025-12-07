// src/App.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { Router, Route, useLocation } from 'preact-iso';
import { getAuthToken } from './lib/apiClient';
import { LoginForm } from './components/LoginForm';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Footer } from './components/Footer';
import { ItemListView } from './pages/ItemListView';
import { ItemDetailView } from './pages/ItemDetailView';
import { ItemCreateForm } from './pages/ItemCreateForm';
import { ItemUpdateForm } from './pages/ItemUpdateForm';
import { HandbookList } from './pages/HandbookList';
import { HandbookDetail } from './pages/HandbookDetail';
import { HandbookCreateForm } from './pages/HandbookCreateForm';
import { HandbookUpdateForm } from './pages/HandbookUpdateForm';
import { HandbookTypeList } from './pages/HandbookTypeList';
import { Home } from './pages/Home';
import { NotFound } from './pages/_404';

function HomeRedirect() {
  const { route } = useLocation();
  
  // Redirect to /items immediately
  route('/items', true); // true for replace (equivalent to { replace: true })
  
  return null; // Return null while redirecting
}

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-base-100 flex items-center justify-center p-4">
        <div className="card bg-base-100 w-full max-w-md p-6 shadow-lg">
          <LoginForm onLogin={() => setIsAuthenticated(true)} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      
      <div className="flex flex-1 min-h-[80vh] w-full">
        <div className="flex w-full">
          {/* Content area - takes up at least 80% of body width */}
          <main className="flex-[4] min-w-[80%] p-4 md:p-6 bg-base-100 overflow-auto">
            <div className="w-full">
              <Router>
                <Route path="/" component={isAuthenticated ? HomeRedirect : Home} />
                <Route path="/items" component={ItemListView} />
                <Route path="/items/:id" component={ItemDetailView} />
                <Route path="/items/create" component={ItemCreateForm} />
                <Route path="/items/edit/:id" component={ItemUpdateForm} />

                <Route path="/handbooks" component={HandbookList} />
                <Route path="/handbooks/:type" component={HandbookTypeList} />
                <Route path="/handbooks/:type/:id" component={HandbookDetail} />
                <Route path="/handbooks/:type/create" component={HandbookCreateForm} />
                <Route path="/handbooks/:type/edit/:id" component={HandbookUpdateForm} />

                <Route default component={NotFound} />
              </Router>
            </div>
          </main>
          
          {/* Navbar (Sidebar) - takes up max 20% of body width */}
          <div className="flex-[1] max-w-[20%]">
            <Sidebar />
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}