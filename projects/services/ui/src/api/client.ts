import type { Order, OrderCreate, ProductListResponse } from '../types';

const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, options);
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: `HTTP ${resp.status}` }));
    throw new Error(error.detail || `HTTP ${resp.status}`);
  }
  return resp.json();
}

export const api = {
  getProducts: (page = 1, size = 50): Promise<ProductListResponse> =>
    request(`/products?page=${page}&size=${size}`),

  login: (email: string, password: string): Promise<{
    access_token: string;
    token_type: string;
    role: string;
    user_id: number;
    email: string;
  }> =>
    request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }),

  createOrder: (data: OrderCreate, idempotencyKey: string, token: string): Promise<Order> =>
    request('/orders', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotencyKey,
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }),

  getOrder: (id: number, token: string): Promise<Order> =>
    request(`/orders/${id}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    }),

  createProduct: (data: Record<string, unknown>, token: string) =>
    request('/products', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }),

  updateProduct: (id: number, data: Record<string, unknown>, token: string) =>
    request(`/products/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }),

  getStock: (productId: number, token: string): Promise<{
    product_id: number;
    available: number;
    reserved: number;
  }> =>
    request(`/stock/${productId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    }),
};