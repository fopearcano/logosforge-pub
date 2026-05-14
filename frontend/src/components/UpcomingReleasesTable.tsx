import { StatusBadge } from './StatusBadge';
import type { UpcomingRelease } from '@/types/dashboard';

interface UpcomingReleasesTableProps {
  entries: UpcomingRelease[];
  onOpenManuscript: (id: string) => void;
}

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function UpcomingReleasesTable({
  entries,
  onOpenManuscript,
}: UpcomingReleasesTableProps) {
  if (entries.length === 0) {
    return (
      <p className="font-serif italic leading-relaxed text-parchment-muted">
        No releases on the horizon.
      </p>
    );
  }

  return (
    <table className="w-full border-collapse">
      <thead>
        <tr className="border-b border-rule">
          <th className="py-2 pr-4 text-left font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Title
          </th>
          <th className="py-2 pr-4 text-left font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Stage
          </th>
          <th className="py-2 pr-4 text-left font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Open work
          </th>
          <th className="py-2 text-right font-mono text-[0.6rem] font-normal uppercase tracking-widest text-parchment-dim">
            Next due
          </th>
        </tr>
      </thead>
      <tbody>
        {entries.map((entry) => (
          <tr key={entry.manuscript_id} className="border-b border-rule">
            <td className="py-3 pr-4 align-top">
              <button
                type="button"
                onClick={() => onOpenManuscript(entry.manuscript_id)}
                className="block text-left font-serif text-[1rem] leading-snug text-parchment transition-colors hover:text-accent"
              >
                {entry.title}
              </button>
              <div className="mt-1 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                {entry.author_name}
              </div>
            </td>
            <td className="py-3 pr-4 align-top">
              <StatusBadge status={entry.status} size="sm" />
            </td>
            <td className="py-3 pr-4 align-top font-mono text-[0.78rem] text-parchment-muted">
              {entry.open_production_items}{' '}
              {entry.open_production_items === 1 ? 'item' : 'items'}
            </td>
            <td className="py-3 text-right align-top font-mono text-[0.78rem] text-parchment">
              {formatDate(entry.next_due)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
