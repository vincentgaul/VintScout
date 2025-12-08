export const COUNTRY_CURRENCY: Record<string, string> = {
  at: 'EUR',
  be: 'EUR',
  cz: 'CZK',
  dk: 'DKK',
  ee: 'EUR',
  fi: 'EUR',
  fr: 'EUR',
  de: 'EUR',
  gr: 'EUR',
  hu: 'HUF',
  ie: 'EUR',
  it: 'EUR',
  lt: 'EUR',
  lv: 'EUR',
  lu: 'EUR',
  nl: 'EUR',
  pl: 'PLN',
  pt: 'EUR',
  ro: 'RON',
  se: 'SEK',
  sk: 'EUR',
  si: 'EUR',
  es: 'EUR',
  uk: 'GBP',
  hr: 'EUR'
};

const CURRENCY_SYMBOLS: Record<string, string> = {
  EUR: '€',
  GBP: '£',
  PLN: 'zł',
  CZK: 'Kč',
  SEK: 'kr',
  DKK: 'kr',
  HUF: 'Ft',
  RON: 'lei'
};

const DEFAULT_CURRENCY = 'EUR';

export const getCurrencyForCountry = (countryCode?: string) => {
  if (!countryCode) return DEFAULT_CURRENCY;
  return COUNTRY_CURRENCY[countryCode.toLowerCase()] ?? DEFAULT_CURRENCY;
};

export const getCurrencySymbol = (currency?: string) => {
  if (!currency) return DEFAULT_CURRENCY;
  return CURRENCY_SYMBOLS[currency] ?? currency;
};

export const getCurrencyLabel = (currency?: string) => {
  const symbol = getCurrencySymbol(currency);
  const upper = currency?.toUpperCase() ?? DEFAULT_CURRENCY;
  return symbol && symbol !== upper ? `${symbol} (${upper})` : upper;
};
