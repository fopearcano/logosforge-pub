export type EntityKind =
  | 'character'
  | 'place'
  | 'theme'
  | 'motif'
  | 'organization'
  | 'work'
  | 'person'
  | 'period'
  | 'other';

export const ENTITY_KINDS: EntityKind[] = [
  'theme',
  'motif',
  'character',
  'person',
  'place',
  'period',
  'work',
  'organization',
  'other',
];

export const ENTITY_KIND_LABEL: Record<EntityKind, string> = {
  character: 'Character',
  place: 'Place',
  theme: 'Theme',
  motif: 'Motif',
  organization: 'Organization',
  work: 'Work',
  person: 'Person',
  period: 'Period',
  other: 'Other',
};

export type RelationshipKind =
  | 'related_to'
  | 'influences'
  | 'descends_from'
  | 'contrasts_with'
  | 'inhabits'
  | 'authored'
  | 'part_of'
  | 'sibling_of'
  | 'mentor_of'
  | 'adapts'
  | 'other';

export const RELATIONSHIP_KIND_LABEL: Record<RelationshipKind, string> = {
  related_to: 'related to',
  influences: 'influences',
  descends_from: 'descends from',
  contrasts_with: 'contrasts with',
  inhabits: 'inhabits',
  authored: 'authored',
  part_of: 'part of',
  sibling_of: 'sibling of',
  mentor_of: 'mentor of',
  adapts: 'adapts',
  other: 'other',
};

export type ManuscriptLinkRole =
  | 'tagged'
  | 'features'
  | 'references'
  | 'set_in'
  | 'derived_from'
  | 'other';

export const MANUSCRIPT_LINK_ROLES: ManuscriptLinkRole[] = [
  'tagged',
  'features',
  'references',
  'set_in',
  'derived_from',
  'other',
];

export const MANUSCRIPT_LINK_ROLE_LABEL: Record<ManuscriptLinkRole, string> = {
  tagged: 'Tagged',
  features: 'Features',
  references: 'References',
  set_in: 'Set in',
  derived_from: 'Derived from',
  other: 'Other',
};

export interface KnowledgeEntity {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  slug: string;
  kind: EntityKind;
  description: string | null;
  extras: string | null;
}

export interface KnowledgeRelationship {
  id: string;
  created_at: string;
  updated_at: string;
  source_id: string;
  target_id: string;
  kind: RelationshipKind;
  weight: number | null;
  description: string | null;
}

export interface KnowledgeRelationshipDetail extends KnowledgeRelationship {
  source_name: string | null;
  source_kind: EntityKind | null;
  target_name: string | null;
  target_kind: EntityKind | null;
}

export interface ManuscriptEntityLink {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  entity_id: string;
  role: ManuscriptLinkRole;
  relevance: number | null;
  notes: string | null;
  entity_name: string | null;
  entity_kind: EntityKind | null;
  entity_slug: string | null;
}

export interface NeighborhoodNode {
  id: string;
  name: string;
  slug: string;
  kind: EntityKind;
  distance: number;
}

export interface NeighborhoodEdge {
  id: string;
  source_id: string;
  target_id: string;
  kind: RelationshipKind;
  weight: number | null;
  description: string | null;
}

export interface NeighborhoodResult {
  root_id: string;
  depth: number;
  nodes: NeighborhoodNode[];
  edges: NeighborhoodEdge[];
}
