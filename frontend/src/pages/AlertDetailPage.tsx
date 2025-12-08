import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import * as api from '../services/api';
import type { Alert, ItemHistory } from '../types';
import AlertCard from '../components/AlertCard';
import { getCurrencySymbol } from '../constants/currency';

export default function AlertDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [items, setItems] = useState<ItemHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    if (id) {
      loadData();
    }
  }, [id, page]);

  const loadData = async () => {
    setLoading(true);
    try {
      const offset = (page - 1) * itemsPerPage;
      const [alertData, itemsData] = await Promise.all([
        api.getAlert(id!),
        api.getHistory(id!, itemsPerPage, offset)
      ]);
      setAlert(alertData);
      setItems(itemsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!alert) return <div>Alert not found</div>;

  return (
    <div>
      <Link to="/alerts">← Back to Alerts</Link>

      <AlertCard alert={alert} itemsCount={alert.total_found_count} />

      <h2>Found Items</h2>

      {items.length === 0 ? (
        <div className="card">
          <p>No items found yet. The alert will check for new items every {alert.check_interval_minutes} minutes.</p>
        </div>
      ) : (
        <>
          <ul className="item-list">
            {items.map(item => {
              const currencyCode = item.currency || alert.currency;
              const symbol = getCurrencySymbol(currencyCode);

              return (
                <li key={item.id} className="item-card">
                  <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                    {/* Thumbnail */}
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.title}
                        loading="lazy"
                        className="item-thumbnail"
                      />
                    ) : (
                      <div className="item-thumbnail-placeholder">
                        No Image
                      </div>
                    )}

                    {/* Item details */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h4 style={{ marginTop: 0 }}>{item.title}</h4>
                      {item.brand_name && <p><strong>Brand:</strong> {item.brand_name}</p>}
                      {item.size && <p><strong>Size:</strong> {item.size}</p>}
                      {item.condition && <p><strong>Condition:</strong> {item.condition}</p>}
                      <p>
                        <strong>Price:</strong>{' '}
                        {symbol}
                        {item.price.toFixed(2)} ({currencyCode})
                      </p>
                      <p><strong>Found:</strong> {new Date(item.found_at).toLocaleString()}</p>
                      <p>
                        <a href={item.url} target="_blank" rel="noopener noreferrer">
                          View on Vinted →
                        </a>
                      </p>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>

          <div className="pagination">
            <button
              onClick={() => setPage(p => p - 1)}
              disabled={page === 1}
            >
              ← Previous
            </button>
            <span>Page {page}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={items.length < itemsPerPage}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
