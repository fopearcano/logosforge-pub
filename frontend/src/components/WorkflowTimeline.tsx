import { StatusBadge } from './StatusBadge';
import type { WorkflowEvent } from '@/types/workflow';

interface WorkflowTimelineProps {
  events: WorkflowEvent[];
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function WorkflowTimeline({ events }: WorkflowTimelineProps) {
  if (events.length === 0) {
    return (
      <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
        No workflow events recorded.
      </p>
    );
  }

  return (
    <ol className="relative ml-3 border-l border-rule">
      {events.map((event) => (
        <li key={event.id} className="relative pl-8 pb-10 last:pb-0">
          <span
            className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full border border-accent bg-ink-800"
            aria-hidden
          />
          <div className="flex flex-col gap-3">
            <div className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
              {formatTimestamp(event.created_at)}
              {event.actor_name && (
                <>
                  <span className="mx-2 text-parchment-dim/40">·</span>
                  <span className="text-parchment-muted">{event.actor_name}</span>
                </>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {event.from_status ? (
                <>
                  <StatusBadge status={event.from_status} size="sm" />
                  <span className="font-mono text-[0.7rem] text-parchment-dim">→</span>
                </>
              ) : (
                <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                  Entered as
                </span>
              )}
              <StatusBadge status={event.to_status} size="sm" />
            </div>

            {event.note && (
              <p className="max-w-prose font-serif text-[0.95rem] italic leading-relaxed text-parchment/90">
                &ldquo;{event.note}&rdquo;
              </p>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
