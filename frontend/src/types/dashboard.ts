import type {
  ProductionItemStatus,
  ProductionStage,
  ReviewVerdict,
} from './editorial';
import type { WorkflowStatus } from './workflow';

export interface StatusCount {
  status: WorkflowStatus;
  count: number;
}

export interface ActiveReviewSummary {
  manuscript_id: string;
  manuscript_title: string;
  author_name: string;
  review_count: number;
  latest_verdict: ReviewVerdict | null;
  latest_review_at: string | null;
}

export interface UpcomingRelease {
  manuscript_id: string;
  title: string;
  author_name: string;
  status: WorkflowStatus;
  next_due: string | null;
  open_production_items: number;
}

export interface DeadlineEntry {
  production_item_id: string;
  manuscript_id: string;
  manuscript_title: string;
  stage: ProductionStage;
  status: ProductionItemStatus;
  assignee_name: string | null;
  due_date: string;
  days_until: number;
}

export interface ActivityEntry {
  event_id: string;
  manuscript_id: string;
  manuscript_title: string;
  actor_id: string | null;
  actor_name: string | null;
  from_status: WorkflowStatus | null;
  to_status: WorkflowStatus;
  note: string | null;
  occurred_at: string;
}
