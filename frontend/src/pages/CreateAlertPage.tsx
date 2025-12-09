import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../services/api';
import type { AlertCreate } from '../types';
import { getCurrencyForCountry } from '../constants/currency';
import { inputClass, selectClass, DEFAULT_COUNTRY_CODE } from '../constants/formStyles';
import {
  BrandSelector,
  CategorySelector,
  ConditionSelector,
  PriceRangeInput
} from '../components/alert-form';

export default function CreateAlertPage() {
  const defaultCurrency = getCurrencyForCountry(DEFAULT_COUNTRY_CODE);
  const [formData, setFormData] = useState<AlertCreate>({
    name: '',
    country_code: DEFAULT_COUNTRY_CODE,
    search_text: '',
    brand_ids: '',
    catalog_ids: '',
    price_min: undefined,
    price_max: undefined,
    currency: defaultCurrency,
    check_interval_minutes: 15,
    notification_config: { telegram: { enabled: true } }
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Toggle states for manual ID entry
  const [useBrandIds, setUseBrandIds] = useState(false);
  const [useCategoryIds, setUseCategoryIds] = useState(false);
  const [useConditionIds, setUseConditionIds] = useState(false);
  const [sizeIdsInput, setSizeIdsInput] = useState('');

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
    setFormData(prev => {
      const updated = { ...prev, [field]: value };
      if (field === 'country_code') {
        updated.currency = getCurrencyForCountry(value);
      }
      return updated;
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">Create New Alert</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Alert Name */}
          <div className="space-y-2">
            <label>Alert Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="e.g., Nike Sneakers Alert"
              required
              className={inputClass}
            />
          </div>

          {/* Country Selector */}
          <div className="space-y-2">
            <label>Country Code *</label>
            <select
              value={formData.country_code}
              onChange={(e) => handleChange('country_code', e.target.value)}
              required
              className={selectClass}
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

          {/* Search Text */}
          <div className="space-y-2">
            <label>Search Text</label>
            <input
              type="text"
              value={formData.search_text}
              onChange={(e) => handleChange('search_text', e.target.value)}
              placeholder="e.g., Nike sneakers size 42"
              className={inputClass}
            />
          </div>

          {/* Category Selector */}
          <CategorySelector
            countryCode={formData.country_code}
            useCategoryIds={useCategoryIds}
            onUseCategoryIdsChange={setUseCategoryIds}
            catalogIds={formData.catalog_ids || ''}
            onCatalogChange={(ids, names) => {
              setFormData(prev => ({
                ...prev,
                catalog_ids: ids,
                catalog_names: names
              }));
            }}
            inputClass={inputClass}
          />

          {/* Condition Selector */}
          <ConditionSelector
            conditions={formData.conditions}
            useConditionIds={useConditionIds}
            onUseConditionIdsChange={setUseConditionIds}
            onConditionsChange={(value) => handleChange('conditions', value)}
            inputClass={inputClass}
          />

          {/* Price Range */}
          <PriceRangeInput
            currency={formData.currency}
            priceMin={formData.price_min}
            priceMax={formData.price_max}
            onPriceMinChange={(value) => handleChange('price_min', value)}
            onPriceMaxChange={(value) => handleChange('price_max', value)}
            inputClass={inputClass}
          />

          {/* Brand Selector */}
          <BrandSelector
            countryCode={formData.country_code}
            useBrandIds={useBrandIds}
            onUseBrandIdsChange={setUseBrandIds}
            brandIds={formData.brand_ids || ''}
            onBrandIdsChange={(ids, names) => {
              setFormData(prev => ({
                ...prev,
                brand_ids: ids,
                brand_names: names
              }));
            }}
            inputClass={inputClass}
          />

          {/* Size Input */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-gray-500">
              <span>Sizes (Optional)</span>
              <label className="text-sm font-normal inline-flex items-center gap-2">
                <input type="checkbox" checked readOnly className="opacity-60" />
                Enter IDs (IDs only for now)
              </label>
            </div>
            <input
              type="text"
              placeholder="Comma-separated size IDs (e.g., 2100,2101)"
              value={sizeIdsInput}
              onChange={(e) => {
                const value = e.target.value;
                setSizeIdsInput(value);
                handleChange('sizes', value || undefined);
              }}
              className={inputClass}
            />
            <small className="text-xs text-gray-500">Size lookups are incomplete, so enter ids directly for now.</small>
          </div>

          {/* Check Interval */}
          <div className="space-y-2">
            <label>Check Interval (minutes) *</label>
            <select
              value={formData.check_interval_minutes}
              onChange={(e) => handleChange('check_interval_minutes', parseInt(e.target.value))}
              required
              className={selectClass}
            >
              <option value={1}>1 minute</option>
              <option value={5}>5 minutes</option>
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={60}>1 hour</option>
            </select>
          </div>

          {/* Error Message */}
          {error && <div className="text-red-600 text-sm">{error}</div>}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded disabled:bg-gray-400"
          >
            {loading ? 'Creating...' : 'Create Alert'}
          </button>
        </form>
      </div>
    </div>
  );
}
