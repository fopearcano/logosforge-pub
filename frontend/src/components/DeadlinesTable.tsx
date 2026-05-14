import {
  PRODUCTION_STAGE_LABEL,
  PRODUCTION_STATUS_LABEL,
  type ProductionItemStatus,
} from '@/types/editorial';
import type { DeadlineEntry } from '@/types/dashboard';

interface DeadlinesTableProps {
  entries: DeadlineEntry[];
  onOpenManuscript: (id: string) => void;
}

const STATUS_TONE: Record<ProductionItemStatus, string> = {
  pending: 'text-parchment-muted border-parchment-muted/40',
  in_progress: 'text-accent border-accent/60',
  blocked: 'text-red-300/80 border-red-400/30',
  done: 'text-parchment-dim border-rule',
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

function formatDaysUntil(days: number): { label: string; tone: string } {
  if (days < 0) {
    const n = Math.abs(days);
    return {
      label: `${n} day${n === 1 ? '' : 's'} overdue`,
      tone: 'text-accent',
    };
  }
  if (days === 0) return { label: 'Due today', tone: 'text-accent' };
  if (days <= 7) return { label: `in ${days} days`, tone: 'text-parchment' };
  return { label: `in ${days} days`, tone: 'text-parchment-muted' };
}

export function DeadlinesTable({
  entries,
  onOpenManuscript,
}: DeadlinesTableProps) {
  if (entries.length === 0) {
    return (
      <p className="font-serif italic leading-relaxed text-parchment-muted">
        No outstanding deadlines.
      </p>
    );
  }

  return (
    <table className="w-full border-collapse">
      <thead>
        <tr className="border-b border-rule">
          <th className="py-2 pr-4 text-left font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Manuscript
          </th>
          <th className="py-2 pr-4 text-left font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Stage
          </th>
          <th className="py-2 pr-4 text-left font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Assignee
          </th>
          <th className="py-2 pr-4 text-left font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Due
          </th>
          <th className="py-2 text-right font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            When
          </th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry) => {
          const days = formatDaysUntil(entry.days_until);
          return (
            <tr key={entry.production_item_id} className="border-b border-rule">
              <td className="py-3 pr-4 align-top">
                <button
                  type="button"
                  onClick={() => onOpenManuscript(entry.manuscript_id)}
                  className="block text-left font-serif text-[1rem] leading-snug text-parchment transition-colors hover:text-accent"
                >
                  {entry.manuscript_title}
                </button>
              </td>
              <td className="py-3 pr-4 align-top">
                <div className="font-serif text-[0.95rem] text-parchment">
                  {PRODUCTION_STAGE_LABEL[entry.stage]}
                </div>
                <span
                  className={`mt-1 inline-flex items-center border ${STATUS_TONE[entry.status]} px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-widest`}
                >
                  {PRODUCTION_STATUS_LABEL[entry.status]}
                </span>
              </td>
              <td className="py-3 pr-4 align-top font-mono text-[0.7rem] uppercase tracking-widest text-parchment-muted">
                {entry.assignee_name ?? 'Unassigned'}
              </td>
              <td className="py-3 pr-4 align-top font-mono text-[0.78rem] text-parchment">
                {formatDate(entry.due_date)}
              </td>
              <td
                className={`py-3 text-right align-top font-mono text-[0.72rem] uppercase tracking-widest ${days.tone}`}
              >
                {days.label}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
