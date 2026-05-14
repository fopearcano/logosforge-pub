import { apiFetch, apiPostJson } from './client';
import type { Author, Manuscript, Page } from '@/types/manuscript';
import type {
  TransitionResponse,
  TransitionsMap,
  WorkflowEvent,
  WorkflowStatus,
} from '@/types/workflow';

type ManuscriptListParams = {
  status?: WorkflowStatus;
  genre?: string;
  author_id?: string;
  skip?: number;
  limit?: number;
};

function toQuery(params: Record<string, unknown>): string {
  const usp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    usp.set(key, String(value));
  }
  const s = usp.toString();
  return s ? `?${s}` : '';
}

export const fetchManuscripts = (params: ManuscriptListParams = {}) =>
  apiFetch<Page<Manuscript>>(`/manuscripts${toQuery(params)}`);

export const fetchManuscript = (id: string) =>
  apiFetch<Manuscript>(`/manuscripts/${id}`);

export const fetchAuthor = (id: string) => apiFetch<Author>(`/authors/${id}`);

export const fetchWorkflowHistory = (id: string) =>
  apiFetch<WorkflowEvent[]>(`/manuscripts/${id}/workflow-events`);

export const transitionManuscript = (
  id: string,
  to_status: WorkflowStatus,
  comment?: string,
) =>
  apiPostJson<TransitionResponse>(`/manuscripts/${id}/transition`, {
    to_status,
    comment: comment?.trim() ? comment.trim() : null,
  });

export const fetchTransitionsMap = () =>
  apiFetch<TransitionsMap>('/workflow/transitions');
