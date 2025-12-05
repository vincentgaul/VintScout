import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import * as api from '../services/api';
import type { Alert, ItemHistory } from '../types';
import AlertCard from '../components/AlertCard';

export default function AlertDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [items, setItems] = useState<ItemHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
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

      // If we got fewer items than requested, we know total
      if (itemsData.length < itemsPerPage) {
        setTotalItems(offset + itemsData.length);
      } else {
        // Estimate - we have at least this many
        setTotalItems(offset + itemsData.length + 1);
      }
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

      <AlertCard alert={alert} itemsCount={items.length} />

      <h2>Found Items</h2>

      {items.length === 0 ? (
        <div className="card">
          <p>No items found yet. The alert will check for new items every {alert.check_interval_minutes} minutes.</p>
        </div>
      ) : (
        <>
          <ul className="item-list">
            {items.map(item => (
              <li key={item.id} className="item-card">
                <h4>{item.title}</h4>
                <p><strong>Price:</strong> €{item.price.toFixed(2)}</p>
                <p><strong>Found:</strong> {new Date(item.found_at).toLocaleString()}</p>
                <p>
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    View on Vinted →
                  </a>
                </p>
              </li>
            ))}
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
