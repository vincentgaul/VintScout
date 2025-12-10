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
  const [runningNow, setRunningNow] = useState(false);
  const [runMessage, setRunMessage] = useState('');
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

  const handleRunNow = async () => {
    if (!id) return;

    setRunningNow(true);
    setRunMessage('');

    try {
      const result = await api.runAlertNow(id);

      if (result.success) {
        setRunMessage(`✓ Found ${result.new_items} new item${result.new_items !== 1 ? 's' : ''}!`);
        // Reload data to show new items
        await loadData();
      } else {
        setRunMessage(`✗ Error: ${result.error || 'Failed to run alert'}`);
      }
    } catch (err: any) {
      setRunMessage(`✗ Error: ${err.response?.data?.detail || 'Failed to run alert'}`);
    } finally {
      setRunningNow(false);
      // Clear message after 5 seconds
      setTimeout(() => setRunMessage(''), 5000);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-600 text-sm">{error}</div>;
  if (!alert) return <div>Alert not found</div>;

  return (
    <div className="space-y-4">
      <Link to="/alerts" className="text-blue-600">← Back to Alerts</Link>

      <AlertCard alert={alert} itemsCount={alert.total_found_count} />

      {/* Manual Run Button */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <button
            onClick={handleRunNow}
            disabled={runningNow}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {runningNow ? 'Running...' : 'Check Now'}
          </button>
          {runMessage && (
            <span className={`text-sm ${runMessage.startsWith('✓') ? 'text-green-600' : 'text-red-600'}`}>
              {runMessage}
            </span>
          )}
          {!runMessage && !runningNow && (
            <span className="text-sm text-gray-500">
              Manually trigger this alert to check for new items
            </span>
          )}
        </div>
      </div>

      <h2>Found Items</h2>

      {items.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-4">
          <p>No items found yet. The alert will check for new items every {alert.check_interval_minutes} minutes.</p>
        </div>
      ) : (
        <>
          <ul className="space-y-3">
            {items.map(item => {
              const currencyCode = item.currency || alert.currency;
              const symbol = getCurrencySymbol(currencyCode);

              return (
                <li key={item.id} className="bg-white rounded-lg shadow p-4">
                  <div className="flex gap-4 items-start">
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
                    <div className="flex-1 min-w-0 space-y-1">
                      <h4 className="text-lg font-semibold">{item.title}</h4>
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
                        <a className="text-blue-600" href={item.url} target="_blank" rel="noopener noreferrer">
                          View on Vinted →
                        </a>
                      </p>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>

          <div className="flex justify-center items-center gap-4 mt-6 bg-white p-4 rounded shadow">
            <button
              className="px-3 py-1 border rounded"
              onClick={() => setPage(p => p - 1)}
              disabled={page === 1}
            >
              ← Previous
            </button>
            <span className="font-medium">Page {page}</span>
            <button
              className="px-3 py-1 border rounded"
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
