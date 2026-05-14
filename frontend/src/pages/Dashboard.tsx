import { useEffect, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { StatusDot } from '@/components/StatusDot';
import { fetchHealth, fetchMeta } from '@/api/meta';
import type { AppMeta } from '@/types/meta';

type ServiceState = 'pending' | 'ok' | 'error';

const SECTIONS = [
  {
    eyebrow: 'Folio I',
    title: 'Catalogue',
    body: 'Forthcoming titles, imprints, and editions in preparation.',
  },
  {
    eyebrow: 'Folio II',
    title: 'Manuscripts',
    body: 'Submissions under review, revision rounds, and editorial notes.',
  },
  {
    eyebrow: 'Folio III',
    title: 'Authors',
    body: 'Contracts, correspondence, and dossiers across the roster.',
  },
  {
    eyebrow: 'Folio IV',
    title: 'Production',
    body: 'Typesetting, proofs, printing schedules, and binding.',
  },
];

export function Dashboard() {
  const [meta, setMeta] = useState<AppMeta | null>(null);
  const [service, setService] = useState<ServiceState>('pending');

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchMeta(), fetchHealth()])
      .then(([m]) => {
        if (cancelled) return;
        setMeta(m);
        setService('ok');
      })
      .catch(() => {
        if (cancelled) return;
        setService('error');
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
            production — under a single, local, archival surface. This is the
            opening folio; the apparatus of the press will be drawn in over
            successive editions.
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
              <dt className="text-parchment-dim">Storage</dt>
              <dd>SQLite</dd>
            </div>
          </dl>
        </aside>
      </section>

      <div className="editorial-rule" />

      <section>
        <Eyebrow>Folios in preparation</Eyebrow>
        <div className="mt-8 grid grid-cols-1 gap-px overflow-hidden border border-rule bg-rule sm:grid-cols-2">
          {SECTIONS.map((item) => (
            <article
              key={item.title}
              className="flex flex-col justify-between bg-ink-800 p-8 transition-colors hover:bg-ink-700"
            >
              <div>
                <Eyebrow>{item.eyebrow}</Eyebrow>
                <h3 className="mt-3 font-serif text-2xl text-parchment">{item.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-parchment-muted">{item.body}</p>
              </div>
              <span className="mt-8 font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                In preparation
              </span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
