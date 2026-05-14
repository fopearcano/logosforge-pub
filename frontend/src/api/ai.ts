import { apiFetch, apiPostJson } from './client';
import type {
  AIFeature,
  AIInsight,
  AIProviderListing,
  AIRunResponse,
} from '@/types/ai';

const FEATURE_PATH: Record<AIFeature, string> = {
  summarize: 'summarize',
  style_analysis: 'style-analysis',
  editorial_suggestions: 'editorial-suggestions',
  semantic_tags: 'semantic-tags',
  consistency_check: 'consistency-check',
};

export const runAIFeature = (
  manuscriptId: string,
  feature: AIFeature,
): Promise<AIRunResponse> =>
  apiPostJson<AIRunResponse>(
    `/ai/manuscripts/${manuscriptId}/${FEATURE_PATH[feature]}`,
    {},
  );

export const fetchAIInsights = (
  manuscriptId: string,
  feature?: AIFeature,
): Promise<AIInsight[]> => {
  const query = feature ? `?feature=${feature}` : '';
  return apiFetch<AIInsight[]>(`/ai/manuscripts/${manuscriptId}/insights${query}`);
};

export const fetchAIProvider = () =>
  apiFetch<AIProviderListing>('/ai/providers');
