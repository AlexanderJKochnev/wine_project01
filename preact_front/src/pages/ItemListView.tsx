// src/pages/ItemListView.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { Link } from '../components/Link';
import { useApi } from '../hooks/useApi';
import { ItemRead } from '../types/item';
import { ItemImage } from '../components/ItemImage';
import { PaginatedResponse } from '../types/base';
import { useLanguage } from '../contexts/LanguageContext';

export const ItemListView = () => {
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [gridColumns, setGridColumns] = useState(3); // Default to 3 columns
  const pageSize = 10;
  
  const { language } = useLanguage();
  
  const { data, loading, error, refetch } = useApi<PaginatedResponse<ItemRead>>(
    `/list_paginated/${language}`,
    'GET',
    undefined,
    { page, page_size: pageSize, search }
  );

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

  const handleSearch = (e: Event) => {
    const target = e.target as HTMLInputElement;
    setSearch(target.value);
    setPage(1); // Reset to first page when searching
  };

  // Function to handle grid column changes
  const handleGridColumnsChange = (e: Event) => {
    const target = e.target as HTMLSelectElement;
    setGridColumns(parseInt(target.value));
  };

  return (
    <div className="space-y-6 w-full">
      <div className="flex flex-row justify-between items-center gap-4">
        <h1 className="text-2xl font-bold">Items</h1>
        <Link href="/items/create" variant="primary">
          Create New Item
        </Link>
      </div>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
          <input
            type="text"
            placeholder="Search items..."
            className="border rounded px-3 py-1.5 w-full max-w-xs border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={search}
            onInput={handleSearch}
          />
          <div className="flex gap-2">
            <button 
              className={`inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 text-base px-4 py-2 ${viewMode === 'table' ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-200 hover:bg-gray-300 text-gray-800 border-gray-300'}`}
              onClick={() => setViewMode('table')}
            >
              Table
            </button>
            <button 
              className={`inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 text-base px-4 py-2 ${viewMode === 'grid' ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-200 hover:bg-gray-300 text-gray-800 border-gray-300'}`}
              onClick={() => setViewMode('grid')}
            >
              Grid
            </button>
          </div>
        </div>
        
        {viewMode === 'grid' && (
          <div className="flex items-center gap-2">
            <label className="text-sm">Columns:</label>
            <select 
              className="border rounded px-3 py-1.5 text-sm border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" 
              value={gridColumns} 
              onChange={handleGridColumnsChange}
            >
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
              <option value={4}>4</option>
              <option value={5}>5</option>
              <option value={6}>6</option>
            </select>
          </div>
        )}
      </div>

      {viewMode === 'table' ? (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Image</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volume</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Country</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.items.map(item => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <ItemImage image_id={item.image_id} size="small" />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.title}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.subcategory}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.vol ? `${item.vol} ml` : 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.price ? `€${item.price}` : 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.country}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex gap-2">
                      <Link href={`/items/${item.id}`} variant="info" size="xs">
                        View
                      </Link>
                      <Link href={`/items/edit/${item.id}`} variant="warning" size="xs">
                        Edit
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className={`grid gap-6 ${gridColumns === 1 ? 'grid-cols-1' : ''} ${gridColumns === 2 ? 'grid-cols-2' : ''} ${gridColumns === 3 ? 'grid-cols-3' : ''} ${gridColumns === 4 ? 'grid-cols-4' : ''} ${gridColumns === 5 ? 'grid-cols-5' : ''} ${gridColumns === 6 ? 'grid-cols-6' : ''}`}>
          {data?.items.map(item => (
            <div key={item.id} className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
              <div className="h-48 flex items-center justify-center bg-gray-100">
                <ItemImage image_id={item.image_id} size="large" />
              </div>
              <div className="p-4">
                <h2 className="text-lg font-semibold mb-2">
                  {item.en?.title || item.ru?.title || item.fr?.title || 'No title'}
                </h2>
                <p className="text-sm text-gray-600 mb-1">Volume: {item.vol ? `${item.vol} ml` : 'N/A'}</p>
                <p className="text-sm text-gray-600 mb-1">Price: {item.price ? `€${item.price}` : 'N/A'}</p>
                <p className="text-sm text-gray-600 mb-4">Country: {item.country || 'N/A'}</p>
                <div className="flex justify-end gap-2">
                  <Link href={`/items/${item.id}`} variant="info">
                    View
                  </Link>
                  <Link href={`/items/edit/${item.id}`} variant="warning">
                    Edit
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total && data.total > pageSize && (
        <div className="flex justify-center mt-6">
          <div className="flex space-x-1">
            <button
              className={`inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-gray-200 hover:bg-gray-300 text-gray-800 border-gray-300 text-base px-4 py-2 ${page <= 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-300'}`}
              onClick={() => setPage(1)}
              disabled={page <= 1}
            >
              «
            </button>
            <button
              className={`inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-gray-200 hover:bg-gray-300 text-gray-800 border-gray-300 text-base px-4 py-2 ${page <= 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-300'}`}
              onClick={() => setPage(prev => Math.max(1, prev - 1))}
              disabled={page <= 1}
            >
              ‹
            </button>
            <button className="inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-blue-600 text-white border-blue-700 text-base px-4 py-2">
              {page} of {Math.ceil((data.total || 0) / pageSize)}
            </button>
            <button
              className={`inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-gray-200 hover:bg-gray-300 text-gray-800 border-gray-300 text-base px-4 py-2 ${page >= Math.ceil((data.total || 0) / pageSize) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-300'}`}
              onClick={() => setPage(prev => Math.min(Math.ceil((data.total || 0) / pageSize), prev + 1))}
              disabled={page >= Math.ceil((data.total || 0) / pageSize)}
            >
              ›
            </button>
            <button
              className={`inline-flex items-center justify-center border rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-gray-200 hover:bg-gray-300 text-gray-800 border-gray-300 text-base px-4 py-2 ${page >= Math.ceil((data.total || 0) / pageSize) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-300'}`}
              onClick={() => setPage(Math.ceil((data.total || 0) / pageSize))}
              disabled={page >= Math.ceil((data.total || 0) / pageSize)}
            >
              »
            </button>
          </div>
        </div>
      )}
    </div>
  );
};