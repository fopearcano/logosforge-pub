import { StatusBadge } from './StatusBadge';
import type { ActivityEntry } from '@/types/dashboard';

interface RecentActivityFeedProps {
  entries: ActivityEntry[];
  onOpenManuscript: (id: string) => void;
}

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function RecentActivityFeed({
  entries,
  onOpenManuscript,
}: RecentActivityFeedProps) {
  if (entries.length === 0) {
    return (
      <p className="font-serif italic leading-relaxed text-parchment-muted">
        No transitions recorded yet.
      </p>
    );
  }

  return (
    <ol className="flex flex-col gap-7">
      {entries.map((e) => (
        <li key={e.event_id} className="border-l border-rule pl-5">
          <div className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
            {formatDateTime(e.occurred_at)}
          </div>

          <button
            type="button"
            onClick={() => onOpenManuscript(e.manuscript_id)}
            className="mt-1 block text-left font-serif text-[1rem] leading-snug text-parchment transition-colors hover:text-accent"
          >
            {e.manuscript_title}
          </button>

          <div className="mt-2 flex flex-wrap items-center gap-2">
            {e.from_status && <StatusBadge status={e.from_status} size="sm" />}
            {e.from_status && (
              <span className="font-mono text-[0.65rem] text-parchment-dim">
                →
              </span>
            )}
            <StatusBadge status={e.to_status} size="sm" />
          </div>

          {e.actor_name && (
            <div className="mt-2 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              by {e.actor_name}
            </div>
          )}

          {e.note && (
            <p className="mt-2 max-w-prose font-serif text-[0.9rem] italic leading-relaxed text-parchment-muted">
              {e.note}
            </p>
          )}
        </li>
      ))}
    </ol>
  );
}
