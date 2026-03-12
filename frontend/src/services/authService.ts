import api from './api';
import { AuthResponse } from '../types';
import { TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '../constants/api';

export const authService = {
  async requestOtp(phone: string) {
    const { data } = await api.post<{ data: { message: string; expires_in: number } }>(
      '/auth/otp/request',
      { phone }
    );
    return data.data;
  },

  async verifyOtp(phone: string, code: string) {
    const { data } = await api.post<{ data: AuthResponse }>('/auth/otp/verify', {
      phone,
      code,
    });
    const authData = data.data;
    localStorage.setItem(TOKEN_KEY, authData.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, authData.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(authData.user));
    return authData;
  },

  /** Verify Telegram WebApp initData and log in (for Mini App). */
  async verifyTelegram(initData: string) {
    const { data } = await api.post<{ data: AuthResponse }>('/auth/telegram/verify', {
      init_data: initData,
    });
    const authData = data.data;
    localStorage.setItem(TOKEN_KEY, authData.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, authData.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(authData.user));
    return authData.user;
  },

  async logout() {
    try {
      await api.post('/auth/logout', {
        refresh_token: localStorage.getItem(REFRESH_TOKEN_KEY),
      });
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
  },

  getStoredUser() {
    const stored = localStorage.getItem(USER_KEY);
    return stored ? JSON.parse(stored) : null;
  },

  isAuthenticated() {
    return !!localStorage.getItem(TOKEN_KEY);
  },
};
