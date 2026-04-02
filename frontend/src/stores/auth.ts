// src/stores/auth.ts
import { defineStore } from 'pinia';
import axios, { type AxiosError } from 'axios';
import { login } from '../api';
const API_BASE = 'http://localhost:8000'; // thay bằng URL FastAPI thật của bạn

interface User {
  id: number;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('access_token'),
    isLoading: false,
  }),

  getters: {
    isLoggedIn: (state): boolean => !!state.token,
    isAdmin: (state): boolean => state.user?.is_admin ?? false,
  },

  actions: {
    async login(username: string, password: string): Promise<boolean> {
      this.isLoading = true;

      try {
        const response = await login(username, password);
        this.token = response.access_token;
        localStorage.setItem('token', this.token);
        //await this.fetchCurrentUser();
        return true;
      } catch (err: unknown) {
        let errorMessage = 'Đăng nhập thất bại';

        if (axios.isAxiosError(err)) {
          const axiosErr = err as AxiosError<{ detail?: string; message?: string }>;
          errorMessage =
            axiosErr.response?.data?.detail ??
            axiosErr.response?.data?.message ??
            axiosErr.message ??
            errorMessage;
        } else if (err instanceof Error) {
          errorMessage = err.message || errorMessage;
        }

        console.error('[auth] Login failed:', err);
        throw new Error(errorMessage, { cause: err });
      } finally {
        this.isLoading = false;
      }
    },

    async fetchCurrentUser(): Promise<void> {
      if (!this.token) return;

      try {
        const res = await axios.get<User>(`${API_BASE}/users/me`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.user = res.data;
      } catch (err: unknown) {
        console.error('[auth] Fetch current user failed:', err);

        let shouldLogout = true;

        if (axios.isAxiosError(err)) {
          const status = err.response?.status;
          if (status !== 401 && status !== 403) {
            shouldLogout = false; // lỗi khác (mạng, server) → không logout ngay
          }
        }

        if (shouldLogout) {
          this.logout();
        }
      }
    },

    logout(): void {
      this.user = null;
      this.token = null;
      localStorage.removeItem('access_token');
    },

    async init(): Promise<void> {
      if (this.token) {
        await this.fetchCurrentUser();
      }
    },
  },

  // Nếu pinia-plugin-persistedstate đã cài và đăng ký → dùng persist: true
  persist: true,
  // hoặc chi tiết hơn:
  // persist: {
  //   key: 'bao-hiem-auth',
  //   storage: localStorage,
  //   paths: ['token']
  // }
});
