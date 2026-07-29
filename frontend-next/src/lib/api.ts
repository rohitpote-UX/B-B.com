import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

const client = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT token to requests if available
client.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('bb_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

export const api = {
  auth: {
    signup: (data: { email: string; password: string; full_name?: string }) =>
      client.post('/auth/signup', data),
    login: (data: { email: string; password: string }) =>
      client.post('/auth/login', data),
    me: () => client.get('/auth/me'),
    updateProfile: (data: Record<string, unknown>) => client.put('/auth/me', data),
  },
  products: {
    list: (params?: Record<string, unknown>) => client.get('/products/', { params }),
    search: (q: string) => client.get('/products/search', { params: { q } }),
    getById: (id: number) => client.get(`/products/${id}`),
    getPrices: (id: number) => client.get(`/products/${id}/prices`),
    getPriceHistory: (id: number) => client.get(`/products/${id}/price-history`),
    getReviews: (id: number) => client.get(`/products/${id}/reviews`),
  },
  compare: {
    create: (productIds: number[]) =>
      client.post('/compare/', { product_ids: productIds }),
    get: (slug: string) => client.get(`/compare/${slug}`),
    trending: () => client.get('/compare/trending'),
    vote: (data: { comparison_id: number; product_id: number }) =>
      client.post('/compare/vote', data),
  },
  ai: {
    recommend: (data: Record<string, unknown>) => client.post('/ai/recommend', data),
    summarize: (data: Record<string, unknown>) => client.post('/ai/summarize', data),
    cartOptimize: (data: Record<string, unknown>) =>
      client.post('/ai/cart-optimize', data),
  },
  deals: {
    list: (params?: Record<string, unknown>) => client.get('/deals/', { params }),
    getById: (id: number) => client.get(`/deals/${id}`),
  },
  alerts: {
    create: (data: Record<string, unknown>) => client.post('/alerts/', data),
    list: () => client.get('/alerts/'),
    delete: (id: number) => client.delete(`/alerts/${id}`),
  },
  notifications: {
    list: () => client.get('/notifications/'),
    markRead: (id: number) => client.put(`/notifications/${id}/read`),
  },
}

export default api
