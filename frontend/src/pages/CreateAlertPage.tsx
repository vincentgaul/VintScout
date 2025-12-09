import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CheckboxTree from 'react-checkbox-tree';
import 'react-checkbox-tree/lib/react-checkbox-tree.css';
import {
  FaCheckSquare,
  FaSquare,
  FaChevronRight,
  FaChevronDown,
  FaPlusSquare,
  FaMinusSquare,
  FaFolder,
  FaFolderOpen,
  FaFile
} from 'react-icons/fa';
import * as api from '../services/api';
import type { AlertCreate, Brand, Category } from '../types';
import { getCurrencyForCountry, getCurrencyLabel } from '../constants/currency';

// Helper to transform Category[] to CheckboxTree nodes
const transformCategoriesToNodes = (categories: Category[]): any[] => {
  return categories.map(cat => ({
    value: cat.id,
    label: `${cat.name} (ID: ${cat.vinted_id})`,
    children: cat.children && cat.children.length > 0
      ? transformCategoriesToNodes(cat.children)
      : undefined
  }));
};

// Helper to find category by ID (recursive)
const findCategoryById = (categories: Category[], id: string): Category | undefined => {
  for (const cat of categories) {
    if (cat.id === id) return cat;
    if (cat.children) {
      const found = findCategoryById(cat.children, id);
      if (found) return found;
    }
  }
  return undefined;
};

