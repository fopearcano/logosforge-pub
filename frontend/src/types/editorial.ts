export type ReviewVerdict = 'accept' | 'reject' | 'revise';

export interface Review {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  reviewer_id: string;
  reviewer_name: string | null;
  verdict: ReviewVerdict;
  summary: string;
  rating: number | null;
}

export type ContractStatus = 'draft' | 'sent' | 'signed' | 'terminated';

export interface Contract {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  author_id: string;
  status: ContractStatus;
  advance_amount: string | null;
  royalty_rate: number | null;
  currency: string;
  rights_territory: string | null;
  signed_at: string | null;
  terms: string | null;
}

export type ProductionStage =
  | 'layout'
  | 'cover_design'
  | 'prepress'
  | 'printing';

export type ProductionItemStatus =
  | 'pending'
  | 'in_progress'
  | 'blocked'
  | 'done';

export interface ProductionItem {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  assignee_id: string | null;
  assignee_name: string | null;
  stage: ProductionStage;
  status: ProductionItemStatus;
  due_date: string | null;
  notes: string | null;
}

export type EditorialNoteKind =
  | 'general'
  | 'structural'
  | 'line'
  | 'design'
  | 'production';

export interface EditorialNote {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  author_user_id: string;
  author_user_name: string | null;
  kind: EditorialNoteKind;
  body: string;
  pinned: boolean;
}

export const REVIEW_VERDICT_LABEL: Record<ReviewVerdict, string> = {
  accept: 'Accept',
  reject: 'Reject',
  revise: 'Revise',
};

export const CONTRACT_STATUS_LABEL: Record<ContractStatus, string> = {
  draft: 'Draft',
  sent: 'Sent',
  signed: 'Signed',
  terminated: 'Terminated',
};

export const PRODUCTION_STAGE_LABEL: Record<ProductionStage, string> = {
  layout: 'Layout',
  cover_design: 'Cover Design',
  prepress: 'Prepress',
  printing: 'Printing',
};

export const PRODUCTION_STATUS_LABEL: Record<ProductionItemStatus, string> = {
  pending: 'Pending',
  in_progress: 'In progress',
  blocked: 'Blocked',
  done: 'Done',
};

export const EDITORIAL_NOTE_KIND_LABEL: Record<EditorialNoteKind, string> = {
  general: 'General',
  structural: 'Structural',
  line: 'Line',
  design: 'Design',
  production: 'Production',
};

export const EDITORIAL_NOTE_KINDS: EditorialNoteKind[] = [
  'general',
  'structural',
  'line',
  'design',
  'production',
];
