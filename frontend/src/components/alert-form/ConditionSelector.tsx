import { useState, useEffect } from 'react';
import { useConditions } from '../../hooks/useConditions';

interface ConditionSelectorProps {
  conditions: string | undefined;
  useConditionIds: boolean;
  onUseConditionIdsChange: (value: boolean) => void;
  onConditionsChange: (value: string | undefined) => void;
  inputClass: string;
}

export function ConditionSelector({
  conditions,
  useConditionIds,
  onUseConditionIdsChange,
  onConditionsChange,
  inputClass
}: ConditionSelectorProps) {
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);
  const [conditionIdsInput, setConditionIdsInput] = useState('');
  const conditionOptions = useConditions();

  useEffect(() => {
    if (!useConditionIds && conditions) {
      const ids = conditions.split(',').map(id => id.trim()).filter(Boolean);
      const known = ids.filter(id => conditionOptions.some(opt => opt.id.toString() === id));
      setSelectedConditions(known);
    }
  }, [conditions, useConditionIds, conditionOptions]);

  const handleToggleCondition = (conditionId: string) => {
    setSelectedConditions(prev => {
      const next = prev.includes(conditionId)
        ? prev.filter(x => x !== conditionId)
        : [...prev, conditionId];
      onConditionsChange(next.length ? next.join(',') : undefined);
      return next;
    });
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span>Conditions (Optional)</span>
        <label className="text-sm font-normal inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={useConditionIds}
            onChange={(e) => {
              const checked = e.target.checked;
              onUseConditionIdsChange(checked);
              if (checked) {
                setConditionIdsInput(conditions || selectedConditions.join(','));
              } else {
                const ids = (conditions || '').split(',').map(id => id.trim()).filter(Boolean);
                setSelectedConditions(ids.filter(id => conditionOptions.some(opt => opt.id.toString() === id)));
              }
            }}
          />
          Enter IDs
        </label>
      </div>

      {useConditionIds ? (
        <div className="space-y-1">
          <input
            type="text"
            placeholder="Comma-separated condition IDs (e.g., 1,2)"
            value={conditionIdsInput}
            onChange={(e) => {
              const value = e.target.value;
              setConditionIdsInput(value);
              onConditionsChange(value || undefined);
            }}
            className={inputClass}
          />
          <small className="text-xs text-gray-500">Use numeric IDs to match Vinted statuses.</small>
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          {conditionOptions.length === 0 ? (
            <div className="text-sm text-gray-500">Loading conditions…</div>
          ) : (
            conditionOptions.map(option => {
              const checked = selectedConditions.includes(option.id.toString());
              return (
                <button
                  type="button"
                  key={option.id}
                  className={`px-3 py-1 rounded border text-sm ${
                    checked
                      ? 'bg-blue-100 border-blue-400 text-blue-700'
                      : 'bg-white border-gray-300 text-gray-700'
                  }`}
                  onClick={() => handleToggleCondition(option.id.toString())}
                >
                  {option.name}
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
