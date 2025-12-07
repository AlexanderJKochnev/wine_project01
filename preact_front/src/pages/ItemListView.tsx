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

  return (
    <div className="space-y-6 w-full">
      <div className="flex flex-row justify-between items-center gap-4">
        <h1 className="text-2xl font-bold">Items</h1>
        <Link href="/items/create" className="btn btn-primary">
          Create New Item
        </Link>
      </div>

      <div className="flex flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Search items..."
            className="input input-bordered w-full max-w-xs"
            value={search}
            onInput={handleSearch}
          />
          <button 
            className={`btn ${viewMode === 'table' ? 'btn-active' : ''}`}
            onClick={() => setViewMode('table')}
          >
            Table
          </button>
          <button 
            className={`btn ${viewMode === 'grid' ? 'btn-active' : ''}`}
            onClick={() => setViewMode('grid')}
          >
            Grid
          </button>
        </div>
      </div>

      {viewMode === 'table' ? (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
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
                <tr key={item.id}>
                  <td>
                    <ItemImage image_id={item.image_id} size="small" />
                  </td>
                  <td>
                    {item.title}
                  </td>
                  <td>
                    {item.subcategory}
                  </td>
                  <td>{item.vol ? `${item.vol} ml` : 'N/A'}</td>
                  <td>{item.price ? `€${item.price}` : 'N/A'}</td>
                  <td>{item.country}</td>
                  <td>
                    <div className="flex gap-2">
                      <Link href={`/items/${item.id}`} className="btn btn-xs btn-info">
                        View
                      </Link>
                      <Link href={`/items/edit/${item.id}`} className="btn btn-xs btn-warning">
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
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {data?.items.map(item => (
            <div key={item.id} className="card bg-base-100 shadow-xl">
              <figure className="h-48">
                <ItemImage image_id={item.image_id} size="large" />
              </figure>
              <div className="card-body">
                <h2 className="card-title">
                  {item.en?.title || item.ru?.title || item.fr?.title || 'No title'}
                </h2>
                <p>Volume: {item.vol ? `${item.vol} ml` : 'N/A'}</p>
                <p>Price: {item.price ? `€${item.price}` : 'N/A'}</p>
                <p>Country: {item.country || 'N/A'}</p>
                <div className="card-actions justify-end">
                  <Link href={`/items/${item.id}`} className="btn btn-info">
                    View
                  </Link>
                  <Link href={`/items/edit/${item.id}`} className="btn btn-warning">
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
          <div className="join">
            <button
              className="join-item btn"
              onClick={() => setPage(1)}
              disabled={page <= 1}
            >
              «
            </button>
            <button
              className="join-item btn"
              onClick={() => setPage(prev => Math.max(1, prev - 1))}
              disabled={page <= 1}
            >
              ‹
            </button>
            <button className="join-item btn btn-active">
              {page} of {Math.ceil((data.total || 0) / pageSize)}
            </button>
            <button
              className="join-item btn"
              onClick={() => setPage(prev => Math.min(Math.ceil((data.total || 0) / pageSize), prev + 1))}
              disabled={page >= Math.ceil((data.total || 0) / pageSize)}
            >
              ›
            </button>
            <button
              className="join-item btn"
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