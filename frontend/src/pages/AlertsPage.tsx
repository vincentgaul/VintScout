import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import * as api from '../services/api';
import type { Alert } from '../types';
import AlertCard from '../components/AlertCard';

export default function AlertsPage() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const data = await api.getAlerts();
      setAlerts(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this alert?')) return;

    try {
      await api.deleteAlert(id);
      setAlerts(alerts.filter(a => a.id !== id));
    } catch (err: any) {
      alert('Failed to delete alert');
    }
  };

  const handleToggleActive = async (alert: Alert) => {
    try {
      await api.updateAlert(alert.id, { ...alert, is_active: !alert.is_active });
      setAlerts(alerts.map(a => a.id === alert.id ? { ...a, is_active: !a.is_active } : a));
    } catch (err: any) {
      alert('Failed to update alert');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h1>My Alerts</h1>
      
      {alerts.length === 0 ? (
        <div className="card">
          <p>No alerts yet. <Link to="/alerts/new">Create your first alert</Link></p>
        </div>
      ) : (
        <div className="alert-list">
          {alerts.map(alert => (
            <AlertCard
              key={alert.id}
              alert={alert}
              itemsCount={alert.total_found_count}
              showActions={true}
              onViewItems={() => navigate(`/alerts/${alert.id}`)}
              onToggleActive={() => handleToggleActive(alert)}
              onDelete={() => handleDelete(alert.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
