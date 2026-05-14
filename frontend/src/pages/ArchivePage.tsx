import { useEffect, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { ApiError } from '@/api/client';
import { fetchManuscripts } from '@/api/manuscripts';
import type { Manuscript } from '@/types/manuscript';

interface ArchivePageProps {
  onOpenManuscript: (id: string) => void;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

function callNumber(m: Manuscript): string {
  const year = new Date(m.created_at).getFullYear();
  const slug = m.id.slice(0, 8).toUpperCase();
  return `LF · ${year} · ${slug}`;
}

export function ArchivePage({ onOpenManuscript }: ArchivePageProps) {
  const [items, setItems] = useState<Manuscript[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchManuscripts({ status: 'archived', limit: 200 })
      .then((page) => {
        if (cancelled) return;
        setItems(page.items);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof ApiError ? e.message : 'Failed to load archive.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="flex flex-col gap-14">
      <header>
        <Eyebrow>Archive · the closed stack</Eyebrow>
        <h2 className="mt-3 font-serif text-5xl leading-tight text-parchment">
          The closed stack.
        </h2>
        <p className="mt-4 max-w-prose text-parchment-muted">
          Manuscripts moved out of active rotation are preserved here in
          read-only form. Opening one yields a frozen record — edits,
          transitions, and new notes are disabled.
        </p>
      </header>

      <div>
        <div className="flex items-baseline justify-between border-b border-rule pb-3">
          <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
            Catalogue entries
          </span>
          <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-muted">
            {items === null
              ? 'Loading…'
              : `${items.length} ${items.length === 1 ? 'entry' : 'entries'}`}
          </span>
        </div>

        {error && (
          <p className="py-10 font-mono text-[0.7rem] uppercase tracking-widest text-red-300">
            {error}
          </p>
        )}

        {items !== null && items.length === 0 && !error && (
          <p className="py-12 font-serif italic leading-relaxed text-parchment-muted">
            The archive is empty. Manuscripts will appear here once they
            are moved to the archived status.
          </p>
        )}

        {items !== null && items.length > 0 && (
          <ul className="border-b border-rule">
            {items.map((m) => (
              <li key={m.id} className="border-t border-rule">
                <button
                  type="button"
                  onClick={() => onOpenManuscript(m.id)}
                  className="grid w-full grid-cols-1 items-baseline gap-2 px-1 py-5 text-left transition-colors hover:bg-ink-700/40 sm:grid-cols-[12rem,1fr,8rem] sm:gap-6"
                >
                  <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                    {callNumber(m)}
                  </span>
                  <div>
                    <div className="font-serif text-[1.1rem] text-parchment">
                      {m.title}
                    </div>
                    {m.subtitle && (
                      <div className="mt-1 font-serif text-[0.9rem] italic text-parchment-muted">
                        {m.subtitle}
                      </div>
                    )}
                    <div className="mt-1 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                      {m.genre ?? '—'} · {m.language.toUpperCase()}
                      {m.word_count != null && (
                        <> · {m.word_count.toLocaleString()} words</>
                      )}
                    </div>
                  </div>
                  <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-muted sm:text-right">
                    Archived · {formatDate(m.updated_at)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
