import axios from 'axios';

// Get API URL from environment
const API_URL = import.meta.env.VITE_API_URL;

if (!API_URL) {
  console.error('VITE_API_URL environment variable is not set');
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log requests in development only
    if (import.meta.env.DEV) {
      console.log(`${config.method.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Log responses in development only
    if (import.meta.env.DEV) {
      console.log(`${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      if (error.response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
      
      // Log errors in development
      if (import.meta.env.DEV) {
        console.error('API Error:', {
          status: error.response.status,
          url: error.config?.url,
          data: error.response.data
        });
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error - No response received');
    } else {
      // Request setup error
      console.error('Request Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;