import type { WorkflowStatus } from './workflow';

export interface Manuscript {
  id: string;
  created_at: string;
  updated_at: string;
  title: string;
  subtitle: string | null;
  synopsis: string | null;
  genre: string | null;
  language: string;
  word_count: number | null;
  status: WorkflowStatus;
  author_id: string;
}

export interface Author {
  id: string;
  created_at: string;
  updated_at: string;
  full_name: string;
  email: string | null;
  country: string | null;
  biography: string | null;
}

export interface Page<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
