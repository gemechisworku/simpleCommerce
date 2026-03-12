import axios, { AxiosError } from 'axios';
import { API_BASE_URL, TOKEN_KEY, REFRESH_TOKEN_KEY } from '../constants/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // FormData must be sent with multipart/form-data and boundary; let the browser set Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as typeof error.config & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (refreshToken) {
        try {
          const { data } = await axios.post<{ data: { access_token: string; refresh_token?: string } }>(
            `${API_BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          const newAccessToken = data.data.access_token;
          const newRefreshToken = data.data.refresh_token;
          localStorage.setItem(TOKEN_KEY, newAccessToken);
          if (newRefreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          }
          return api(originalRequest);
        } catch {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(REFRESH_TOKEN_KEY);
          localStorage.removeItem('simplecommerce_user');
          window.location.href = '/login';
        }
      } else {
        if (!originalRequest.url?.includes('/auth/')) {
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
