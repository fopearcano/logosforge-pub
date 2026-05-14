import { REVIEW_VERDICT_LABEL, type ReviewVerdict } from '@/types/editorial';
import type { ActiveReviewSummary } from '@/types/dashboard';

interface ActiveReviewsListProps {
  entries: ActiveReviewSummary[];
  onOpenManuscript: (id: string) => void;
}

const VERDICT_TONE: Record<ReviewVerdict, string> = {
  accept: 'text-accent border-accent/60',
  revise: 'text-parchment-muted border-parchment-muted/40',
  reject: 'text-red-300/80 border-red-400/30',
};

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString(undefined, {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
  });
}

export function ActiveReviewsList({
  entries,
  onOpenManuscript,
}: ActiveReviewsListProps) {
  if (entries.length === 0) {
    return (
      <p className="font-serif italic leading-relaxed text-parchment-muted">
        No manuscripts currently under review.
      </p>
    );
  }

  return (
    <ul className="flex flex-col">
      {entries.map((entry) => (
        <li
          key={entry.manuscript_id}
          className="border-t border-rule py-4 first:border-t-0"
        >
          <button
            type="button"
            onClick={() => onOpenManuscript(entry.manuscript_id)}
            className="block w-full text-left transition-colors hover:text-accent"
          >
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <span className="font-serif text-[1.05rem] text-parchment">
                {entry.manuscript_title}
              </span>
              <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                {entry.review_count}{' '}
                {entry.review_count === 1 ? 'review' : 'reviews'}
              </span>
            </div>

            <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              <span>{entry.author_name}</span>
              {entry.latest_verdict && (
                <>
                  <span className="text-parchment-dim/40">·</span>
                  <span
                    className={`inline-flex items-center border ${VERDICT_TONE[entry.latest_verdict]} px-2 py-0.5`}
                  >
                    Latest · {REVIEW_VERDICT_LABEL[entry.latest_verdict]}
                  </span>
                  <span className="text-parchment-dim/40">·</span>
                  <span>{formatDate(entry.latest_review_at)}</span>
                </>
              )}
            </div>
          </button>
        </li>
      ))}
    </ul>
  );
}
