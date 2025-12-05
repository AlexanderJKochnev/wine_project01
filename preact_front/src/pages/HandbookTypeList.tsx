// src/pages/HandbookTypeList.tsx
import { h, useState } from 'preact/hooks';
import { Link, useLocation } from 'preact-iso';
import { useApi } from '../hooks/useApi';

export const HandbookTypeList = () => {
  const { path } = useLocation();
  const type = path.split('/')[2];
  const [search, setSearch] = useState('');
  
  // Determine the endpoint based on the handbook type
  const getEndpoint = (type: string) => {
    const endpoints: Record<string, string> = {
      'categories': '/categories/all',
      'countries': '/countries/all',
      'subcategories': '/subcategories/all',
      'subregions': '/subregions/all',
      'sweetnesses': '/sweetnesses/all',
      'foods': '/foods/all',
      'varietals': '/varietals/all',
    };
    return endpoints[type] || `/handbooks/${type}/all`;
  };

  const { data, loading, error, refetch } = useApi<any[]>(
    getEndpoint(type),
    'GET'
  );

  // Get the readable name for the handbook type
  const getReadableName = (type: string) => {
    const names: Record<string, string> = {
      'categories': 'Categories',
      'countries': 'Countries',
      'subcategories': 'Subcategories',
      'subregions': 'Subregions',
      'sweetnesses': 'Sweetnesses',
      'foods': 'Foods',
      'varietals': 'Varietals',
    };
    return names[type] || type.charAt(0).toUpperCase() + type.slice(1) + 's';
  };

  // Filter data based on search
  const filteredData = data?.filter(item => {
    const searchTerm = search.toLowerCase();
    return (
      (item.name && item.name.toLowerCase().includes(searchTerm)) ||
      (item.name_en && item.name_en.toLowerCase().includes(searchTerm)) ||
      (item.name_ru && item.name_ru.toLowerCase().includes(searchTerm)) ||
      (item.name_fr && item.name_fr.toLowerCase().includes(searchTerm)) ||
      (item.description && item.description.toLowerCase().includes(searchTerm)) ||
      (item.id && item.id.toString().includes(searchTerm))
    );
  }) || [];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <div>
          <span>Error: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold">{getReadableName(type)}</h1>
        <Link href={`/handbooks/${type}/create`} className="btn btn-primary">
          Create New {getReadableName(type).slice(0, -1)}
        </Link>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder={`Search ${getReadableName(type).toLowerCase()}...`}
          className="input input-bordered w-full max-w-xs"
          value={search}
          onInput={(e) => {
            const target = e.target as HTMLInputElement;
            setSearch(target.value);
          }}
        />
      </div>

      <div className="overflow-x-auto">
        <table className="table table-zebra">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>
                  {item.name || item.name_en || item.name_ru || item.name_fr || 'No name'}
                </td>
                <td>
                  {item.description || item.description_en || item.description_ru || item.description_fr || 'N/A'}
                </td>
                <td>
                  <div className="flex gap-2">
                    <Link href={`/handbooks/${type}/${item.id}`} className="btn btn-xs btn-info">
                      View
                    </Link>
                    <Link href={`/handbooks/${type}/edit/${item.id}`} className="btn btn-xs btn-warning">
                      Edit
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredData.length === 0 && (
        <div className="text-center py-8">
          <p>No {getReadableName(type).toLowerCase()} found.</p>
        </div>
      )}
    </div>
  );
};