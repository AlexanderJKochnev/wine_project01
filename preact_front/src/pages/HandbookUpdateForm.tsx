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
        'categories': `/read/categories/${id}`,
        'countries': `/read/countries/${id}`,
        'regions': `/read/regions/${id}`,
        'subcategories': `/read/subcategories/${id}`,
        'subregions': `/read/subregions/${id}`,
        'sweetness': `/read/sweetness/${id}`,
        'superfoods': `/read/superfoods/${id}`,
        'foods': `/read/foods/${id}`,
        'varietals': `/read/varietals/${id}`,
      };
      return endpoints[type] || `/read/${type}/${id}`;
    })(),
    'GET'
  );

  // Additional API calls for dropdowns based on the model type
  const { data: countriesData, loading: loadingCountries } = useApi<any[]>(
    type === 'region' ? '/handbooks/countries/ru' : null,
    'GET',
    undefined,
    undefined,
    type === 'region'
  );

  const { data: categoriesData, loading: loadingCategories } = useApi<any[]>(
    type === 'subcategories' ? '/handbooks/categories/ru' : null,
    'GET',
    undefined,
    undefined,
    type === 'subcategories'
  );

  const { data: regionsData, loading: loadingRegions } = useApi<any[]>(
    type === 'subregions' ? '/handbooks/regions/ru' : null,
    'GET',
    undefined,
    undefined,
    type === 'subregions'
  );

  const { data: superfoodsData, loading: loadingSuperfoods } = useApi<any[]>(
    type === 'foods' ? '/handbooks/superfoods/ru' : null,
    'GET',
    undefined,
    undefined,
    type === 'foods'
  );
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    countries_id: undefined,
    categories_id: undefined,
    region_id: undefined,
    suprefood_id: undefined
  });
  const [loading, setLoading] = useState(false);

  // Load initial data when item is loaded
  useEffect(() => {
    if (data) {
      setFormData({
        name: data.name || '',
        description: data.description || '',
        countries_id: data.countries_id || undefined,
        categories_id: data.categories_id || undefined,
        region_id: data.region_id || undefined,
        suprefood_id: data.suprefood_id || undefined
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
      'regions': `/patch/regions/${id}`,
    };
    return endpoints[type] || `/patch/${type}/${id}`;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await apiClient(getEndpoint(type), {
        method: 'PATCH',
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
              
              {/* Conditional dropdowns based on handbook type */}
              {type === 'region' && (
                <div>
                  <label className="label">
                    <span className="label-text">Country</span>
                  </label>
                  {loadingCountries ? (
                    <select className="select select-bordered w-full" disabled>
                      <option>Loading...</option>
                    </select>
                  ) : (
                    <select
                      name="countries_id"
                      value={formData.countries_id || ''}
                      onChange={(e) => {
                        const target = e.target as HTMLSelectElement;
                        setFormData(prev => ({
                          ...prev,
                          countries_id: target.value ? parseInt(target.value) : undefined
                        }));
                      }}
                      className="select select-bordered w-full"
                    >
                      <option value="">Select a country</option>
                      {countriesData && countriesData.map((country: any) => (
                        <option key={country.id} value={country.id}>
                          {country.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
              
              {type === 'subcategories' && (
                <div>
                  <label className="label">
                    <span className="label-text">Category</span>
                  </label>
                  {loadingCategories ? (
                    <select className="select select-bordered w-full" disabled>
                      <option>Loading...</option>
                    </select>
                  ) : (
                    <select
                      name="categories_id"
                      value={formData.categories_id || ''}
                      onChange={(e) => {
                        const target = e.target as HTMLSelectElement;
                        setFormData(prev => ({
                          ...prev,
                          categories_id: target.value ? parseInt(target.value) : undefined
                        }));
                      }}
                      className="select select-bordered w-full"
                    >
                      <option value="">Select a category</option>
                      {categoriesData && categoriesData.map((category: any) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
              
              {type === 'subregions' && (
                <div>
                  <label className="label">
                    <span className="label-text">Region</span>
                  </label>
                  {loadingRegions ? (
                    <select className="select select-bordered w-full" disabled>
                      <option>Loading...</option>
                    </select>
                  ) : (
                    <select
                      name="region_id"
                      value={formData.region_id || ''}
                      onChange={(e) => {
                        const target = e.target as HTMLSelectElement;
                        setFormData(prev => ({
                          ...prev,
                          region_id: target.value ? parseInt(target.value) : undefined
                        }));
                      }}
                      className="select select-bordered w-full"
                    >
                      <option value="">Select a region</option>
                      {regionsData && regionsData.map((region: any) => (
                        <option key={region.id} value={region.id}>
                          {region.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
              
              {type === 'foods' && (
                <div>
                  <label className="label">
                    <span className="label-text">Superfood</span>
                  </label>
                  {loadingSuperfoods ? (
                    <select className="select select-bordered w-full" disabled>
                      <option>Loading...</option>
                    </select>
                  ) : (
                    <select
                      name="suprefood_id"
                      value={formData.suprefood_id || ''}
                      onChange={(e) => {
                        const target = e.target as HTMLSelectElement;
                        setFormData(prev => ({
                          ...prev,
                          suprefood_id: target.value ? parseInt(target.value) : undefined
                        }));
                      }}
                      className="select select-bordered w-full"
                    >
                      <option value="">Select a superfood</option>
                      {superfoodsData && superfoodsData.map((superfood: any) => (
                        <option key={superfood.id} value={superfood.id}>
                          {superfood.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
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