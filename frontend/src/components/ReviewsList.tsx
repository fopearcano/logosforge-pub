import { Eyebrow } from './Eyebrow';
import {
  REVIEW_VERDICT_LABEL,
  type Review,
  type ReviewVerdict,
} from '@/types/editorial';

interface ReviewsListProps {
  reviews: Review[];
}

const VERDICT_TONE: Record<ReviewVerdict, string> = {
  accept: 'text-accent border-accent/60',
  revise: 'text-parchment-muted border-parchment-muted/40',
  reject: 'text-red-300/80 border-red-400/30',
};

function formatRating(rating: number | null): string {
  if (rating == null) return '';
  return `${rating} / 5`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function ReviewsList({ reviews }: ReviewsListProps) {
  return (
    <section>
      <div className="flex items-baseline justify-between">
        <Eyebrow>Reviews</Eyebrow>
        <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
          {reviews.length === 0
            ? 'None on file'
            : `${reviews.length} on file`}
        </span>
      </div>

      {reviews.length === 0 ? (
        <p className="mt-6 font-serif text-[0.95rem] italic leading-relaxed text-parchment-muted">
          No reviews have been recorded for this manuscript.
        </p>
      ) : (
        <ol className="mt-8 flex flex-col gap-10">
          {reviews.map((r) => (
            <li key={r.id} className="border-l border-rule pl-6">
              <div className="flex flex-wrap items-center gap-4">
                <span
                  className={`inline-flex items-center border ${VERDICT_TONE[r.verdict]} px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-widest`}
                >
                  {REVIEW_VERDICT_LABEL[r.verdict]}
                </span>
                {r.rating != null && (
                  <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-muted">
                    {formatRating(r.rating)}
                  </span>
                )}
                <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                  {formatDate(r.created_at)}
                </span>
                {r.reviewer_name && (
                  <>
                    <span className="font-mono text-[0.65rem] text-parchment-dim/40">·</span>
                    <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-muted">
                      {r.reviewer_name}
                    </span>
                  </>
                )}
              </div>

              <p className="mt-4 max-w-prose font-serif text-[1rem] leading-relaxed text-parchment/90">
                {r.summary}
              </p>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
