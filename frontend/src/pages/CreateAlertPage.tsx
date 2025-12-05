import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../services/api';
import type { AlertCreate, Brand, Category } from '../types';

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

  // Brand search state
  const [brandQuery, setBrandQuery] = useState('');
  const [brandResults, setBrandResults] = useState<Brand[]>([]);
  const [selectedBrands, setSelectedBrands] = useState<Brand[]>([]);
  const [brandSearching, setBrandSearching] = useState(false);

  // Category search state
  const [categoryQuery, setCategoryQuery] = useState('');
  const [categoryResults, setCategoryResults] = useState<Category[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<Category[]>([]);
  const [categorySearching, setCategorySearching] = useState(false);

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

  const handleBrandSearch = async (query: string) => {
    setBrandQuery(query);

    if (query.length < 2) {
      setBrandResults([]);
      return;
    }

    setBrandSearching(true);
    try {
      const results = await api.searchBrands(query, formData.country_code);
      setBrandResults(results);
    } catch (err) {
      console.error('Brand search failed:', err);
      setBrandResults([]);
    } finally {
      setBrandSearching(false);
    }
  };

  const handleSelectBrand = (brand: Brand) => {
    // Add brand if not already selected
    if (!selectedBrands.find(b => b.id === brand.id)) {
      const newBrands = [...selectedBrands, brand];
      setSelectedBrands(newBrands);

      // Update formData with brand IDs and names
      const brandIds = newBrands.map(b => b.vinted_id).join(',');
      const brandNames = newBrands.map(b => b.name).join(', ');
      setFormData(prev => ({
        ...prev,
        brand_ids: brandIds,
        brand_names: brandNames
      }));
    }

    // Clear search
    setBrandQuery('');
    setBrandResults([]);
  };

  const handleRemoveBrand = (brandId: string) => {
    const newBrands = selectedBrands.filter(b => b.id !== brandId);
    setSelectedBrands(newBrands);

    // Update formData
    const brandIds = newBrands.map(b => b.vinted_id).join(',');
    const brandNames = newBrands.map(b => b.name).join(', ');
    setFormData(prev => ({
      ...prev,
      brand_ids: brandIds,
      brand_names: brandNames
    }));
  };

  const handleCategorySearch = async (query: string) => {
    setCategoryQuery(query);

    if (query.length < 2) {
      setCategoryResults([]);
      return;
    }

    setCategorySearching(true);
    try {
      const results = await api.searchCategories(query, formData.country_code);
      setCategoryResults(results);
    } catch (err) {
      console.error('Category search failed:', err);
      setCategoryResults([]);
    } finally {
      setCategorySearching(false);
    }
  };

  const handleSelectCategory = (category: Category) => {
    // Add category if not already selected
    if (!selectedCategories.find(c => c.id === category.id)) {
      const newCategories = [...selectedCategories, category];
      setSelectedCategories(newCategories);

      // Update formData with category IDs and names
      const catalogIds = newCategories.map(c => c.vinted_id).join(',');
      const catalogNames = newCategories.map(c => c.name).join(', ');
      setFormData(prev => ({
        ...prev,
        catalog_ids: catalogIds,
        catalog_names: catalogNames
      }));
    }

    // Clear search
    setCategoryQuery('');
    setCategoryResults([]);
  };

  const handleRemoveCategory = (categoryId: string) => {
    const newCategories = selectedCategories.filter(c => c.id !== categoryId);
    setSelectedCategories(newCategories);

    // Update formData
    const catalogIds = newCategories.map(c => c.vinted_id).join(',');
    const catalogNames = newCategories.map(c => c.name).join(', ');
    setFormData(prev => ({
      ...prev,
      catalog_ids: catalogIds,
      catalog_names: catalogNames
    }));
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
              <option value="at">Austria (vinted.at)</option>
              <option value="be">Belgium (vinted.be)</option>
              <option value="hr">Croatia (vinted.hr)</option>
              <option value="cz">Czech Republic (vinted.cz)</option>
              <option value="dk">Denmark (vinted.dk)</option>
              <option value="ee">Estonia (vinted.ee)</option>
              <option value="fi">Finland (vinted.fi)</option>
              <option value="fr">France (vinted.fr)</option>
              <option value="de">Germany (vinted.de)</option>
              <option value="gr">Greece (vinted.gr)</option>
              <option value="hu">Hungary (vinted.hu)</option>
              <option value="ie">Ireland (vinted.ie)</option>
              <option value="it">Italy (vinted.it)</option>
              <option value="lv">Latvia (vinted.lv)</option>
              <option value="lt">Lithuania (vinted.lt)</option>
              <option value="lu">Luxembourg (vinted.lu)</option>
              <option value="nl">Netherlands (vinted.nl)</option>
              <option value="pl">Poland (vinted.pl)</option>
              <option value="pt">Portugal (vinted.pt)</option>
              <option value="ro">Romania (vinted.ro)</option>
              <option value="sk">Slovakia (vinted.sk)</option>
              <option value="si">Slovenia (vinted.si)</option>
              <option value="es">Spain (vinted.es)</option>
              <option value="se">Sweden (vinted.se)</option>
              <option value="uk">UK (vinted.co.uk)</option>
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
            <label>Categories (Optional)</label>

            {/* Selected categories */}
            {selectedCategories.length > 0 && (
              <div style={{ marginBottom: '10px' }}>
                {selectedCategories.map(category => (
                  <span
                    key={category.id}
                    style={{
                      display: 'inline-block',
                      background: '#e0e0e0',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      marginRight: '8px',
                      marginBottom: '8px'
                    }}
                  >
                    {category.name}
                    <button
                      type="button"
                      onClick={() => handleRemoveCategory(category.id)}
                      style={{
                        marginLeft: '8px',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        padding: 0,
                        color: '#666'
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* Category search input */}
            <input
              type="text"
              value={categoryQuery}
              onChange={(e) => handleCategorySearch(e.target.value)}
              placeholder="Search categories (e.g., shoes, hats, dresses)"
            />
            <small>Type to search for categories by name</small>

            {/* Category search results */}
            {categorySearching && <div>Searching...</div>}
            {categoryResults.length > 0 && (
              <div style={{
                position: 'absolute',
                background: 'white',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginTop: '4px',
                maxHeight: '200px',
                overflowY: 'auto',
                zIndex: 1000,
                width: 'calc(100% - 40px)'
              }}>
                {categoryResults.map(category => (
                  <div
                    key={category.id}
                    onClick={() => handleSelectCategory(category)}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      borderBottom: '1px solid #eee'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#f5f5f5'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                  >
                    <strong>{category.name}</strong>
                    <span style={{ fontSize: '0.8em', color: '#666', marginLeft: '8px' }}>
                      (ID: {category.vinted_id})
                    </span>
                  </div>
                ))}
              </div>
            )}
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
            <label>Brands (Optional)</label>

            {/* Selected brands */}
            {selectedBrands.length > 0 && (
              <div style={{ marginBottom: '10px' }}>
                {selectedBrands.map(brand => (
                  <span
                    key={brand.id}
                    style={{
                      display: 'inline-block',
                      background: '#e0e0e0',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      marginRight: '8px',
                      marginBottom: '8px'
                    }}
                  >
                    {brand.name}
                    <button
                      type="button"
                      onClick={() => handleRemoveBrand(brand.id)}
                      style={{
                        marginLeft: '8px',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        padding: 0,
                        color: '#666'
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* Brand search input */}
            <input
              type="text"
              value={brandQuery}
              onChange={(e) => handleBrandSearch(e.target.value)}
              placeholder="Search brands (e.g., nike, zara, adidas)"
            />
            <small>Type to search for brands by name</small>

            {/* Brand search results */}
            {brandSearching && <div>Searching...</div>}
            {brandResults.length > 0 && (
              <div style={{
                position: 'absolute',
                background: 'white',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginTop: '4px',
                maxHeight: '200px',
                overflowY: 'auto',
                zIndex: 1000,
                width: 'calc(100% - 40px)'
              }}>
                {brandResults.map(brand => (
                  <div
                    key={brand.id}
                    onClick={() => handleSelectBrand(brand)}
                    style={{
                      padding: '8px 12px',
                      cursor: 'pointer',
                      borderBottom: '1px solid #eee'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#f5f5f5'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                  >
                    <strong>{brand.name}</strong>
                  </div>
                ))}
              </div>
            )}
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
