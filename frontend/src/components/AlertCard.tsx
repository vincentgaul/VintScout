import { useState } from 'react';
import type { Alert } from '../types';
import { getCurrencySymbol } from '../constants/currency';
import { useConditions } from '../hooks/useConditions';

interface AlertCardProps {
  alert: Alert;
  itemsCount?: number;
  showActions?: boolean;
  onToggleActive?: () => void;
  onDelete?: () => void;
  onViewItems?: () => void;
}

export default function AlertCard({
  alert,
  itemsCount,
  showActions = false,
  onToggleActive,
  onDelete,
  onViewItems
}: AlertCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusText = () => {
    if (!alert.is_active) return '❌ Inactive';
    if (!alert.last_checked_at) return '✅ Active (Creating Baseline)';
    return '✅ Active';
  };

  const hasPriceMin = alert.price_min !== undefined && alert.price_min !== null;
  const hasPriceMax = alert.price_max !== undefined && alert.price_max !== null;
  const currencySymbol = getCurrencySymbol(alert.currency);
  const conditions = useConditions();
  const conditionMap = conditions.reduce<Record<number, string>>((acc, condition) => {
    acc[condition.id] = condition.name;
    return acc;
  }, {});

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-start mb-3 gap-3">
        <div className="space-y-1">
          <p><strong>Alert Name:</strong> {alert.name}</p>
          {itemsCount !== undefined && (
            <p><strong>Items Found:</strong> {itemsCount}</p>
          )}
          <p><strong>Check Interval:</strong> {alert.check_interval_minutes} minutes</p>
          <p><strong>Status:</strong> {getStatusText()}</p>
          <p>
            <strong>Last Checked:</strong>{' '}
            {alert.last_checked_at ? new Date(alert.last_checked_at).toLocaleString() : '-'}
          </p>
        </div>
        <button
          className="border px-3 py-1 rounded text-sm bg-gray-100"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? '▼ Hide Details' : '▶ Show Details'}
        </button>
      </div>

      {isExpanded && (
        <>
          <p><strong>Country:</strong> {alert.country_code.toUpperCase()}</p>
      {alert.search_text && <p><strong>Search:</strong> {alert.search_text}</p>}
      {alert.catalog_names && (
        <p>
          <strong>Categories:</strong>{' '}
          {alert.catalog_ids
            ? alert.catalog_names.split(', ').map((name: string, i: number) => {
              const id = alert.catalog_ids?.split(',')[i];
              return id ? `${name} (ID: ${id})` : name;
            }).join(', ')
            : alert.catalog_names}
        </p>
      )}
      {alert.brand_names && (
        <p>
          <strong>Brands:</strong>{' '}
          {alert.brand_ids
            ? alert.brand_names.split(', ').map((name: string, i: number) => {
              const id = alert.brand_ids?.split(',')[i];
              return id ? `${name} (ID: ${id})` : name;
            }).join(', ')
            : alert.brand_names}
        </p>
      )}
      {alert.sizes && (
        <p>
          <strong>Sizes:</strong>{' '}
          {alert.sizes.split(',').map((sizeId: string) => sizeId.trim()).join(', ')}
        </p>
      )}
      {alert.conditions && (
        <p>
          <strong>Conditions:</strong>{' '}
          {alert.conditions.split(',').map((id: string) => {
            const key = parseInt(id.trim(), 10);
            return conditionMap[key] || id.trim();
          }).join(', ')}
        </p>
      )}
      {(hasPriceMin || hasPriceMax) && (
        <p>
          <strong>Price Range:</strong>{' '}
          {hasPriceMin ? `${currencySymbol}${alert.price_min}` : 'Any'} - {hasPriceMax ? `${currencySymbol}${alert.price_max}` : 'Any'}
          {' '}({alert.currency})
        </p>
      )}
        </>
      )}

      {showActions && (
        <div className="mt-4 pt-4 border-t flex flex-wrap gap-2">
          {onViewItems && (
            <button onClick={onViewItems} className="bg-blue-600 text-white px-3 py-1 rounded">
              View Items
            </button>
          )}
          {onToggleActive && (
            <button onClick={onToggleActive} className="bg-gray-200 px-3 py-1 rounded">
              {alert.is_active ? 'Deactivate' : 'Activate'}
            </button>
          )}
          {onDelete && (
            <button onClick={onDelete} className="bg-red-600 text-white px-3 py-1 rounded">
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  );
}
