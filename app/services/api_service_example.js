/**
 * SANA API Service — paste this into your React frontend:
 * src/services/api.js
 *
 * Usage:
 *   import api from './services/api'
 *   const products = await api.getProducts({ occasion: 'Wedding' })
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

// ── Token helpers ─────────────────────────────────────────────────────────────
const getToken  = () => localStorage.getItem('access_token')
const setTokens = (access, refresh) => {
  localStorage.setItem('access_token', access)
  if (refresh) localStorage.setItem('refresh_token', refresh)
}
const clearTokens = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// ── Base fetch wrapper ────────────────────────────────────────────────────────
async function request(path, options = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  const data = await res.json()

  if (!res.ok) throw new Error(data.message || 'Request failed')
  return data
}

// ── Auth ──────────────────────────────────────────────────────────────────────
const auth = {
  register: async (payload) => {
    const data = await request('/auth/register', { method: 'POST', body: JSON.stringify(payload) })
    setTokens(data.data.access_token, data.data.refresh_token)
    return data
  },
  login: async (email, password) => {
    const data = await request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
    setTokens(data.data.access_token, data.data.refresh_token)
    return data
  },
  adminLogin: async (username, password) => {
    const data = await request('/auth/admin/login', { method: 'POST', body: JSON.stringify({ username, password }) })
    setTokens(data.data.access_token, data.data.refresh_token)
    return data
  },
  logout: () => clearTokens(),
  getProfile: () => request('/auth/me'),
  updateProfile: (payload) => request('/auth/me', { method: 'PATCH', body: JSON.stringify(payload) }),
}

// ── Products ──────────────────────────────────────────────────────────────────
const products = {
  getAll: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/products${qs ? '?' + qs : ''}`)
  },
  getById:  (id) => request(`/products/${id}`),
  getFilters: ()  => request('/products/filters'),
  create: (formData) =>
    fetch(`${BASE_URL}/products`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: formData,   // FormData for image upload
    }).then(r => r.json()),
  update: (id, payload) => request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  delete: (id) => request(`/products/${id}`, { method: 'DELETE' }),
}

// ── Orders ────────────────────────────────────────────────────────────────────
const orders = {
  place: (payload) => request('/orders', { method: 'POST', body: JSON.stringify(payload) }),
  track: (orderNumber) => request(`/orders/track/${orderNumber}`),
  myOrders: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/orders/my${qs ? '?' + qs : ''}`)
  },
  // Admin
  getAll: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/orders${qs ? '?' + qs : ''}`)
  },
  updateStatus: (id, status) =>
    request(`/orders/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  delete: (id) => request(`/orders/${id}`, { method: 'DELETE' }),
}

// ── Admin ─────────────────────────────────────────────────────────────────────
const admin = {
  getDashboard: () => request('/admin/dashboard'),
  getUsers:     (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/admin/users${qs ? '?' + qs : ''}`)
  },
  toggleUser: (id) => request(`/admin/users/${id}/toggle`, { method: 'PATCH' }),
  deleteUser: (id) => request(`/admin/users/${id}`, { method: 'DELETE' }),
}

// ── Upload ────────────────────────────────────────────────────────────────────
const upload = {
  image: (file, folder = 'products') => {
    const form = new FormData()
    form.append('file', file)
    return fetch(`${BASE_URL}/upload/image?folder=${folder}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: form,
    }).then(r => r.json())
  },
}

// ── WhatsApp ──────────────────────────────────────────────────────────────────
const whatsapp = {
  send: (to, message) =>
    request('/whatsapp/send', { method: 'POST', body: JSON.stringify({ to, message }) }),
}

const api = { auth, products, orders, admin, upload, whatsapp }
export default api