const DEFAULT_COUNTRY_CODE = 'fr';
const inputClass = 'w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200';
const selectClass = inputClass;

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

  // Brand search state
  const [brandQuery, setBrandQuery] = useState('');
  const [brandResults, setBrandResults] = useState<Brand[]>([]);
  const [selectedBrands, setSelectedBrands] = useState<Brand[]>([]);
  const [brandSearching, setBrandSearching] = useState(false);
  const [useBrandIds, setUseBrandIds] = useState(false);

  // Category Tree state
  const [treeCategories, setTreeCategories] = useState<Category[]>([]);
  const [loadingTree, setLoadingTree] = useState(false);
  const [checkedCategories, setCheckedCategories] = useState<string[]>([]);
  const [expandedCategories, setExpandedCategories] = useState<string[]>([]);
  const [useCategoryIds, setUseCategoryIds] = useState(false);

  // Fetch category tree when country changes
  useEffect(() => {
    const fetchCategories = async () => {
      setLoadingTree(true);
      try {
        const categories = await api.getCategories(formData.country_code);
        setTreeCategories(categories);
      } catch (error) {
        console.error('Failed to fetch category tree:', error);
        setTreeCategories([]);
      } finally {
        setLoadingTree(false);
      }
    };

    fetchCategories();
  }, [formData.country_code]);

  // Update formData when checked categories change
  useEffect(() => {
    if (treeCategories.length === 0) return;

    const selectedCats = checkedCategories
      .map(id => findCategoryById(treeCategories, id))
      .filter((c): c is Category => !!c);

    const catalogIds = selectedCats.map(c => c.vinted_id).join(',');
    const catalogNames = selectedCats.map(c => c.name).join(', ');

    setFormData(prev => ({
      ...prev,
      catalog_ids: catalogIds,
      catalog_names: catalogNames
    }));
  }, [checkedCategories, treeCategories]);

  // TEMPORARILY DISABLED - Fetch available sizes when categories change
  // Re-enable when size gender context issue is resolved
  /* useEffect(() => {
    const fetchSizes = async () => {
      if (!formData.catalog_ids || !formData.catalog_names) {
        setAvailableSizes([]);
        setSelectedSizes([]);
        return;
      }

      setLoadingSizes(true);
      try {
        const sizes = await api.getSizes(formData.catalog_ids, formData.catalog_names);
        setAvailableSizes(sizes);
        // Clear selected sizes if they're not in the new available sizes
        setSelectedSizes(prev => prev.filter(s => sizes.some(size => size.id === s.id)));
      } catch (error) {
        console.error('Failed to fetch sizes:', error);
        setAvailableSizes([]);
      } finally {
        setLoadingSizes(false);
      }
    };

    fetchSizes();
  }, [formData.catalog_ids, formData.catalog_names]); */

  // TEMPORARILY DISABLED - Update formData when selected sizes change
  /* useEffect(() => {
    const sizeIds = selectedSizes.map(s => s.id).join(',');
    setFormData(prev => ({
      ...prev,
      sizes: sizeIds || undefined
    }));
  }, [selectedSizes]); */

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

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold">Create New Alert</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
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

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span>Categories (Optional)</span>
              <label className="text-sm font-normal inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={useCategoryIds}
                  onChange={(e) => setUseCategoryIds(e.target.checked)}
                />
                Enter IDs
              </label>
            </div>

            {useCategoryIds ? (
              <div className="space-y-1">
                <input
                  type="text"
                  placeholder="Comma-separated category IDs (e.g., 1193,1920)"
                  value={formData.catalog_ids || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData(prev => ({
                      ...prev,
                      catalog_ids: value,
                      catalog_names: value ? `IDs: ${value}` : undefined
                    }));
                  }}
                  className={inputClass}
                />
                <small className="text-xs text-gray-500">Paste Vinted catalog IDs when you already know them.</small>
              </div>
            ) : (
              <div>
                {loadingTree ? (
                  <div className="text-sm text-gray-500 p-4 border rounded bg-gray-50 text-center">
                    Loading categories...
                  </div>
                ) : (
                  <div className="border rounded p-2 bg-white max-h-96 overflow-y-auto">
                    <CheckboxTree
                      nodes={transformCategoriesToNodes(treeCategories)}
                      checked={checkedCategories}
                      expanded={expandedCategories}
                      onCheck={(checked) => setCheckedCategories(checked as string[])}
                      onExpand={(expanded) => setExpandedCategories(expanded as string[])}
                      icons={{
                        check: <FaCheckSquare />,
                        uncheck: <FaSquare />,
                        halfCheck: <FaMinusSquare />,
                        expandClose: <FaChevronRight />,
                        expandOpen: <FaChevronDown />,
                        expandAll: <FaPlusSquare />,
                        collapseAll: <FaMinusSquare />,
                        parentClose: <FaFolder />,
                        parentOpen: <FaFolderOpen />,
                        leaf: <FaFile />
                      }}
                    />
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="space-y-2">
            <label>Price Min ({getCurrencyLabel(formData.currency)})</label>
            <input
              type="number"
              step="0.01"
              value={formData.price_min || ''}
              onChange={(e) => handleChange('price_min', e.target.value ? parseFloat(e.target.value) : undefined)}
              placeholder="0.00"
              className={inputClass}
            />
          </div>

          <div className="space-y-2">
            <label>Price Max ({getCurrencyLabel(formData.currency)})</label>
            <input
              type="number"
              step="0.01"
              value={formData.price_max || ''}
              onChange={(e) => handleChange('price_max', e.target.value ? parseFloat(e.target.value) : undefined)}
              placeholder="100.00"
              className={inputClass}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span>Brands (Optional)</span>
              <label className="text-sm font-normal inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={useBrandIds}
                  onChange={(e) => setUseBrandIds(e.target.checked)}
                />
                Enter IDs
              </label>
            </div>

            {useBrandIds ? (
              <div className="space-y-1">
                <input
                  type="text"
                  placeholder="Comma-separated brand IDs (e.g., 53,14)"
                  value={formData.brand_ids || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData(prev => ({
                      ...prev,
                      brand_ids: value,
                      brand_names: value ? `IDs: ${value}` : undefined
                    }));
                  }}
                  className={inputClass}
                />
                <small className="text-xs text-gray-500">Enter numeric brand IDs directly.</small>
              </div>
            ) : (
              <>
                {selectedBrands.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedBrands.map(brand => (
                      <span
                        key={brand.id}
                        className="inline-flex items-center bg-gray-200 rounded px-2 py-1 text-sm"
                      >
                        {brand.name} (ID: {brand.vinted_id})
                        <button
                          type="button"
                          onClick={() => handleRemoveBrand(brand.id)}
                          className="ml-2 text-gray-600 hover:text-gray-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                <div className="relative">
                  <input
                    type="text"
                    value={brandQuery}
                    onChange={(e) => handleBrandSearch(e.target.value)}
                    placeholder="Search brands (e.g., nike, zara, adidas)"
                    className={inputClass}
                  />

                  {brandSearching && <div>Searching...</div>}
                  {brandResults.length > 0 && (
                    <div className="absolute left-0 right-0 bg-white border rounded mt-1 max-h-52 overflow-y-auto z-10 shadow">
                      {brandResults.map(brand => (
                        <div
                          key={brand.id}
                          className="px-3 py-2 cursor-pointer border-b hover:bg-gray-50"
                          onClick={() => handleSelectBrand(brand)}
                        >
                          <strong>{brand.name} (ID: {brand.vinted_id})</strong>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {/* TEMPORARILY DISABLED - Size IDs vary by gender (men's 42 ≠ women's 42) */}
          {/* Size selection will be re-enabled once the gender context issue is resolved */}
          {/* {availableSizes.length > 0 && (
            <div className="space-y-2">
              <label>Sizes (Optional)</label>

              {loadingSizes && <div className="mb-2">Loading sizes...</div>}

              {selectedSizes.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {selectedSizes.map(size => (
                    <span
                      key={size.id}
                      className="inline-flex items-center bg-gray-200 rounded px-2 py-1 text-sm"
                    >
                      {size.name} (ID: {size.id})
                      <button
                        type="button"
                        onClick={() => setSelectedSizes(prev => prev.filter(s => s.id !== size.id))}
                        className="ml-2 text-gray-600 hover:text-gray-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}

              <select
                value=""
                onChange={(e) => {
                  const sizeId = e.target.value;
                  const size = availableSizes.find(s => s.id === sizeId);
                  if (size && !selectedSizes.find(s => s.id === size.id)) {
                    setSelectedSizes(prev => [...prev, size]);
                  }
                }}
                disabled={loadingSizes}
                className={selectClass}
              >
                <option value="">Select a size...</option>
                {availableSizes
                  .filter(size => !selectedSizes.find(s => s.id === size.id))
                  .map(size => (
                    <option key={size.id} value={size.id}>
                      {size.name}
                    </option>
                  ))
                }
              </select>
            </div>
          )} */}

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

          {error && <div className="text-red-600 text-sm">{error}</div>}

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
