import { useEffect, useState, type FormEvent } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { SectionHeading } from '@/components/SectionHeading';
import { StatusBadge } from '@/components/StatusBadge';
import { ApiError } from '@/api/client';
import { fetchAuthors } from '@/api/manuscripts';
import { search } from '@/api/search';
import {
  CONTRACT_STATUS_LABEL,
  EDITORIAL_NOTE_KIND_LABEL,
  REVIEW_VERDICT_LABEL,
  type EditorialNoteKind,
} from '@/types/editorial';
import type { Author } from '@/types/manuscript';
import type { SearchFilters, SearchResults } from '@/types/search';
import { STATUS_LABELS, WORKFLOW_STATUSES, type WorkflowStatus } from '@/types/workflow';

interface SearchPageProps {
  onOpenManuscript: (id: string) => void;
}

interface DraftFilters {
  q: string;
  status: string;
  genre: string;
  year: string;
  author_id: string;
  rights_territory: string;
}

const EMPTY: DraftFilters = {
  q: '',
  status: '',
  genre: '',
  year: '',
  author_id: '',
  rights_territory: '',
};

function buildFilters(draft: DraftFilters): SearchFilters | null {
  const q = draft.q.trim();
  if (!q) return null;
  return {
    q,
    status: (draft.status || undefined) as WorkflowStatus | undefined,
    genre: draft.genre.trim() || undefined,
    year: draft.year ? Number(draft.year) : undefined,
    author_id: draft.author_id || undefined,
    rights_territory: draft.rights_territory.trim() || undefined,
  };
}

