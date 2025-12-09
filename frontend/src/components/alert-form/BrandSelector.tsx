import { useState } from 'react';
import type { Brand } from '../../types';
import * as api from '../../services/api';

interface BrandSelectorProps {
  countryCode: string;
  useBrandIds: boolean;
  onUseBrandIdsChange: (value: boolean) => void;
  brandIds: string;
  onBrandIdsChange: (brandIds: string, brandNames: string | undefined) => void;
  inputClass: string;
}

export function BrandSelector({
  countryCode,
  useBrandIds,
  onUseBrandIdsChange,
  brandIds,
  onBrandIdsChange,
  inputClass
}: BrandSelectorProps) {
  const [brandQuery, setBrandQuery] = useState('');
  const [brandResults, setBrandResults] = useState<Brand[]>([]);
  const [selectedBrands, setSelectedBrands] = useState<Brand[]>([]);
  const [brandSearching, setBrandSearching] = useState(false);

  const handleBrandSearch = async (query: string) => {
    setBrandQuery(query);

    if (query.length < 2) {
      setBrandResults([]);
      return;
    }

    setBrandSearching(true);
    try {
      const results = await api.searchBrands(query, countryCode);
      setBrandResults(results);
    } catch (err) {
      console.error('Brand search failed:', err);
      setBrandResults([]);
    } finally {
      setBrandSearching(false);
    }
  };

  const handleSelectBrand = (brand: Brand) => {
    if (!selectedBrands.find(b => b.id === brand.id)) {
      const newBrands = [...selectedBrands, brand];
      setSelectedBrands(newBrands);

      const ids = newBrands.map(b => b.vinted_id).join(',');
      const names = newBrands.map(b => b.name).join(', ');
      onBrandIdsChange(ids, names);
    }

    setBrandQuery('');
    setBrandResults([]);
  };

  const handleRemoveBrand = (brandId: string) => {
    const newBrands = selectedBrands.filter(b => b.id !== brandId);
    setSelectedBrands(newBrands);

    const ids = newBrands.map(b => b.vinted_id).join(',');
    const names = newBrands.map(b => b.name).join(', ');
    onBrandIdsChange(ids, names || undefined);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span>Brands (Optional)</span>
        <label className="text-sm font-normal inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={useBrandIds}
            onChange={(e) => onUseBrandIdsChange(e.target.checked)}
          />
          Enter IDs
        </label>
      </div>

      {useBrandIds ? (
        <div className="space-y-1">
          <input
            type="text"
            placeholder="Comma-separated brand IDs (e.g., 53,14)"
            value={brandIds || ''}
            onChange={(e) => {
              const value = e.target.value;
              onBrandIdsChange(value, value ? `IDs: ${value}` : undefined);
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
  );
}
