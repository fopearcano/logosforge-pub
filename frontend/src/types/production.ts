import type { WorkflowStatus } from './workflow';

export type StreamStatus =
  | 'not_planned'
  | 'pending'
  | 'in_progress'
  | 'blocked'
  | 'complete';

export const STREAM_STATUSES: StreamStatus[] = [
  'not_planned',
  'pending',
  'in_progress',
  'blocked',
  'complete',
];

export const STREAM_STATUS_LABEL: Record<StreamStatus, string> = {
  not_planned: 'Not planned',
  pending: 'Pending',
  in_progress: 'In progress',
  blocked: 'Blocked',
  complete: 'Complete',
};

export type StreamKey =
  | 'print_status'
  | 'ebook_status'
  | 'audiobook_status'
  | 'cover_status'
  | 'layout_status'
  | 'prepress_status';

export interface ProductionRecord {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  isbn: string | null;
  release_date: string | null;
  print_status: StreamStatus;
  ebook_status: StreamStatus;
  audiobook_status: StreamStatus;
  cover_status: StreamStatus;
  layout_status: StreamStatus;
  prepress_status: StreamStatus;
  notes: string | null;
}

export interface ProductionRecordDetail extends ProductionRecord {
  manuscript_title: string;
  manuscript_status: WorkflowStatus;
  author_name: string | null;
}

export const FORMAT_STREAMS: { key: StreamKey; label: string }[] = [
  { key: 'print_status', label: 'Print' },
  { key: 'ebook_status', label: 'Ebook' },
  { key: 'audiobook_status', label: 'Audiobook' },
];

export const STAGE_STREAMS: { key: StreamKey; label: string }[] = [
  { key: 'cover_status', label: 'Cover' },
  { key: 'layout_status', label: 'Layout' },
  { key: 'prepress_status', label: 'Prepress' },
];

export const ALL_STREAMS: { key: StreamKey; label: string }[] = [
  ...FORMAT_STREAMS,
  ...STAGE_STREAMS,
];
