import { apiFetch, apiPatchJson, apiPostJson } from './client';
import type { Page } from '@/types/manuscript';
import type {
  ProductionRecord,
  ProductionRecordDetail,
  StreamStatus,
} from '@/types/production';

export interface ProductionRecordListParams {
  manuscript_id?: string;
  has_release_date?: boolean;
  release_from?: string;
  release_to?: string;
  limit?: number;
  skip?: number;
}

function toQuery(params: ProductionRecordListParams = {}): string {
  const sp = new URLSearchParams();
  if (params.manuscript_id) sp.set('manuscript_id', params.manuscript_id);
  if (params.has_release_date != null)
    sp.set('has_release_date', String(params.has_release_date));
  if (params.release_from) sp.set('release_from', params.release_from);
  if (params.release_to) sp.set('release_to', params.release_to);
  if (params.limit != null) sp.set('limit', String(params.limit));
  if (params.skip != null) sp.set('skip', String(params.skip));
  const q = sp.toString();
  return q ? `?${q}` : '';
}

export const fetchProductionRecords = (params: ProductionRecordListParams = {}) =>
  apiFetch<Page<ProductionRecordDetail>>(`/production-records${toQuery(params)}`);

export const fetchProductionRecordByManuscript = (manuscriptId: string) =>
  apiFetch<ProductionRecord>(`/production-records/by-manuscript/${manuscriptId}`);

export interface ProductionRecordCreateBody {
  manuscript_id: string;
  isbn?: string | null;
  release_date?: string | null;
  print_status?: StreamStatus;
  ebook_status?: StreamStatus;
  audiobook_status?: StreamStatus;
  cover_status?: StreamStatus;
  layout_status?: StreamStatus;
  prepress_status?: StreamStatus;
  notes?: string | null;
}

export const createProductionRecord = (body: ProductionRecordCreateBody) =>
  apiPostJson<ProductionRecord>('/production-records', body);

export type ProductionRecordPatch = Partial<ProductionRecordCreateBody>;

export const patchProductionRecord = (id: string, body: ProductionRecordPatch) =>
  apiPatchJson<ProductionRecord>(`/production-records/${id}`, body);
