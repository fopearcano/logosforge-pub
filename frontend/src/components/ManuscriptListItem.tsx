import { StatusBadge } from './StatusBadge';
import type { Manuscript } from '@/types/manuscript';

interface Props {
  manuscript: Manuscript;
  onOpen: (id: string) => void;
}

export function ManuscriptListItem({ manuscript, onOpen }: Props) {
  return (
    <button
      type="button"
      onClick={() => onOpen(manuscript.id)}
      className="grid w-full grid-cols-[1fr_auto] items-baseline gap-6 border-b border-rule bg-ink-800 px-2 py-6 text-left transition-colors hover:bg-ink-700 focus:bg-ink-700 focus:outline-none"
    >
      <div className="flex flex-col gap-2">
        <h3 className="font-serif text-xl text-parchment">{manuscript.title}</h3>
        {manuscript.subtitle && (
          <p className="font-serif text-[0.95rem] italic text-parchment-muted">
            {manuscript.subtitle}
          </p>
        )}
        <div className="flex items-center gap-4 font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
          {manuscript.genre && <span>{manuscript.genre}</span>}
          {manuscript.word_count != null && (
            <span>{manuscript.word_count.toLocaleString()} words</span>
          )}
        </div>
      </div>
      <StatusBadge status={manuscript.status} />
    </button>
  );
}
