import { apiFetch } from './client';
import type {
  ActiveReviewSummary,
  ActivityEntry,
  DeadlineEntry,
  StatusCount,
  UpcomingRelease,
} from '@/types/dashboard';

export const fetchStatusCounts = () =>
  apiFetch<StatusCount[]>('/dashboard/status-counts');

export const fetchActiveReviews = () =>
  apiFetch<ActiveReviewSummary[]>('/dashboard/active-reviews');

export const fetchUpcomingReleases = () =>
  apiFetch<UpcomingRelease[]>('/dashboard/upcoming-releases');

export const fetchDeadlines = () =>
  apiFetch<DeadlineEntry[]>('/dashboard/deadlines');

export const fetchRecentActivity = () =>
  apiFetch<ActivityEntry[]>('/dashboard/recent-activity');