export function SearchPage({ onOpenManuscript }: SearchPageProps) {
  const [draft, setDraft] = useState<DraftFilters>(EMPTY);
  const [results, setResults] = useState<SearchResults | null>(null);
  const [authors, setAuthors] = useState<Author[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchAuthors()
      .then((page) => {
        if (!cancelled) setAuthors(page.items);
      })
      .catch(() => {
        /* author list is non-essential */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const filters = buildFilters(draft);
    if (!filters) {
      setError('Enter a search term to begin.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const r = await search(filters);
      setResults(r);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Search failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDraft(EMPTY);
    setResults(null);
    setError(null);
  };

  return (
    <div className="flex flex-col gap-14">
      <header>
        <Eyebrow>Search · the catalogue</Eyebrow>
        <h2 className="mt-3 font-serif text-5xl leading-tight text-parchment">
          A reading room for the whole press.
        </h2>
        <p className="mt-4 max-w-prose text-parchment-muted">
          One query across manuscripts, authors, reviews, editorial notes,
          and contracts. Narrow the field with the filters at the right of
          the search bar.
        </p>
      </header>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-6 border border-rule p-8"
      >
        <label className="flex flex-col gap-2">
          <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
            Query
          </span>
          <input
            type="text"
            value={draft.q}
            onChange={(e) => setDraft({ ...draft, q: e.target.value })}
            placeholder="A title, name, theme, territory…"
            className="border border-rule bg-ink-700 px-4 py-3 font-serif text-xl text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none"
            autoFocus
          />
        </label>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Status
            </span>
            <select
              value={draft.status}
              onChange={(e) => setDraft({ ...draft, status: e.target.value })}
              className="border border-rule bg-ink-800 px-3 py-2 font-mono text-[0.78rem] uppercase tracking-wider text-parchment focus:border-accent focus:outline-none"
            >
              <option value="">Any</option>
              {WORKFLOW_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {STATUS_LABELS[s]}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Genre
            </span>
            <input
              type="text"
              value={draft.genre}
              onChange={(e) => setDraft({ ...draft, genre: e.target.value })}
              placeholder="Essays, Fiction…"
              className="border border-rule bg-ink-800 px-3 py-2 font-serif text-[0.95rem] text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none"
            />
          </label>

          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Year
            </span>
            <input
              type="number"
              inputMode="numeric"
              min={1900}
              max={2999}
              value={draft.year}
              onChange={(e) => setDraft({ ...draft, year: e.target.value })}
              placeholder="—"
              className="border border-rule bg-ink-800 px-3 py-2 font-mono text-[0.85rem] text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none"
            />
          </label>

          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Author
            </span>
            <select
              value={draft.author_id}
              onChange={(e) =>
                setDraft({ ...draft, author_id: e.target.value })
              }
              className="border border-rule bg-ink-800 px-3 py-2 font-serif text-[0.9rem] text-parchment focus:border-accent focus:outline-none"
            >
              <option value="">Any</option>
              {authors.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.full_name}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Rights territory
            </span>
            <input
              type="text"
              list="rights-territories"
              value={draft.rights_territory}
              onChange={(e) =>
                setDraft({ ...draft, rights_territory: e.target.value })
              }
              placeholder="world · europe …"
              className="border border-rule bg-ink-800 px-3 py-2 font-mono text-[0.85rem] text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none"
            />
            <datalist id="rights-territories">
              <option value="world" />
              <option value="europe" />
              <option value="north_america" />
              <option value="uk" />
              <option value="latin_america" />
              <option value="asia_pacific" />
            </datalist>
          </label>
        </div>

        <div className="flex items-center justify-between gap-4">
          {error && (
            <span className="font-mono text-[0.65rem] uppercase tracking-widest text-red-300">
              {error}
            </span>
          )}
          <div className="ml-auto flex items-center gap-4">
            <button
              type="button"
              onClick={handleReset}
              className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment-muted"
            >
              Reset
            </button>
            <button
              type="submit"
              disabled={loading}
              className="border border-accent px-5 py-2 font-mono text-[0.7rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:opacity-40"
            >
              {loading ? 'Searching…' : 'Search'}
            </button>
          </div>
        </div>
      </form>

      {results && (
        <div className="flex flex-col gap-14">
          <div className="flex items-baseline justify-between border-b border-rule pb-3">
            <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
              Results for &ldquo;{results.query}&rdquo;
            </span>
            <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-muted">
              {results.total} hit{results.total === 1 ? '' : 's'}
            </span>
          </div>

          <ResultSection
            eyebrow="Catalogue"
            title="Manuscripts"
            count={results.manuscripts.length}
          >
            {results.manuscripts.length === 0 ? (
              <Empty />
            ) : (
              <ul className="flex flex-col">
                {results.manuscripts.map((m) => (
                  <li
                    key={m.id}
                    className="border-t border-rule py-4 first:border-t-0"
                  >
                    <button
                      type="button"
                      onClick={() => onOpenManuscript(m.id)}
                      className="block w-full text-left transition-colors hover:text-accent"
                    >
                      <div className="flex flex-wrap items-baseline justify-between gap-3">
                        <span className="font-serif text-[1.1rem] text-parchment">
                          {m.title}
                        </span>
                        <StatusBadge status={m.status} size="sm" />
                      </div>
                      <div className="mt-1 font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                        {m.author_name}
                        {m.genre && (
                          <>
                            <span className="text-parchment-dim/40 px-2">·</span>
                            {m.genre}
                          </>
                        )}
                      </div>
                      {m.subtitle && (
                        <p className="mt-2 max-w-prose font-serif text-[0.9rem] italic text-parchment-muted">
                          {m.subtitle}
                        </p>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </ResultSection>

          <ResultSection
            eyebrow="Dossier"
            title="Authors"
            count={results.authors.length}
          >
            {results.authors.length === 0 ? (
              <Empty />
            ) : (
              <ul className="flex flex-col">
                {results.authors.map((a) => (
                  <li
                    key={a.id}
                    className="border-t border-rule py-4 first:border-t-0"
                  >
                    <div className="flex flex-wrap items-baseline justify-between gap-3">
                      <span className="font-serif text-[1.05rem] text-parchment">
                        {a.full_name}
                      </span>
                      {a.country && (
                        <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                          {a.country}
                        </span>
                      )}
                    </div>
                    {a.biography && (
                      <p className="mt-2 max-w-prose font-serif text-[0.9rem] italic leading-relaxed text-parchment-muted">
                        {a.biography}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </ResultSection>

          <ResultSection
            eyebrow="Marginalia"
            title="Reviews"
            count={results.reviews.length}
          >
            {results.reviews.length === 0 ? (
              <Empty />
            ) : (
              <ul className="flex flex-col">
                {results.reviews.map((r) => (
                  <li
                    key={r.id}
                    className="border-t border-rule py-4 first:border-t-0"
                  >
                    <button
                      type="button"
                      onClick={() => onOpenManuscript(r.manuscript_id)}
                      className="block w-full text-left"
                    >
                      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
                        <span className="font-serif text-[1rem] text-parchment transition-colors hover:text-accent">
                          {r.manuscript_title}
                        </span>
                        <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-muted">
                          {REVIEW_VERDICT_LABEL[r.verdict]}
                          {r.rating != null && ` · ${r.rating}/5`}
                        </span>
                        {r.reviewer_name && (
                          <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                            by {r.reviewer_name}
                          </span>
                        )}
                      </div>
                      <p className="mt-2 max-w-prose font-serif text-[0.95rem] leading-relaxed text-parchment-muted">
                        {r.summary}
                      </p>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </ResultSection>

          <ResultSection
            eyebrow="Apparatus"
            title="Editorial notes"
            count={results.editorial_notes.length}
          >
            {results.editorial_notes.length === 0 ? (
              <Empty />
            ) : (
              <ul className="flex flex-col">
                {results.editorial_notes.map((n) => (
                  <li
                    key={n.id}
                    className="border-t border-rule py-4 first:border-t-0"
                  >
                    <button
                      type="button"
                      onClick={() => onOpenManuscript(n.manuscript_id)}
                      className="block w-full text-left"
                    >
                      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
                        <span className="font-serif text-[1rem] text-parchment transition-colors hover:text-accent">
                          {n.manuscript_title}
                        </span>
                        <span className="inline-flex items-center border border-rule px-2 py-0.5 font-mono text-[0.58rem] uppercase tracking-widest text-parchment-muted">
                          {EDITORIAL_NOTE_KIND_LABEL[n.kind as EditorialNoteKind]}
                        </span>
                        {n.pinned && (
                          <span className="font-mono text-[0.58rem] uppercase tracking-widest text-accent">
                            Pinned
                          </span>
                        )}
                        {n.author_user_name && (
                          <span className="font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
                            by {n.author_user_name}
                          </span>
                        )}
                      </div>
                      <p className="mt-2 max-w-prose font-serif text-[0.95rem] leading-relaxed text-parchment-muted">
                        {n.body}
                      </p>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </ResultSection>

          <ResultSection
            eyebrow="Rights"
            title="Contracts"
            count={results.contracts.length}
          >
            {results.contracts.length === 0 ? (
              <Empty />
            ) : (
              <ul className="flex flex-col">
                {results.contracts.map((c) => (
                  <li
                    key={c.id}
                    className="border-t border-rule py-4 first:border-t-0"
                  >
                    <button
                      type="button"
                      onClick={() => onOpenManuscript(c.manuscript_id)}
                      className="block w-full text-left"
                    >
                      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
                        <span className="font-serif text-[1rem] text-parchment transition-colors hover:text-accent">
                          {c.manuscript_title}
                        </span>
                        <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-muted">
                          {CONTRACT_STATUS_LABEL[c.status]}
                        </span>
                        {c.rights_territory && (
                          <span className="font-mono text-[0.6rem] uppercase tracking-widest text-accent">
                            {c.rights_territory}
                          </span>
                        )}
                      </div>
                      {c.terms && (
                        <p className="mt-2 max-w-prose font-serif text-[0.92rem] italic leading-relaxed text-parchment-muted">
                          {c.terms}
                        </p>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </ResultSection>
        </div>
      )}

      {!results && !error && !loading && (
        <p className="font-serif italic leading-relaxed text-parchment-muted">
          Submit a query to consult the catalogue.
        </p>
      )}
    </div>
  );
}

interface ResultSectionProps {
  eyebrow: string;
  title: string;
  count: number;
  children: React.ReactNode;
}

function ResultSection({ eyebrow, title, count, children }: ResultSectionProps) {
  return (
    <section>
      <SectionHeading
        eyebrow={eyebrow}
        title={title}
        meta={count === 0 ? 'No matches' : `${count} ${count === 1 ? 'match' : 'matches'}`}
      />
      <div className="mt-6">{children}</div>
    </section>
  );
}

function Empty() {
  return (
    <p className="font-serif italic leading-relaxed text-parchment-muted">
      Nothing turned up here.
    </p>
  );
}
