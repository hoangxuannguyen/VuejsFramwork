import type { AxiosInstance } from 'axios';
import axios from 'axios';
import { type Token } from '../data/comon';

const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(email: string, password: string): Promise<Token> {
  const response = await api.post<Token>(
    '/login',
    { email: email, password: password },
    {
      headers: { 'Content-Type': 'application/json' },
    },
  );
  return response.data;
}
