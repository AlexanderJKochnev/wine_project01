// src/pages/ItemDetailView.tsx
import { h, useState, useEffect } from 'preact/hooks';
import { useLocation } from 'preact-iso';
import { Link } from '../components/Link';
import { useApi } from '../hooks/useApi';
import { ItemRead } from '../types/item';
import { ItemImage } from '../components/ItemImage';
import { deleteItem } from '../lib/apiClient';
import { useNotification } from '../hooks/useNotification';
import { Notification } from '../components/Notification';

export const ItemDetailView = () => {
  const { path } = useLocation();
  const id = parseInt(path.split('/')[3]);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const { showNotification } = useNotification();
  
  const { data, loading, error, refetch } = useApi<ItemRead>(
    `/items/${id}`,
    'GET'
  );

  const handleDelete = async () => {
    const success = await deleteItem(`/items/${id}`);
    if (success) {
      showNotification('Item deleted successfully', 'success');
      window.location.href = '/items';
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

  // Function to get field value, preferring non-null values
  const getFieldValue = (field: string, item: ItemRead) => {
    const enValue = item.en?.[field as keyof typeof item.en];
    const ruValue = item.ru?.[field as keyof typeof item.ru];
    const frValue = item.fr?.[field as keyof typeof item.fr];
    
    return enValue || ruValue || frValue || null;
  };

  // Function to get all available fields for a property
  const getAllLangFields = (field: string, item: ItemRead) => {
    const fields: { lang: string; value: any }[] = [];
    if (item.en?.[field as keyof typeof item.en]) {
      fields.push({ lang: 'EN', value: item.en[field as keyof typeof item.en] });
    }
    if (item.ru?.[field as keyof typeof item.ru]) {
      fields.push({ lang: 'RU', value: item.ru[field as keyof typeof item.ru] });
    }
    if (item.fr?.[field as keyof typeof item.fr]) {
      fields.push({ lang: 'FR', value: item.fr[field as keyof typeof item.fr] });
    }
    return fields;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {getFieldValue('title', data) || 'Item Detail'}
        </h1>
        <div className="flex gap-2">
          <Link href={`/items/edit/${id}`} className="btn btn-warning">
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card bg-base-100 shadow-xl">
          <figure className="h-80">
            <ItemImage image_id={data.image_id} size="large" />
          </figure>
        </div>
        
        <div className="space-y-4">
          <div className="card bg-base-100 shadow">
            <div className="card-body">
              <h2 className="card-title">Basic Information</h2>
              <div className="space-y-2">
                <div className="flex">
                  <span className="font-semibold w-32">Volume:</span>
                  <span>{data.vol ? `${data.vol} ml` : 'N/A'}</span>
                </div>
                <div className="flex">
                  <span className="font-semibold w-32">Price:</span>
                  <span>{data.price ? `€${data.price}` : 'N/A'}</span>
                </div>
                <div className="flex">
                  <span className="font-semibold w-32">Count:</span>
                  <span>{data.count || 'N/A'}</span>
                </div>
                <div className="flex">
                  <span className="font-semibold w-32">Category:</span>
                  <span>{data.category || 'N/A'}</span>
                </div>
                <div className="flex">
                  <span className="font-semibold w-32">Country:</span>
                  <span>{data.country || 'N/A'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Title fields */}
          {getAllLangFields('title', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Title</h2>
                {getAllLangFields('title', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Description fields */}
          {getAllLangFields('description', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Description</h2>
                {getAllLangFields('description', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Subtitle fields */}
          {getAllLangFields('subtitle', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Subtitle</h2>
                {getAllLangFields('subtitle', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendation fields */}
          {getAllLangFields('recommendation', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Recommendation</h2>
                {getAllLangFields('recommendation', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Made of fields */}
          {getAllLangFields('madeof', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Made Of</h2>
                {getAllLangFields('madeof', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alcohol fields */}
          {getAllLangFields('alc', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Alcohol</h2>
                {getAllLangFields('alc', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sugar fields */}
          {getAllLangFields('sugar', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Sugar</h2>
                {getAllLangFields('sugar', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Age fields */}
          {getAllLangFields('age', data).length > 0 && (
            <div className="card bg-base-100 shadow">
              <div className="card-body">
                <h2 className="card-title">Age</h2>
                {getAllLangFields('age', data).map(({ lang, value }) => (
                  <div key={lang} className="flex">
                    <span className="font-semibold w-16">{lang}:</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg">Confirm Delete</h3>
            <p className="py-4">Are you sure you want to delete this item?</p>
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