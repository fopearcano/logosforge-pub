import type {
  ContractStatus,
  EditorialNoteKind,
  ReviewVerdict,
} from './editorial';
import type { WorkflowStatus } from './workflow';

export interface ManuscriptHit {
  id: string;
  title: string;
  subtitle: string | null;
  status: WorkflowStatus;
  genre: string | null;
  author_id: string;
  author_name: string;
}

export interface AuthorHit {
  id: string;
  full_name: string;
  country: string | null;
  biography: string | null;
}

export interface ReviewHit {
  id: string;
  manuscript_id: string;
  manuscript_title: string;
  verdict: ReviewVerdict;
  summary: string;
  rating: number | null;
  reviewer_name: string | null;
}

export interface NoteHit {
  id: string;
  manuscript_id: string;
  manuscript_title: string;
  kind: EditorialNoteKind;
  body: string;
  pinned: boolean;
  author_user_name: string | null;
}

export interface ContractHit {
  id: string;
  manuscript_id: string;
  manuscript_title: string;
  status: ContractStatus;
  rights_territory: string | null;
  terms: string | null;
}

export interface SearchResults {
  query: string;
  total: number;
  manuscripts: ManuscriptHit[];
  authors: AuthorHit[];
  reviews: ReviewHit[];
  editorial_notes: NoteHit[];
  contracts: ContractHit[];
}

export interface SearchFilters {
  q: string;
  status?: WorkflowStatus;
  genre?: string;
  year?: number;
  author_id?: string;
  rights_territory?: string;
}
