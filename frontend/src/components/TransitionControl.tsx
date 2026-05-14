import { useState } from 'react';
import { Eyebrow } from './Eyebrow';
import { StatusBadge } from './StatusBadge';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import { transitionManuscript } from '@/api/manuscripts';
import { STATUS_LABELS, type TransitionResponse, type WorkflowStatus } from '@/types/workflow';

interface TransitionControlProps {
  manuscriptId: string;
  currentStatus: WorkflowStatus;
  allowedNext: WorkflowStatus[];
  onTransition: (response: TransitionResponse) => void;
}

export function TransitionControl({
  manuscriptId,
  currentStatus,
  allowedNext,
  onTransition,
}: TransitionControlProps) {
  const { status: authStatus } = useAuth();
  const [target, setTarget] = useState<WorkflowStatus | ''>(
    allowedNext[0] ?? '',
  );
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authed = authStatus === 'authenticated';
  const noTargets = allowedNext.length === 0;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!target) return;
    setSubmitting(true);
    setError(null);
    try {
      const response = await transitionManuscript(
        manuscriptId,
        target as WorkflowStatus,
        comment,
      );
      onTransition(response);
      setComment('');
      setTarget(response.allowed_next[0] ?? '');
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message || 'Transition failed.');
      } else {
        setError('Transition failed.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="border border-rule p-6">
      <div className="flex items-baseline justify-between">
        <Eyebrow>Advance status</Eyebrow>
        <StatusBadge status={currentStatus} size="sm" />
      </div>

      {noTargets ? (
        <p className="mt-6 max-w-prose font-serif text-[0.95rem] italic leading-relaxed text-parchment-muted">
          This manuscript has reached a terminal status. No further transitions
          are permitted.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-5">
          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              Move to
            </span>
            <select
              value={target}
              onChange={(e) => setTarget(e.target.value as WorkflowStatus)}
              disabled={!authed || submitting}
              className="border border-rule bg-ink-800 px-3 py-2 text-sm text-parchment focus:border-accent focus:outline-none disabled:opacity-50"
            >
              {allowedNext.map((s) => (
                <option key={s} value={s}>
                  {STATUS_LABELS[s]}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              Comment (optional)
            </span>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              disabled={!authed || submitting}
              rows={3}
              placeholder="Editorial note that will accompany this transition…"
              className="resize-none border border-rule bg-ink-800 px-3 py-2 font-serif text-sm leading-relaxed text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none disabled:opacity-50"
            />
          </label>

          {error && (
            <p className="font-mono text-[0.7rem] uppercase tracking-widest text-signal">
              {error}
            </p>
          )}

          {!authed && (
            <p className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
              Sign in to perform a transition.
            </p>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!authed || submitting || !target}
              className="border border-accent px-5 py-2 font-mono text-[0.68rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {submitting ? 'Recording…' : 'Record transition'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
