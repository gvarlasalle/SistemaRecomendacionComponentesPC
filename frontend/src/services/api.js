// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Endpoints
export const chatAPI = {
  parse: (message) => api.post('/chat', { message }),
};

export const recommendAPI = {
  getRecommendation: (message, modelType = null) => {
    const payload = { message };
    // Solo incluir model_type si se especifica explícitamente
    if (modelType !== null) {
      payload.model_type = modelType;
    }
    return api.post('/recommend', payload);
  },
  
  compareModels: (message) => 
    api.post('/compare-models', { message }),
  
  byProfile: (profileId, componentType, modelType = 'rule', topK = 5) =>
    api.get(`/recommend/${profileId}/${componentType}`, {
      params: { model_type: modelType, top_k: topK }
    }),
};

export const profileAPI = {
  list: () => api.get('/profiles'),
  get: (profileId) => api.get(`/profiles/${profileId}`),
};

export const componentAPI = {
  list: (params) => api.get('/components', { params }),
  types: () => api.get('/components/types'),
};

export const validateAPI = {
  configuration: (components) => api.post('/validate', { components }),
};

export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;