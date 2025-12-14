// src/pages/HandbookCreateForm.tsx
import { h, useState } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { Link } from '../components/Link';
import { apiClient } from '../lib/apiClient';
import { useNotification } from '../hooks/useNotification';

export const HandbookCreateForm = () => {
  const { path } = useLocation();
  
  // Extract handbook type from path: /handbooks/:type/create
  // Using regex to extract type parameter more reliably
  const match = path.match(/^\/handbooks\/([^\/]+)\/create$/);
  const type = match ? match[1] : undefined;
  
  // Check if type is valid
  if (!type) {
    return (
      <div className="alert-error">
        <div>
          <span>Error: Invalid handbook ID: {match ? match[1] : 'unknown'}. Expected format: /handbooks/type/create</span>
        </div>
      </div>
    );
  }
  
  const { route } = useLocation();
  const { showNotification } = useNotification();
  
  const [formData, setFormData] = useState({
    name: '',
    name_en: '',
    name_ru: '',
    name_fr: '',
    description: '',
    description_en: '',
    description_ru: '',
    description_fr: '',
    code: '',
    value: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e: Event) => {
    const target = e.target as HTMLInputElement | HTMLTextAreaElement;
    const { name, value } = target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Get the readable name for the handbook type
  const getReadableName = (type: string) => {
    const names: Record<string, string> = {
      'categories': 'Category',
      'countries': 'Country',
      'regions': 'Region',
      'subcategories': 'Subcategory',
      'subregions': 'Subregion',
      'sweetness': 'Sweetness',
      'superfoods': 'Superfood',
      'foods': 'Food',
      'varietals': 'Varietal',
    };
    return names[type] || (type && type.charAt(0).toUpperCase() + type.slice(1)) || 'Unknown';
  };

  // Determine the endpoint based on the handbook type
  const getEndpoint = (type: string) => {
    const endpoints: Record<string, string> = {
      'categories': '/create/categories',
      'countries': '/create/countries',
      'regions': '/create/regions',
      'subcategories': '/create/subcategories',
      'subregions': '/create/subregions',
      'sweetness': '/create/sweetness',
      'superfoods': '/create/superfoods',
      'foods': '/create/foods',
      'varietals': '/create/varietals',
    };
    return endpoints[type] || `/create/${type}`;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await apiClient(getEndpoint(type), {
        method: 'POST',
        body: formData
      });
      showNotification(`${getReadableName(type)} created successfully`, 'success');
      route(`/handbooks/${type}`);
    } catch (error) {
      console.error(`Error creating ${type}:`, error);
      showNotification(`Error creating ${getReadableName(type)}: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Create New {getReadableName(type)}</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <h2 className="card-title">Basic Information</h2>
            <div className="space-y-4">
              <div>
                <label className="label">
                  <span className="label-text">Name</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onInput={handleChange}
                  className="input input-bordered w-full"
                  placeholder="Name"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Name (EN)</span>
                </label>
                <input
                  type="text"
                  name="name_en"
                  value={formData.name_en}
                  onInput={handleChange}
                  className="input input-bordered w-full"
                  placeholder="English name"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Name (RU)</span>
                </label>
                <input
                  type="text"
                  name="name_ru"
                  value={formData.name_ru}
                  onInput={handleChange}
                  className="input input-bordered w-full"
                  placeholder="Russian name"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Name (FR)</span>
                </label>
                <input
                  type="text"
                  name="name_fr"
                  value={formData.name_fr}
                  onInput={handleChange}
                  className="input input-bordered w-full"
                  placeholder="French name"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Description</span>
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onInput={handleChange}
                  className="textarea textarea-bordered w-full"
                  rows={3}
                  placeholder="Description"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Description (EN)</span>
                </label>
                <textarea
                  name="description_en"
                  value={formData.description_en}
                  onInput={handleChange}
                  className="textarea textarea-bordered w-full"
                  rows={3}
                  placeholder="English description"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Description (RU)</span>
                </label>
                <textarea
                  name="description_ru"
                  value={formData.description_ru}
                  onInput={handleChange}
                  className="textarea textarea-bordered w-full"
                  rows={3}
                  placeholder="Russian description"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Description (FR)</span>
                </label>
                <textarea
                  name="description_fr"
                  value={formData.description_fr}
                  onInput={handleChange}
                  className="textarea textarea-bordered w-full"
                  rows={3}
                  placeholder="French description"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Code</span>
                </label>
                <input
                  type="text"
                  name="code"
                  value={formData.code}
                  onInput={handleChange}
                  className="input input-bordered w-full"
                  placeholder="Code (optional)"
                />
              </div>
              
              <div>
                <label className="label">
                  <span className="label-text">Value</span>
                </label>
                <input
                  type="text"
                  name="value"
                  value={formData.value}
                  onInput={handleChange}
                  className="input input-bordered w-full"
                  placeholder="Value (optional)"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <button 
            type="submit" 
            className={`btn btn-primary ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? `Creating ${getReadableName(type)}...` : `Create ${getReadableName(type)}`}
          </button>
          <Link href={`/handbooks/${type}`} variant="ghost">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
};