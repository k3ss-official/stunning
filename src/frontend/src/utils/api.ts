import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const authAPI = {
  login: (username: string, password: string) => 
    api.post('/token', new URLSearchParams({ username, password })),
  getMe: () => api.get('/users/me'),
};

export const clientsAPI = {
  getAll: () => api.get('/clients/'),
  getById: (id: number) => api.get(`/clients/${id}`),
  create: (data: any) => api.post('/clients/', data),
  update: (id: number, data: any) => api.put(`/clients/${id}`, data),
  delete: (id: number) => api.delete(`/clients/${id}`),
};

export const modelsAPI = {
  getAll: (clientId?: number) => api.get('/models/', { params: { client_id: clientId } }),
  getById: (id: number) => api.get(`/models/${id}`),
  create: (formData: FormData) => api.post('/models/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  delete: (id: number) => api.delete(`/models/${id}`),
};

export const layersAPI = {
  getAll: (type?: string) => api.get('/layers/', { params: { type } }),
  getById: (id: number) => api.get(`/layers/${id}`),
  create: (formData: FormData) => api.post('/layers/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  delete: (id: number) => api.delete(`/layers/${id}`),
};

export const generationAPI = {
  generate: (data: any) => api.post('/generate/', data),
  inpaint: (formData: FormData) => api.post('/inpaint/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
};

export const historyAPI = {
  getAll: (modelId?: number) => api.get('/histories/', { params: { model_id: modelId } }),
  getById: (id: number) => api.get(`/histories/${id}`),
};

export const lookbooksAPI = {
  getAll: (clientId?: number) => api.get('/lookbooks/', { params: { client_id: clientId } }),
  getById: (id: number) => api.get(`/lookbooks/${id}`),
  create: (data: any) => api.post('/lookbooks/', data),
  getEntries: (lookbookId: number) => api.get(`/lookbooks/${lookbookId}/entries/`),
  addEntry: (lookbookId: number, data: any) => api.post(`/lookbooks/${lookbookId}/entries/`, data),
};

export default api;
