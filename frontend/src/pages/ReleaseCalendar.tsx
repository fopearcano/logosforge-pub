import { useEffect, useMemo, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { StreamStatusBadge } from '@/components/StreamStatusBadge';
import { ApiError } from '@/api/client';
import { fetchProductionRecords } from '@/api/productionRecords';
import {
  FORMAT_STREAMS,
  type ProductionRecordDetail,
} from '@/types/production';

interface ReleaseCalendarProps {
  onOpenManuscript: (id: string) => void;
}

interface MonthBucket {
  key: string;
  label: string;
  records: ProductionRecordDetail[];
}

function monthKey(iso: string): { key: string; label: string } {
  const d = new Date(iso);
  const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
  const label = d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
  });
  return { key, label };
}

function bucketByMonth(records: ProductionRecordDetail[]): MonthBucket[] {
  const buckets = new Map<string, MonthBucket>();
  for (const r of records) {
    if (!r.release_date) continue;
    const { key, label } = monthKey(r.release_date);
    if (!buckets.has(key)) {
      buckets.set(key, { key, label, records: [] });
    }
    buckets.get(key)!.records.push(r);
  }
  return Array.from(buckets.values()).sort((a, b) => a.key.localeCompare(b.key));
}

function formatDay(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    weekday: 'short',
    day: '2-digit',
  });
}

export function ReleaseCalendar({ onOpenManuscript }: ReleaseCalendarProps) {
  const [records, setRecords] = useState<ProductionRecordDetail[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchProductionRecords({ has_release_date: true, limit: 200 })
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

  const buckets = useMemo(
    () => (records ? bucketByMonth(records) : []),
    [records],
  );

  return (
    <div className="flex flex-col gap-14">
      <header>
        <Eyebrow>Calendar · the year ahead</Eyebrow>
        <h2 className="mt-3 font-serif text-5xl leading-tight text-parchment">
          Release calendar.
        </h2>
        <p className="mt-4 max-w-prose text-parchment-muted">
          Titles with scheduled releases, grouped by month. Past releases
          remain on file for the historical record.
        </p>
      </header>

      {error && (
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-signal">
          {error}
        </p>
      )}

      {records === null && !error && (
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
          Loading…
        </p>
      )}

      {records !== null && buckets.length === 0 && (
        <p className="font-serif italic leading-relaxed text-parchment-muted">
          Nothing on the calendar yet.
        </p>
      )}

      <div className="flex flex-col gap-12">
        {buckets.map((bucket) => (
          <section key={bucket.key}>
            <div className="flex items-baseline justify-between border-b border-rule pb-2">
              <h3 className="font-serif text-2xl text-parchment">
                {bucket.label}
              </h3>
              <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                {bucket.records.length}{' '}
                {bucket.records.length === 1 ? 'release' : 'releases'}
              </span>
            </div>

            <ul className="mt-4">
              {bucket.records.map((r) => (
                <li
                  key={r.id}
                  className="border-b border-rule py-4"
                >
                  <button
                    type="button"
                    onClick={() => onOpenManuscript(r.manuscript_id)}
                    className="grid w-full grid-cols-1 items-baseline gap-2 text-left sm:grid-cols-[7rem,1fr,auto]"
                  >
                    <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment">
                      {formatDay(r.release_date!)}
                    </span>
                    <div>
                      <div className="font-serif text-[1.05rem] text-parchment transition-colors hover:text-accent">
                        {r.manuscript_title}
                      </div>
                      <div className="mt-1 font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                        {r.author_name ?? '—'}
                        {r.isbn && (
                          <>
                            <span className="text-parchment-dim/40 px-2">·</span>
                            {r.isbn}
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1.5 sm:justify-end">
                      {FORMAT_STREAMS.map(({ key, label }) => (
                        <StreamStatusBadge
                          key={key}
                          status={r[key]}
                          size="sm"
                          label={label}
                        />
                      ))}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
