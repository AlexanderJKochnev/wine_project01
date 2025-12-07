// src/pages/HandbookDetail.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { Link } from '../components/Link';
import { useApi } from '../hooks/useApi';
import { deleteItem } from '../lib/apiClient';
import { useNotification } from '../hooks/useNotification';

export const HandbookDetail = () => {
  const { path } = useLocation();
  const pathParts = path.split('/');
  const type = pathParts[2];
  const idParam = pathParts[3];
  const id = parseInt(idParam);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
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
  
  // Determine the endpoint based on the handbook type
  const getEndpoint = (type: string) => {
    const lang = localStorage.getItem('language') || 'en';
    const endpoints: Record<string, string> = {
      'categories': `/get/categories/${lang}/${id}`,
      'countries': `/get/countries/${lang}/${id}`,
      'subcategories': `/get/subcategories/${lang}/${id}`,
      'subregions': `/get/subregions/${lang}/${id}`,
      'sweetnesses': `/get/sweetnesses/${lang}/${id}`,
      'foods': `/get/foods/${lang}/${id}`,
      'varietals': `/get/varietals/${lang}/${id}`,
    };
    return endpoints[type] || `/get/${type}/${lang}/${id}`;
  };

  const { data, loading, error, refetch } = useApi<any>(
    getEndpoint(type),
    'GET'
  );

  const handleDelete = async () => {
    const lang = localStorage.getItem('language') || 'en';
    const deleteEndpoint = `/delete/${type}/${id}`;
    const success = await deleteItem(deleteEndpoint);
    if (success) {
      showNotification('Item deleted successfully', 'success');
      window.location.href = `/handbooks/${type}`;
    } else {
      showNotification('Failed to delete item', 'error');
    }
    setShowConfirmDialog(false);
  };

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

  if (!data) {
    return (
      <div className="alert alert-warning">
        <div>
          <span>Item not found</span>
        </div>
      </div>
    );
  }

  // Get the readable name for the handbook type
  const getReadableName = (type: string) => {
    const names: Record<string, string> = {
      'categories': 'Category',
      'countries': 'Country',
      'subcategories': 'Subcategory',
      'subregions': 'Subregion',
      'sweetnesses': 'Sweetness',
      'foods': 'Food',
      'varietals': 'Varietal',
    };
    return names[type] || type.charAt(0).toUpperCase() + type.slice(1);
  };

  // Get the name field from the data (try different possible names)
  const getName = (data: any) => {
    return data.name || data.name_en || data.name_ru || data.name_fr || data.title || data.id || 'Unnamed';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {getReadableName(type)} Detail: {getName(data)}
        </h1>
        <div className="flex gap-2">
          <Link href={`/handbooks/${type}/edit/${id}`} className="btn btn-warning">
            Edit
          </Link>
          <button 
            className="btn btn-error"
            onClick={() => setShowConfirmDialog(true)}
          >
            Delete
          </button>
        </div>
      </div>

      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">Information</h2>
          <div className="space-y-2">
            <div className="flex">
              <span className="font-semibold w-32">ID:</span>
              <span>{data.id}</span>
            </div>
            
            {/* Try to display name in different languages if available */}
            {data.name && (
              <div className="flex">
                <span className="font-semibold w-32">Name:</span>
                <span>{data.name}</span>
              </div>
            )}
            
            {data.name_en && (
              <div className="flex">
                <span className="font-semibold w-32">Name (EN):</span>
                <span>{data.name_en}</span>
              </div>
            )}
            
            {data.name_ru && (
              <div className="flex">
                <span className="font-semibold w-32">Name (RU):</span>
                <span>{data.name_ru}</span>
              </div>
            )}
            
            {data.name_fr && (
              <div className="flex">
                <span className="font-semibold w-32">Name (FR):</span>
                <span>{data.name_fr}</span>
              </div>
            )}
            
            {data.description && (
              <div className="flex">
                <span className="font-semibold w-32">Description:</span>
                <span>{data.description}</span>
              </div>
            )}
            
            {data.description_en && (
              <div className="flex">
                <span className="font-semibold w-32">Description (EN):</span>
                <span>{data.description_en}</span>
              </div>
            )}
            
            {data.description_ru && (
              <div className="flex">
                <span className="font-semibold w-32">Description (RU):</span>
                <span>{data.description_ru}</span>
              </div>
            )}
            
            {data.description_fr && (
              <div className="flex">
                <span className="font-semibold w-32">Description (FR):</span>
                <span>{data.description_fr}</span>
              </div>
            )}
            
            {/* Add any other common fields */}
            {data.code && (
              <div className="flex">
                <span className="font-semibold w-32">Code:</span>
                <span>{data.code}</span>
              </div>
            )}
            
            {data.value && (
              <div className="flex">
                <span className="font-semibold w-32">Value:</span>
                <span>{data.value}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-4">
        <Link href={`/handbooks/${type}`} className="btn btn-ghost">
          ← Back to {getReadableName(type)} List
        </Link>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg">Confirm Delete</h3>
            <p className="py-4">Are you sure you want to delete this {getReadableName(type).toLowerCase()}?</p>
            <div className="modal-action">
              <button 
                className="btn btn-error"
                onClick={handleDelete}
              >
                Yes, Delete
              </button>
              <button 
                className="btn"
                onClick={() => setShowConfirmDialog(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};