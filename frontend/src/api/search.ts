import { apiFetch } from './client';
import type { SearchFilters, SearchResults } from '@/types/search';

function toQuery(params: SearchFilters): string {
  const sp = new URLSearchParams();
  sp.set('q', params.q);
  if (params.status) sp.set('status', params.status);
  if (params.genre) sp.set('genre', params.genre);
  if (params.year != null && !Number.isNaN(params.year)) sp.set('year', String(params.year));
  if (params.author_id) sp.set('author_id', params.author_id);
  if (params.rights_territory) sp.set('rights_territory', params.rights_territory);
  sp.set('limit', '50');
  return `?${sp.toString()}`;
}

export const search = (filters: SearchFilters) =>
  apiFetch<SearchResults>(`/search${toQuery(filters)}`);
