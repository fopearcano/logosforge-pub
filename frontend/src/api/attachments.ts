import { apiFetch, apiPostJson } from './client';
import type { Page } from '@/types/manuscript';
import type { Attachment, AttachmentKind } from '@/types/attachment';

interface AttachmentListParams {
  manuscript_id?: string;
  kind?: AttachmentKind;
  limit?: number;
}

function toQuery(params: AttachmentListParams = {}): string {
  const sp = new URLSearchParams();
  if (params.manuscript_id) sp.set('manuscript_id', params.manuscript_id);
  if (params.kind) sp.set('kind', params.kind);
  if (params.limit != null) sp.set('limit', String(params.limit));
  const q = sp.toString();
  return q ? `?${q}` : '';
}

export const fetchAttachments = (params: AttachmentListParams = {}) =>
  apiFetch<Page<Attachment>>(`/attachments${toQuery(params)}`);

export interface AttachmentPlaceholderBody {
  manuscript_id: string;
  filename: string;
  content_type?: string;
  size_bytes?: number;
  kind?: AttachmentKind;
  description?: string | null;
}

export const createPlaceholderAttachment = (body: AttachmentPlaceholderBody) =>
  apiPostJson<Attachment>('/attachments', body);
