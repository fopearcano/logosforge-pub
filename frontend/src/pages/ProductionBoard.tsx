import { useEffect, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { StatusBadge } from '@/components/StatusBadge';
import { StreamStatusBadge } from '@/components/StreamStatusBadge';
import { ApiError } from '@/api/client';
import { fetchProductionRecords } from '@/api/productionRecords';
import {
  FORMAT_STREAMS,
  STAGE_STREAMS,
  type ProductionRecordDetail,
} from '@/types/production';

interface ProductionBoardProps {
  onOpenManuscript: (id: string) => void;
}

function formatRelease(iso: string | null): string {
  if (!iso) return 'Unscheduled';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function ProductionBoard({ onOpenManuscript }: ProductionBoardProps) {
  const [records, setRecords] = useState<ProductionRecordDetail[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchProductionRecords({ limit: 200 })
      .then((page) => {
        if (cancelled) return;
        setRecords(page.items);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof ApiError ? e.message : 'Failed to load.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="flex flex-col gap-14">
      <header>
        <Eyebrow>Production · the workshop</Eyebrow>
        <h2 className="mt-3 font-serif text-5xl leading-tight text-parchment">
          Every title that's on the press.
        </h2>
        <p className="mt-4 max-w-prose text-parchment-muted">
          One row per production record. Formats and stages each carry
          their own status; release dates are listed soonest first, with
          unscheduled titles at the end.
        </p>
      </header>

      {error && (
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-signal">
          {error}
        </p>
      )}

      <div>
        <div className="flex items-baseline justify-between border-b border-rule pb-3">
          <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
            {records === null
              ? 'Loading…'
              : `${records.length} ${records.length === 1 ? 'record' : 'records'} on file`}
          </span>
          <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
            Formats · Stages
          </span>
        </div>

        {records !== null && records.length === 0 && (
          <p className="py-12 font-serif italic leading-relaxed text-parchment-muted">
            No production records yet. Open one from a manuscript's detail
            page.
          </p>
        )}

        {records?.map((r) => (
          <article
            key={r.id}
            className="grid grid-cols-1 gap-4 border-b border-rule py-6 lg:grid-cols-[1fr,1.4fr,auto]"
          >
            <div>
              <button
                type="button"
                onClick={() => onOpenManuscript(r.manuscript_id)}
                className="block text-left font-serif text-[1.15rem] text-parchment transition-colors hover:text-accent"
              >
                {r.manuscript_title}
              </button>
              <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                {r.author_name && <span>{r.author_name}</span>}
                <span className="text-parchment-dim/40">·</span>
                <StatusBadge status={r.manuscript_status} size="sm" />
              </div>
              <div className="mt-2 font-mono text-[0.7rem] uppercase tracking-widest text-parchment-muted">
                {r.isbn ?? 'No ISBN'} · {formatRelease(r.release_date)}
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <div>
                <span className="label-eyebrow">Formats</span>
                <div className="mt-1.5 flex flex-wrap gap-2">
                  {FORMAT_STREAMS.map(({ key, label }) => (
                    <StreamStatusBadge
                      key={key}
                      status={r[key]}
                      size="sm"
                      label={`${label} · ${labelFor(r[key])}`}
                    />
                  ))}
                </div>
              </div>
              <div>
                <span className="label-eyebrow">Stages</span>
                <div className="mt-1.5 flex flex-wrap gap-2">
                  {STAGE_STREAMS.map(({ key, label }) => (
                    <StreamStatusBadge
                      key={key}
                      status={r[key]}
                      size="sm"
                      label={`${label} · ${labelFor(r[key])}`}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div className="self-start font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim lg:text-right">
              Updated · {new Date(r.updated_at).toLocaleDateString()}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function labelFor(s: string): string {
  switch (s) {
    case 'not_planned':
      return '—';
    case 'pending':
      return 'pending';
    case 'in_progress':
      return 'in progress';
    case 'blocked':
      return 'blocked';
    case 'complete':
      return 'complete';
    default:
      return s;
  }
}
