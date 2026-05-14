import {
  PRODUCTION_STAGE_LABEL,
  PRODUCTION_STATUS_LABEL,
  type ProductionItem,
  type ProductionItemStatus,
} from '@/types/editorial';

interface ProductionTimelineProps {
  items: ProductionItem[];
  highlightId?: string | null;
  onOpenItem?: (id: string) => void;
}

const STATUS_TONE: Record<ProductionItemStatus, string> = {
  pending: 'text-parchment-muted border-parchment-muted/40',
  in_progress: 'text-accent border-accent/60',
  blocked: 'text-signal/80 border-signal/30',
  done: 'text-parchment-dim border-rule',
};

function formatDate(iso: string | null): string {
  if (!iso) return 'No due date';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

function daysFromToday(iso: string): { label: string; tone: string } {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(iso);
  const diffDays = Math.round((target.getTime() - today.getTime()) / 86_400_000);
  if (diffDays < 0) {
    const n = Math.abs(diffDays);
    return {
      label: `${n} day${n === 1 ? '' : 's'} overdue`,
      tone: 'text-accent',
    };
  }
  if (diffDays === 0) return { label: 'Today', tone: 'text-accent' };
  if (diffDays <= 7) return { label: `in ${diffDays} days`, tone: 'text-parchment' };
  return { label: `in ${diffDays} days`, tone: 'text-parchment-muted' };
}

function sortItems(items: ProductionItem[]): ProductionItem[] {
  return [...items].sort((a, b) => {
    if (a.due_date && b.due_date) return a.due_date.localeCompare(b.due_date);
    if (a.due_date) return -1;
    if (b.due_date) return 1;
    return a.created_at.localeCompare(b.created_at);
  });
}

export function ProductionTimeline({
  items,
  highlightId,
  onOpenItem,
}: ProductionTimelineProps) {
  const sorted = sortItems(items);

  if (sorted.length === 0) {
    return (
      <p className="font-serif italic leading-relaxed text-parchment-muted">
        No production work has been scheduled.
      </p>
    );
  }

  return (
    <ol className="flex flex-col gap-7">
      {sorted.map((item) => {
        const isCurrent = item.id === highlightId;
        const days = item.due_date && item.status !== 'done'
          ? daysFromToday(item.due_date)
          : null;

        return (
          <li
            key={item.id}
            className={`border-l ${
              isCurrent ? 'border-accent' : 'border-rule'
            } pl-6`}
          >
            <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
              <div className="flex flex-wrap items-baseline gap-3">
                {onOpenItem ? (
                  <button
                    type="button"
                    onClick={() => onOpenItem(item.id)}
                    className="font-serif text-[1rem] leading-snug text-parchment transition-colors hover:text-accent"
                  >
                    {PRODUCTION_STAGE_LABEL[item.stage]}
                  </button>
                ) : (
                  <span className="font-serif text-[1rem] leading-snug text-parchment">
                    {PRODUCTION_STAGE_LABEL[item.stage]}
                  </span>
                )}
                <span
                  className={`inline-flex items-center border ${STATUS_TONE[item.status]} px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-widest`}
                >
                  {PRODUCTION_STATUS_LABEL[item.status]}
                </span>
                {isCurrent && (
                  <span className="font-mono text-[0.58rem] uppercase tracking-widest text-accent">
                    · current
                  </span>
                )}
              </div>
              <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                {formatDate(item.due_date)}
              </span>
            </div>

            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1">
              <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                {item.assignee_name ?? 'Unassigned'}
              </span>
              {days && (
                <span
                  className={`font-mono text-[0.6rem] uppercase tracking-widest ${days.tone}`}
                >
                  {days.label}
                </span>
              )}
            </div>

            {item.notes && (
              <p className="mt-2 max-w-prose font-serif text-[0.9rem] italic leading-relaxed text-parchment-muted">
                {item.notes}
              </p>
            )}
          </li>
        );
      })}
    </ol>
  );
}
