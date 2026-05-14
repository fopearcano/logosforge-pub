import { apiFetch } from './client';
import type { AppMeta, HealthStatus } from '@/types/meta';

export const fetchMeta = () => apiFetch<AppMeta>('/meta');
export const fetchHealth = () => apiFetch<HealthStatus>('/health');
