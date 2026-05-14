import { useEffect, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { StatusDot } from '@/components/StatusDot';
import { ManuscriptListItem } from '@/components/ManuscriptListItem';
import { fetchHealth, fetchMeta } from '@/api/meta';
import { fetchManuscripts } from '@/api/manuscripts';
import type { AppMeta } from '@/types/meta';
import type { Manuscript } from '@/types/manuscript';

type ServiceState = 'pending' | 'ok' | 'error';

interface DashboardProps {
  onOpenManuscript: (id: string) => void;
}

export function Dashboard({ onOpenManuscript }: DashboardProps) {
  const [meta, setMeta] = useState<AppMeta | null>(null);
  const [service, setService] = useState<ServiceState>('pending');
  const [manuscripts, setManuscripts] = useState<Manuscript[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchMeta(), fetchHealth(), fetchManuscripts({ limit: 50 })])
      .then(([m, , page]) => {
        if (cancelled) return;
        setMeta(m);
        setService('ok');
        setManuscripts(page.items);
      })
      .catch((e) => {
        if (cancelled) return;
        setService('error');
        setError(e instanceof Error ? e.message : 'Failed to load manuscripts.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const serviceLabel =
    service === 'ok' ? 'Connected' : service === 'error' ? 'Offline' : 'Probing';

  return (
    <div className="flex flex-col gap-16">
      <section className="grid grid-cols-1 gap-10 lg:grid-cols-[2fr,1fr]">
        <div>
          <Eyebrow>Prospectus</Eyebrow>
          <h2 className="mt-3 font-serif text-5xl leading-tight text-parchment">
            A quiet workshop for the long work of publishing.
          </h2>
          <p className="mt-6 max-w-prose text-parchment-muted">
            LOGOSFORGE assembles the daily ledger of an editorial house —
            manuscripts, authors, contracts, and the slow choreography of
            production — under a single, local, archival surface.
          </p>
        </div>

        <aside className="border-l border-rule pl-8">
          <Eyebrow>Colophon</Eyebrow>
          <dl className="mt-4 space-y-4 font-mono text-[0.78rem] uppercase tracking-wider text-parchment-muted">
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Service</dt>
              <dd>
                <StatusDot
                  tone={service === 'ok' ? 'ok' : service === 'error' ? 'error' : 'pending'}
                  label={serviceLabel}
                />
              </dd>
            </div>
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Edition</dt>
              <dd>{meta?.version ?? '—'}</dd>
            </div>
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Environment</dt>
              <dd>{meta?.environment ?? '—'}</dd>
            </div>
            <div className="flex items-baseline justify-between gap-4">
              <dt className="text-parchment-dim">Manuscripts</dt>
              <dd>{manuscripts?.length ?? '—'}</dd>
            </div>
          </dl>
        </aside>
      </section>

      <div className="editorial-rule" />

      <section>
        <div className="flex items-baseline justify-between">
          <Eyebrow>Manuscripts in the house</Eyebrow>
          <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
            Most recent first
          </span>
        </div>

        <div className="mt-6 border-t border-rule">
          {manuscripts === null && !error && (
            <p className="py-10 font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
              Loading…
            </p>
          )}
          {error && (
            <p className="py-10 font-mono text-[0.7rem] uppercase tracking-widest text-red-300">
              {error}
            </p>
          )}
          {manuscripts !== null && manuscripts.length === 0 && (
            <p className="py-10 font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
              No manuscripts on the desk.
            </p>
          )}
          {manuscripts?.map((m) => (
            <ManuscriptListItem
              key={m.id}
              manuscript={m}
              onOpen={onOpenManuscript}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
