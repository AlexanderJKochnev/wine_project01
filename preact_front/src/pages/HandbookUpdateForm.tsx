// src/pages/HandbookUpdateForm.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { Link } from '../components/Link';
import { useApi } from '../hooks/useApi';
import { apiClient } from '../lib/apiClient';
import { useNotification } from '../hooks/useNotification';
import { useLanguage } from '../contexts/LanguageContext';

export const HandbookUpdateForm = () => {
  const { path } = useLocation();
  const pathParts = path.split('/');
  const type = pathParts[2];
  const idParam = pathParts[4];
  const id = parseInt(idParam);
  const { route } = useLocation();
  const { showNotification } = useNotification();
  
  // Check if ID is valid
  if (isNaN(id)) {
    return (
      <div className="alert alert-error">
        <div>
          <span>Invalid handbook ID: {idParam}</span>
        </div>
      </div>
    );
  }
  
  const { language } = useLanguage();
  
  const { data, loading: loadingItem, error: errorItem } = useApi<any>(
    (() => {
      const endpoints: Record<string, string> = {
        'categories': `/get/categories/${language}/${id}`,
        'countries': `/get/countries/${language}/${id}`,
        'regions': `/get/regions/${language}/${id}`,
        'subcategories': `/get/subcategories/${language}/${id}`,
        'subregions': `/get/subregions/${language}/${id}`,
        'sweetness': `/get/sweetness/${language}/${id}`,
        'foods': `/get/foods/${language}/${id}`,
        'varietals': `/get/varietals/${language}/${id}`,
      };
      return endpoints[type] || `/get/${type}/${language}/${id}`;
    })(),
    'GET'
  );
  
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

  // Load initial data when item is loaded
  useEffect(() => {
    if (data) {
      setFormData({
        name: data.name || '',
        name_en: data.name_en || '',
        name_ru: data.name_ru || '',
        name_fr: data.name_fr || '',
        description: data.description || '',
        description_en: data.description_en || '',
        description_ru: data.description_ru || '',
        description_fr: data.description_fr || '',
        code: data.code || '',
        value: data.value || ''
      });
    }
  }, [data]);

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
      'subcategories': 'Subcategory',
      'subregions': 'Subregion',
      'sweetness': 'Sweetness',
      'foods': 'Food',
      'varietals': 'Varietal',
    };
    return names[type] || type.charAt(0).toUpperCase() + type.slice(1);
  };

  // Determine the endpoint based on the handbook type
  const getEndpoint = (type: string) => {
    const endpoints: Record<string, string> = {
      'categories': `/patch/categories/${id}`,
      'countries': `/patch/countries/${id}`,
      'subcategories': `/patch/subcategories/${id}`,
      'subregions': `/patch/subregions/${id}`,
      'sweetness': `/patch/sweetness/${id}`,
      'foods': `/patch/foods/${id}`,
      'varietals': `/patch/varietals/${id}`,
    };
    return endpoints[type] || `/patch/${type}/${id}`;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await apiClient(getEndpoint(type), {
        method: 'PUT',
        body: formData
      });
      showNotification(`${getReadableName(type)} updated successfully`, 'success');
      route(`/handbooks/${type}/${id}`);
    } catch (error) {
      console.error(`Error updating ${type}:`, error);
      showNotification(`Error updating ${getReadableName(type)}: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loadingItem) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (errorItem) {
    return (
      <div className="alert alert-error">
        <div>
          <span>Error: {errorItem}</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="alert alert-warning">
        <div>
          <span>Item not found</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Edit {getReadableName(type)}</h1>
      
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
            {loading ? `Updating ${getReadableName(type)}...` : `Update ${getReadableName(type)}`}
          </button>
          <Link href={`/handbooks/${type}/${id}`} variant="ghost">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
};