import { api } from './client'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  phone?: string
  tiktok_url?: string
  instagram_url?: string
  terms_accepted: boolean
}

export const authApi = {
  login: (data: LoginPayload) => api.post('/auth/login', data),
  register: (data: RegisterPayload) => api.post('/auth/register', data),
  refresh: (refresh_token: string) => api.post('/auth/refresh', { refresh_token }),
}
