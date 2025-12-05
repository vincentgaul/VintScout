import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../services/api';
import type { AlertCreate } from '../types';

export default function CreateAlertPage() {
  const [formData, setFormData] = useState<AlertCreate>({
    name: '',
    country_code: 'fr',
    search_text: '',
    brand_ids: '',
    catalog_ids: '',
    price_min: undefined,
    price_max: undefined,
    check_interval_minutes: 15,
    notification_config: { email: { enabled: false } }
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.createAlert(formData);
      navigate('/alerts');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create alert');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof AlertCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div>
      <h1>Create New Alert</h1>
      
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Alert Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="e.g., Nike Sneakers Alert"
              required
            />
          </div>

          <div className="form-group">
            <label>Country Code *</label>
            <select
              value={formData.country_code}
              onChange={(e) => handleChange('country_code', e.target.value)}
              required
            >
              <option value="fr">France (fr)</option>
              <option value="de">Germany (de)</option>
              <option value="es">Spain (es)</option>
              <option value="it">Italy (it)</option>
              <option value="be">Belgium (be)</option>
              <option value="nl">Netherlands (nl)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Search Text</label>
            <input
              type="text"
              value={formData.search_text}
              onChange={(e) => handleChange('search_text', e.target.value)}
              placeholder="e.g., Nike sneakers size 42"
            />
            <small>Tip: Include brand name in search (e.g., "Nike sneakers")</small>
          </div>

          <div className="form-group">
            <label>Category IDs</label>
            <input
              type="text"
              value={formData.catalog_ids}
              onChange={(e) => handleChange('catalog_ids', e.target.value)}
              placeholder="e.g., 16 or 16,17"
            />
            <small>Use category search to find IDs (comma-separated)</small>
          </div>

          <div className="form-group">
            <label>Price Min (€)</label>
            <input
              type="number"
              step="0.01"
              value={formData.price_min || ''}
              onChange={(e) => handleChange('price_min', e.target.value ? parseFloat(e.target.value) : undefined)}
              placeholder="0.00"
            />
          </div>

          <div className="form-group">
            <label>Price Max (€)</label>
            <input
              type="number"
              step="0.01"
              value={formData.price_max || ''}
              onChange={(e) => handleChange('price_max', e.target.value ? parseFloat(e.target.value) : undefined)}
              placeholder="100.00"
            />
          </div>

          <div className="form-group">
            <label>Brand IDs (Advanced - Optional)</label>
            <input
              type="text"
              value={formData.brand_ids}
              onChange={(e) => handleChange('brand_ids', e.target.value)}
              placeholder="e.g., 53,14 (Nike=53, Adidas=14)"
            />
            <small>Only if you know the brand IDs manually</small>
          </div>

          <div className="form-group">
            <label>Check Interval (minutes) *</label>
            <select
              value={formData.check_interval_minutes}
              onChange={(e) => handleChange('check_interval_minutes', parseInt(e.target.value))}
              required
            >
              <option value={5}>5 minutes</option>
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={60}>1 hour</option>
            </select>
          </div>

          {error && <div className="error">{error}</div>}
          
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Alert'}
          </button>
        </form>
      </div>
    </div>
  );
}
