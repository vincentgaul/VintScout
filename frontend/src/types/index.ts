export interface User {
  id: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Alert {
  id: string;
  name: string;
  country_code: string;
  search_text?: string;
  brand_ids?: string;
  brand_names?: string;
  catalog_ids?: string;
  catalog_names?: string;
  sizes?: string;
  price_min?: number;
  price_max?: number;
  check_interval_minutes: number;
  notification_config: Record<string, any>;
  last_checked_at?: string;
  last_found_count: number;
  total_found_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertCreate {
  name: string;
  country_code: string;
  search_text?: string;
  brand_ids?: string;
  brand_names?: string;
  catalog_ids?: string;
  catalog_names?: string;
  sizes?: string;
  price_min?: number;
  price_max?: number;
  check_interval_minutes: number;
  notification_config?: Record<string, any>;
  is_active?: boolean;
}

export interface ItemHistory {
  id: string;
  alert_id: string;
  item_id: string;
  title: string;
  url: string;
  image_url?: string;
  brand_name?: string;
  size?: string;
  condition?: string;
  price: number;
  found_at: string;
}

export interface Category {
  id: string;
  vinted_id: string;
  name: string;
  parent_id?: string;
  children?: Category[];
}

export interface Brand {
  id: string;
  vinted_id: string;
  name: string;
}

export interface Size {
  id: string;
  name: string;
}
