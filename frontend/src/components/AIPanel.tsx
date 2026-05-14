import { useEffect, useState } from 'react';
import { SidebarSection } from './SidebarSection';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import { fetchAIInsights, fetchAIProvider, runAIFeature } from '@/api/ai';
import {
  AI_FEATURE_BLURB,
  AI_FEATURE_LABEL,
  type AIFeature,
  type AIInsight,
  type AIProviderInfo,
} from '@/types/ai';

interface AIPanelProps {
  manuscriptId: string;
  readOnly?: boolean;
}

const FEATURE_ORDER: AIFeature[] = [
  'summarize',
  'style_analysis',
  'editorial_suggestions',
  'semantic_tags',
  'consistency_check',
];

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function AIPanel({ manuscriptId, readOnly = false }: AIPanelProps) {
  const { status } = useAuth();
  const authed = !readOnly && status === 'authenticated';

  const [provider, setProvider] = useState<AIProviderInfo | null>(null);
  const [latest, setLatest] = useState<Partial<Record<AIFeature, AIInsight>>>(
    {},
  );
  const [running, setRunning] = useState<AIFeature | null>(null);
  const [expanded, setExpanded] = useState<AIFeature | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchAIProvider(), fetchAIInsights(manuscriptId)])
      .then(([p, insights]) => {
        if (cancelled) return;
        setProvider(p.active);
        const byFeature: Partial<Record<AIFeature, AIInsight>> = {};
        for (const insight of insights) {
          // The list endpoint returns newest first, so the first hit
          // per feature wins.
          if (!byFeature[insight.feature]) {
            byFeature[insight.feature] = insight;
          }
        }
        setLatest(byFeature);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof ApiError ? e.message : 'AI scaffolding unavailable.');
      });
    return () => {
      cancelled = true;
    };
  }, [manuscriptId]);

  const handleRun = async (feature: AIFeature) => {
    if (!authed) return;
    setRunning(feature);
    setError(null);
    try {
      const response = await runAIFeature(manuscriptId, feature);
      setLatest((prev) => ({
        ...prev,
        [feature]: {
          id: response.insight_id,
          created_at: response.generated_at,
          updated_at: response.generated_at,
          manuscript_id: manuscriptId,
          feature: response.feature,
          provider: response.provider,
          model: response.model,
          payload: response.result,
        },
      }));
      setExpanded(feature);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Run failed.');
    } finally {
      setRunning(null);
    }
  };

  return (
    <SidebarSection
      title="AI assistance"
      meta={provider ? (provider.is_live ? provider.provider : 'dry-run') : '—'}
    >
      <p className="font-serif text-[0.92rem] italic leading-relaxed text-parchment-muted">
        Editorial AI features run through a single provider abstraction. The
        default is a dry-run stub; configure <code className="text-parchment">AI_PROVIDER</code>{' '}
        to talk to a real backend.
      </p>

      {error && (
        <p className="mt-3 font-mono text-[0.6rem] uppercase tracking-widest text-signal">
          {error}
        </p>
      )}

      <ul className="mt-5 flex flex-col gap-4">
        {FEATURE_ORDER.map((feature) => {
          const insight = latest[feature];
          const isExpanded = expanded === feature;
          return (
            <li
              key={feature}
              className="border-t border-rule pt-4 first:border-t-0 first:pt-0"
            >
              <div className="flex items-baseline justify-between gap-3">
                <button
                  type="button"
                  onClick={() => setExpanded(isExpanded ? null : feature)}
                  className="text-left"
                >
                  <div className="font-serif text-[1rem] text-parchment transition-colors hover:text-accent">
                    {AI_FEATURE_LABEL[feature]}
                  </div>
                  <p className="mt-0.5 max-w-[18rem] font-serif text-[0.82rem] italic text-parchment-muted">
                    {AI_FEATURE_BLURB[feature]}
                  </p>
                </button>
                <button
                  type="button"
                  onClick={() => void handleRun(feature)}
                  disabled={!authed || running !== null}
                  className="border border-accent px-3 py-1 font-mono text-[0.6rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:cursor-not-allowed disabled:opacity-40"
                  title={
                    readOnly
                      ? 'Archived · read-only'
                      : !authed
                        ? 'Sign in to run'
                        : undefined
                  }
                >
                  {running === feature
                    ? 'Running…'
                    : insight
                      ? 'Re-run'
                      : 'Run'}
                </button>
              </div>

              {insight && (
                <div className="mt-2 font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
                  Last · {formatDate(insight.created_at)} · {insight.provider}
                  {insight.model ? ` · ${insight.model}` : ''}
                </div>
              )}

              {insight && isExpanded && (
                <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap break-words border border-rule bg-ink-700/50 p-3 font-mono text-[0.72rem] leading-relaxed text-parchment/90">
                  {JSON.stringify(insight.payload, null, 2)}
                </pre>
              )}
            </li>
          );
        })}
      </ul>
    </SidebarSection>
  );
}
