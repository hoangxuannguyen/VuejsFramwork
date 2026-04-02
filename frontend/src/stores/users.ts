import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

export interface User {
  id?: number;
  email: string;
  password?: string; // Chỉ dùng khi tạo/sửa
  is_active: boolean;
}

const API_BASE = 'http://localhost:8000'; // Thay bằng URL của bạn

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [] as User[],
    isLoading: false,
  }),
  actions: {
    getAuthHeader() {
      const authStore = useAuthStore();
      if (!authStore.token) throw new Error('Không có token xác thực');
      return {
        headers: { Authorization: `Bearer ${authStore.token}` },
      };
    },

    async fetchUsers() {
      this.isLoading = true;
      try {
        const res = await axios.get<{ data: User[] }>(`${API_BASE}/users/`, this.getAuthHeader());
        this.users = Array.isArray(res.data.data) ? res.data.data : [];
      } finally {
        this.isLoading = false;
      }
    },
    async createUser(user: Partial<User>) {
      console.log(user);
      await axios.post(`${API_BASE}/users/`, user, this.getAuthHeader());
      await this.fetchUsers();
    },
    async updateUser(id: number, user: Partial<User>) {
      await axios.put(`${API_BASE}/users/${id}`, user, this.getAuthHeader());
      await this.fetchUsers();
    },
    async deleteUser(id: number) {
      await axios.delete(`${API_BASE}/users/${id}`, this.getAuthHeader());
      await this.fetchUsers();
    },
  },
});
