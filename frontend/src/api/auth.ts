import { apiFetch, apiPostForm } from './client';
import type { CurrentUser, TokenResponse } from '@/types/auth';

export const login = (email: string, password: string) =>
  apiPostForm<TokenResponse>('/auth/login', { username: email, password });

export const fetchMe = () => apiFetch<CurrentUser>('/auth/me');
