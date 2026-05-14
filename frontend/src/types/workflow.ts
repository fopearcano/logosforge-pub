export type WorkflowStatus =
  | 'submitted'
  | 'under_review'
  | 'accepted'
  | 'rejected'
  | 'development_editing'
  | 'copy_editing'
  | 'proofreading'
  | 'layout'
  | 'cover_design'
  | 'prepress'
  | 'published'
  | 'archived';

export const WORKFLOW_STATUSES: WorkflowStatus[] = [
  'submitted',
  'under_review',
  'accepted',
  'rejected',
  'development_editing',
  'copy_editing',
  'proofreading',
  'layout',
  'cover_design',
  'prepress',
  'published',
  'archived',
];

export const STATUS_LABELS: Record<WorkflowStatus, string> = {
  submitted: 'Submitted',
  under_review: 'Under Review',
  accepted: 'Accepted',
  rejected: 'Rejected',
  development_editing: 'Development Editing',
  copy_editing: 'Copy Editing',
  proofreading: 'Proofreading',
  layout: 'Layout',
  cover_design: 'Cover Design',
  prepress: 'Prepress',
  published: 'Published',
  archived: 'Archived',
};

export interface WorkflowEvent {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  actor_id: string | null;
  actor_name: string | null;
  from_status: WorkflowStatus | null;
  to_status: WorkflowStatus;
  note: string | null;
}

export interface TransitionResponse {
  manuscript_id: string;
  status: WorkflowStatus;
  event: WorkflowEvent;
  allowed_next: WorkflowStatus[];
}

export type TransitionsMap = Record<WorkflowStatus, WorkflowStatus[]>;
