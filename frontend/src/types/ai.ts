export type AIFeature =
  | 'summarize'
  | 'style_analysis'
  | 'editorial_suggestions'
  | 'semantic_tags'
  | 'consistency_check';

export const AI_FEATURE_LABEL: Record<AIFeature, string> = {
  summarize: 'Summary',
  style_analysis: 'Style analysis',
  editorial_suggestions: 'Editorial suggestions',
  semantic_tags: 'Semantic tags',
  consistency_check: 'Consistency check',
};

export const AI_FEATURE_BLURB: Record<AIFeature, string> = {
  summarize: 'One-line pitch, short editorial summary, thematic tags.',
  style_analysis: 'Register, voice, rhythm, and stylistic concerns.',
  editorial_suggestions: 'Concrete editorial suggestions with rationale.',
  semantic_tags: 'Catalogue tags for faceted search.',
  consistency_check: 'Potential narrative inconsistencies to verify.',
};

export interface AIRunResponse {
  feature: AIFeature;
  provider: string;
  model: string | null;
  generated_at: string;
  insight_id: string;
  result: Record<string, unknown>;
}

export interface AIInsight {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  feature: AIFeature;
  provider: string;
  model: string | null;
  payload: Record<string, unknown>;
}

export interface AIProviderInfo {
  provider: string;
  model: string;
  base_url: string | null;
  is_live: boolean;
}

export interface AIProviderListing {
  active: AIProviderInfo;
  known: string[];
}
