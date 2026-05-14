import { apiFetch, apiPatchJson, apiPostJson } from './client';
import type { Page } from '@/types/manuscript';
import type {
  EntityKind,
  KnowledgeEntity,
  ManuscriptEntityLink,
  ManuscriptLinkRole,
  NeighborhoodResult,
} from '@/types/knowledge';

interface EntityListParams {
  kind?: EntityKind;
  q?: string;
  limit?: number;
  skip?: number;
}

function toQuery(params: EntityListParams = {}): string {
  const sp = new URLSearchParams();
  if (params.kind) sp.set('kind', params.kind);
  if (params.q) sp.set('q', params.q);
  if (params.limit != null) sp.set('limit', String(params.limit));
  if (params.skip != null) sp.set('skip', String(params.skip));
  const q = sp.toString();
  return q ? `?${q}` : '';
}

// --- entities -----------------------------------------------------------

export const fetchEntities = (params: EntityListParams = {}) =>
  apiFetch<Page<KnowledgeEntity>>(`/knowledge/entities${toQuery(params)}`);

export const fetchEntity = (id: string) =>
  apiFetch<KnowledgeEntity>(`/knowledge/entities/${id}`);

export interface EntityCreateBody {
  name: string;
  slug?: string;
  kind?: EntityKind;
  description?: string | null;
  extras?: string | null;
}

export const createEntity = (body: EntityCreateBody) =>
  apiPostJson<KnowledgeEntity>('/knowledge/entities', body);

export const fetchNeighborhood = (id: string, depth = 1) =>
  apiFetch<NeighborhoodResult>(
    `/knowledge/entities/${id}/neighborhood?depth=${depth}`,
  );

// --- manuscript-scoped links -------------------------------------------

export const fetchManuscriptLinks = (manuscriptId: string) =>
  apiFetch<ManuscriptEntityLink[]>(
    `/manuscripts/${manuscriptId}/entity-links`,
  );

export interface ManuscriptLinkBody {
  entity_id: string;
  role?: ManuscriptLinkRole;
  relevance?: number | null;
  notes?: string | null;
}

export const createManuscriptLink = (
  manuscriptId: string,
  body: ManuscriptLinkBody,
) =>
  apiPostJson<ManuscriptEntityLink>(
    `/manuscripts/${manuscriptId}/entity-links`,
    { manuscript_id: manuscriptId, ...body },
  );

export const patchManuscriptLink = (
  manuscriptId: string,
  linkId: string,
  body: Partial<ManuscriptLinkBody>,
) =>
  apiPatchJson<ManuscriptEntityLink>(
    `/manuscripts/${manuscriptId}/entity-links/${linkId}`,
    body,
  );

export const deleteManuscriptLink = async (
  manuscriptId: string,
  linkId: string,
): Promise<void> => {
  await apiFetch<void>(`/manuscripts/${manuscriptId}/entity-links/${linkId}`, {
    method: 'DELETE',
  });
};
