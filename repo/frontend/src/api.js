import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  console.log('🔑 API Request Debug:', {
    url: config.url,
    method: config.method,
    hasToken: !!token,
    tokenPrefix: token ? token.substring(0, 20) + '...' : 'No token',
    headers: config.headers
  });
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else {
    console.warn('⚠️ No authentication token found in localStorage');
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add response interceptor to log responses and handle auth errors
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      url: response.config.url,
      status: response.status,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('❌ API Error:', {
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    });
    
    // If unauthorized, redirect to login
    if (error.response?.status === 401) {
      console.warn('🚪 Unauthorized - redirecting to login');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userRole');
      window.location.reload();
    }
    
    return Promise.reject(error);
  }
);

export default apiClient; 