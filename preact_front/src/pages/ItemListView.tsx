// src/pages/ItemListView.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { Link } from '../components/Link';
import { useApi } from '../hooks/useApi';
import { ItemRead } from '../types/item';
import { ItemImage } from '../components/ItemImage';
import { PaginatedResponse } from '../types/base';
import { useLanguage } from '../contexts/LanguageContext';

export const ItemListView = () => {
  const [viewMode, setViewMode] = useState<'table' | 'grid'>(() => {
    const savedViewMode = localStorage.getItem('itemListViewMode');
    return savedViewMode === 'table' || savedViewMode === 'grid' ? savedViewMode : 'table';
  });
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [gridColumns, setGridColumns] = useState(3); // Default to 3 columns
  const pageSize = 12;
  
  const { language } = useLanguage();
  
  const { data, loading, error, refetch } = useApi<PaginatedResponse<ItemRead>>(
    `/list_paginated/${language}`,
    'GET',
    undefined,
    { page, page_size: pageSize, search }
  );

  useEffect(() => {
    localStorage.setItem('itemListViewMode', viewMode);
  }, [viewMode]);

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
              className={`btn ${viewMode === 'table' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setViewMode('table')}
            >
              Table
            </button>
            <button 
              className={`btn ${viewMode === 'grid' ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setViewMode('grid')}
            >
              Grid
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'table' ? (
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Image</th>
                <th>Title</th>
                <th>Category</th>
                <th>Volume</th>
                <th>Price</th>
                <th>Country</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map(item => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td>
                    <ItemImage image_id={item.image_id} size="small" />
                  </td>
                  <td>{item.title}</td>
                  <td>{item.subcategory}</td>
                  <td>{item.vol ? `${item.vol} ml` : 'N/A'}</td>
                  <td>{item.price ? `€${item.price}` : 'N/A'}</td>
                  <td>{item.country}</td>
                  <td>
                    <div className="flex gap-2">
                      <Link href={`/items/${item.id}`} variant="link">
                        View
                      </Link>
                      <Link href={`/items/edit/${item.id}`} variant="link">
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
        <div className={`card-grid grid-cols-${gridColumns}`}>
          {data?.items.map(item => (
            <div key={item.id} className="card">
              <div className="h-48 flex items-center justify-center bg-gray-100">
                <ItemImage image_id={item.image_id} size="large" />
              </div>
              <div className="p-4">
                <h2 className="text-lg font-semibold mb-2">
                  {item?.title || 'No title'}
                </h2>
                <p className="text-sm text-gray-600 mb-1">Volume: {item.vol ? `${item.vol} ml` : 'N/A'}</p>
                <p className="text-sm text-gray-600 mb-1">Price: {item.price ? `€${item.price}` : 'N/A'}</p>
                <p className="text-sm text-gray-600 mb-4">Country: {item.country || 'N/A'}</p>
                <div className="flex justify-end gap-2">
                  <Link href={`/items/${item.id}`} variant="link">
                    View
                  </Link>
                  <Link href={`/items/edit/${item.id}`} variant="link">
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
              className={`btn ${page <= 1 ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => setPage(1)}
              disabled={page <= 1}
            >
              «
            </button>
            <button
              className={`btn ${page <= 1 ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => setPage(prev => Math.max(1, prev - 1))}
              disabled={page <= 1}
            >
              ‹
            </button>
            <button className="btn btn-primary">
              {page} of {Math.ceil((data.total || 0) / pageSize)}
            </button>
            <button
              className={`btn ${page >= Math.ceil((data.total || 0) / pageSize) ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => setPage(prev => Math.min(Math.ceil((data.total || 0) / pageSize), prev + 1))}
              disabled={page >= Math.ceil((data.total || 0) / pageSize)}
            >
              ›
            </button>
            <button
              className={`btn ${page >= Math.ceil((data.total || 0) / pageSize) ? 'opacity-50 cursor-not-allowed' : ''}`}
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