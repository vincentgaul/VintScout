import axios from 'axios';
import type { AuthResponse, Alert, AlertCreate, ItemHistory, Category, Brand } from '../types';

const api = axios.create({
  baseURL: '/api',
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (email: string, password: string) =>
  api.post<AuthResponse>('/auth/register', { email, password }).then(res => res.data);

export const login = (email: string, password: string) =>
  api.post<AuthResponse>('/auth/login', { email, password }).then(res => res.data);

// Alerts
export const getAlerts = () =>
  api.get<Alert[]>('/alerts').then(res => res.data);

export const getAlert = (id: string) =>
  api.get<Alert>(`/alerts/${id}`).then(res => res.data);

export const createAlert = (data: AlertCreate) =>
  api.post<Alert>('/alerts', data).then(res => res.data);

export const updateAlert = (id: string, data: Partial<AlertCreate>) =>
  api.put<Alert>(`/alerts/${id}`, data).then(res => res.data);

export const deleteAlert = (id: string) =>
  api.delete(`/alerts/${id}`);

// History
export const getHistory = (alertId: string, limit = 20, offset = 0) =>
  api.get<ItemHistory[]>('/history', { params: { alert_id: alertId, limit, offset } }).then(res => res.data);

// Categories
export const getCategories = (countryCode: string) =>
  api.get<Category[]>('/categories', { params: { country_code: countryCode } }).then(res => res.data);

export const searchCategories = (q: string, countryCode: string) =>
  api.get<Category[]>('/categories/search', { params: { q, country_code: countryCode } }).then(res => res.data);

// Brands
export const searchBrands = (q: string, countryCode: string) =>
  api.get<Brand[]>('/brands/search', { params: { q, country_code: countryCode } }).then(res => res.data);
