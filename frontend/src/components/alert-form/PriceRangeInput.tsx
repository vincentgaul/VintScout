import { getCurrencyLabel } from '../../constants/currency';

interface PriceRangeInputProps {
  currency: string;
  priceMin: number | undefined;
  priceMax: number | undefined;
  onPriceMinChange: (value: number | undefined) => void;
  onPriceMaxChange: (value: number | undefined) => void;
  inputClass: string;
}

export function PriceRangeInput({
  currency,
  priceMin,
  priceMax,
  onPriceMinChange,
  onPriceMaxChange,
  inputClass
}: PriceRangeInputProps) {
  return (
    <>
      <div className="space-y-2">
        <label>Price Min ({getCurrencyLabel(currency)})</label>
        <input
          type="number"
          step="0.01"
          value={priceMin || ''}
          onChange={(e) => onPriceMinChange(e.target.value ? parseFloat(e.target.value) : undefined)}
          placeholder="0.00"
          className={inputClass}
        />
      </div>

      <div className="space-y-2">
        <label>Price Max ({getCurrencyLabel(currency)})</label>
        <input
          type="number"
          step="0.01"
          value={priceMax || ''}
          onChange={(e) => onPriceMaxChange(e.target.value ? parseFloat(e.target.value) : undefined)}
          placeholder="100.00"
          className={inputClass}
        />
      </div>
    </>
  );
}
