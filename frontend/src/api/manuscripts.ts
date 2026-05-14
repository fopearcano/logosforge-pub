import { apiFetch, apiPatchJson, apiPostJson } from './client';
import type { Author, Manuscript, Page } from '@/types/manuscript';
import type {
  Contract,
  EditorialNote,
  EditorialNoteKind,
  ProductionItem,
  Review,
} from '@/types/editorial';
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

export const fetchAuthors = () =>
  apiFetch<Page<Author>>(`/authors?limit=200`);

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

export type ManuscriptPatch = Partial<{
  title: string;
  subtitle: string | null;
  synopsis: string | null;
  genre: string | null;
  language: string;
  word_count: number | null;
}>;

export const patchManuscript = (id: string, body: ManuscriptPatch) =>
  apiPatchJson<Manuscript>(`/manuscripts/${id}`, body);

export const fetchReviews = (manuscript_id: string) =>
  apiFetch<Page<Review>>(`/reviews${toQuery({ manuscript_id, limit: 100 })}`);

export const fetchContracts = (manuscript_id: string) =>
  apiFetch<Page<Contract>>(`/contracts${toQuery({ manuscript_id, limit: 100 })}`);

export const fetchProductionItems = (manuscript_id: string) =>
  apiFetch<Page<ProductionItem>>(
    `/production-items${toQuery({ manuscript_id, limit: 100 })}`,
  );

export const fetchEditorialNotes = (manuscript_id: string) =>
  apiFetch<Page<EditorialNote>>(
    `/editorial-notes${toQuery({ manuscript_id, limit: 100 })}`,
  );

export const createEditorialNote = (body: {
  manuscript_id: string;
  author_user_id: string;
  kind: EditorialNoteKind;
  body: string;
  pinned?: boolean;
}) => apiPostJson<EditorialNote>('/editorial-notes', body);
