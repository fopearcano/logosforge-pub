import { apiFetch } from './client';
import type { ExportFormat, ExportFormatDescriptor } from '@/types/attachment';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

export const fetchExportFormats = () =>
  apiFetch<ExportFormatDescriptor[]>('/exports/formats');

export function manuscriptExportUrl(
  manuscriptId: string,
  format: ExportFormat,
): string {
  return `${API_BASE}/manuscripts/${manuscriptId}/export?format=${format}`;
}
