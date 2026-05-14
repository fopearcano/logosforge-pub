import { useCallback, useEffect, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { StatusBadge } from '@/components/StatusBadge';
import { WorkflowTimeline } from '@/components/WorkflowTimeline';
import { TransitionControl } from '@/components/TransitionControl';
import {
  fetchAuthor,
  fetchManuscript,
  fetchTransitionsMap,
  fetchWorkflowHistory,
} from '@/api/manuscripts';
import type { Author, Manuscript } from '@/types/manuscript';
import type { TransitionResponse, TransitionsMap, WorkflowEvent } from '@/types/workflow';

interface ManuscriptViewProps {
  manuscriptId: string;
  onBack: () => void;
}

export function ManuscriptView({ manuscriptId, onBack }: ManuscriptViewProps) {
  const [manuscript, setManuscript] = useState<Manuscript | null>(null);
  const [author, setAuthor] = useState<Author | null>(null);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [transitions, setTransitions] = useState<TransitionsMap | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [m, history, map] = await Promise.all([
        fetchManuscript(manuscriptId),
        fetchWorkflowHistory(manuscriptId),
        fetchTransitionsMap(),
      ]);
      setManuscript(m);
      setEvents(history);
      setTransitions(map);
      const a = await fetchAuthor(m.author_id).catch(() => null);
      setAuthor(a);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load manuscript.');
    }
  }, [manuscriptId]);

  useEffect(() => {
    setManuscript(null);
    setAuthor(null);
    setEvents([]);
    setError(null);
    void load();
  }, [load]);

  const handleTransition = (response: TransitionResponse) => {
    setManuscript((prev) =>
      prev ? { ...prev, status: response.status } : prev,
    );
    setEvents((prev) => [...prev, response.event]);
  };

  if (error) {
    return (
      <div>
        <button
          type="button"
          onClick={onBack}
          className="mb-8 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment"
        >
          ← Back to manuscripts
        </button>
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-red-300">
          {error}
        </p>
      </div>
    );
  }

  if (!manuscript || !transitions) {
    return (
      <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
        Loading…
      </p>
    );
  }

  const allowedNext = transitions[manuscript.status] ?? [];

  return (
    <div>
      <button
        type="button"
        onClick={onBack}
        className="font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment"
      >
        ← Back to manuscripts
      </button>

      <header className="mt-6 flex flex-col gap-4 border-b border-rule pb-10">
        <Eyebrow>{manuscript.genre ?? 'Untitled folio'}</Eyebrow>
        <h2 className="font-serif text-4xl leading-tight text-parchment">
          {manuscript.title}
        </h2>
        {manuscript.subtitle && (
          <p className="font-serif text-xl italic text-parchment-muted">
            {manuscript.subtitle}
          </p>
        )}
        <div className="mt-2 flex flex-wrap items-center gap-6 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim">
          {author && <span>By {author.full_name}</span>}
          {manuscript.word_count != null && (
            <span>{manuscript.word_count.toLocaleString()} words</span>
          )}
          <span>{manuscript.language.toUpperCase()}</span>
        </div>
        <div className="mt-2">
          <StatusBadge status={manuscript.status} />
        </div>
      </header>

      {manuscript.synopsis && (
        <section className="mt-12 max-w-prose">
          <Eyebrow>Synopsis</Eyebrow>
          <p className="mt-4 font-serif text-[1.05rem] leading-relaxed text-parchment/90">
            {manuscript.synopsis}
          </p>
        </section>
      )}

      <section className="mt-16 grid grid-cols-1 gap-16 lg:grid-cols-[2fr,1fr]">
        <div>
          <Eyebrow>Workflow chronicle</Eyebrow>
          <div className="mt-8">
            <WorkflowTimeline events={events} />
          </div>
        </div>

        <aside>
          <TransitionControl
            manuscriptId={manuscript.id}
            currentStatus={manuscript.status}
            allowedNext={allowedNext}
            onTransition={handleTransition}
          />
        </aside>
      </section>
    </div>
  );
}
