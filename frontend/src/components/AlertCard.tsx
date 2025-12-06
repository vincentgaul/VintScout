import type { Alert } from '../types';

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
  const getStatusText = () => {
    if (!alert.is_active) return '❌ Inactive';
    if (!alert.last_checked_at) return '✅ Active (Creating Baseline)';
    return '✅ Active';
  };

  return (
    <div className="card">
      <p><strong>Alert Name:</strong> {alert.name}</p>
      {itemsCount !== undefined && (
        <p><strong>Items Found:</strong> {itemsCount}</p>
      )}
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
      {alert.price_min !== undefined && alert.price_max !== undefined && (
        <p><strong>Price Range:</strong> €{alert.price_min} - €{alert.price_max}</p>
      )}
      <p><strong>Check Interval:</strong> {alert.check_interval_minutes} minutes</p>
      <p><strong>Status:</strong> {getStatusText()}</p>
      <p>
        <strong>Last Checked:</strong>{' '}
        {alert.last_checked_at ? new Date(alert.last_checked_at).toLocaleString() : '-'}
      </p>

      {showActions && (
        <div className="actions">
          {onViewItems && (
            <button onClick={onViewItems}>View Items</button>
          )}
          {onToggleActive && (
            <button onClick={onToggleActive}>
              {alert.is_active ? 'Deactivate' : 'Activate'}
            </button>
          )}
          {onDelete && (
            <button onClick={onDelete} style={{ background: '#dc3545' }}>
              Delete
            </button>
          )}
        </div>
      )}
    </div>
  );
}
