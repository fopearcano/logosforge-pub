import { useState } from 'react';
import { Eyebrow } from './Eyebrow';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import { createEditorialNote } from '@/api/manuscripts';
import {
  EDITORIAL_NOTE_KINDS,
  EDITORIAL_NOTE_KIND_LABEL,
  type EditorialNote,
  type EditorialNoteKind,
} from '@/types/editorial';

interface EditorialNotesPanelProps {
  manuscriptId: string;
  notes: EditorialNote[];
  readOnly?: boolean;
  onCreate: (note: EditorialNote) => void;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function sortNotes(notes: EditorialNote[]): EditorialNote[] {
  return [...notes].sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
    return b.created_at.localeCompare(a.created_at);
  });
}

export function EditorialNotesPanel({
  manuscriptId,
  notes,
  readOnly = false,
  onCreate,
}: EditorialNotesPanelProps) {
  const { user, status } = useAuth();
  const authed = !readOnly && status === 'authenticated' && user;

  const [kind, setKind] = useState<EditorialNoteKind>('general');
  const [body, setBody] = useState('');
  const [pinned, setPinned] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sorted = sortNotes(notes);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!authed || !body.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const created = await createEditorialNote({
        manuscript_id: manuscriptId,
        author_user_id: user.id,
        kind,
        body: body.trim(),
        pinned,
      });
      onCreate(created);
      setBody('');
      setPinned(false);
      setKind('general');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not save note.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section>
      <div className="flex items-baseline justify-between">
        <Eyebrow>Editorial notes</Eyebrow>
        <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
          {notes.length === 0 ? 'None recorded' : `${notes.length} on file`}
        </span>
      </div>

      {sorted.length === 0 ? (
        <p className="mt-6 font-serif text-[0.95rem] italic leading-relaxed text-parchment-muted">
          No editorial notes have been left for this manuscript yet.
        </p>
      ) : (
        <ul className="mt-8 flex flex-col gap-8">
          {sorted.map((note) => (
            <li
              key={note.id}
              className={`border-l ${
                note.pinned ? 'border-accent' : 'border-rule'
              } pl-6`}
            >
              <div className="flex flex-wrap items-center gap-3 font-mono text-[0.62rem] uppercase tracking-widest">
                <span className="border border-rule px-2 py-0.5 text-parchment-muted">
                  {EDITORIAL_NOTE_KIND_LABEL[note.kind]}
                </span>
                {note.pinned && (
                  <span className="text-accent">Pinned</span>
                )}
                <span className="text-parchment-dim">{formatDate(note.created_at)}</span>
                {note.author_user_name && (
                  <>
                    <span className="text-parchment-dim/40">·</span>
                    <span className="text-parchment-muted">{note.author_user_name}</span>
                  </>
                )}
              </div>
              <p className="mt-3 max-w-prose font-serif text-[1rem] leading-relaxed text-parchment/90">
                {note.body}
              </p>
            </li>
          ))}
        </ul>
      )}

      <form
        onSubmit={handleSubmit}
        className="mt-10 flex flex-col gap-4 border border-rule p-6"
      >
        <div className="flex items-baseline justify-between">
          <Eyebrow>Leave a note</Eyebrow>
          {!authed && (
            <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              {readOnly ? 'Archived · read-only' : 'Sign in to write'}
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[auto,1fr]">
          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              Kind
            </span>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as EditorialNoteKind)}
              disabled={!authed || submitting}
              className="border border-rule bg-ink-800 px-3 py-2 font-mono text-sm uppercase tracking-wider text-parchment focus:border-accent focus:outline-none disabled:opacity-50"
            >
              {EDITORIAL_NOTE_KINDS.map((k) => (
                <option key={k} value={k}>
                  {EDITORIAL_NOTE_KIND_LABEL[k]}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              Note
            </span>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              disabled={!authed || submitting}
              rows={3}
              placeholder="A brief editorial annotation…"
              className="resize-none border border-rule bg-ink-800 px-3 py-2 font-serif text-[0.95rem] leading-relaxed text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none disabled:opacity-50"
            />
          </label>
        </div>

        <div className="flex items-center justify-between gap-4">
          <label className="flex items-center gap-2 font-mono text-[0.65rem] uppercase tracking-widest text-parchment-muted">
            <input
              type="checkbox"
              checked={pinned}
              onChange={(e) => setPinned(e.target.checked)}
              disabled={!authed || submitting}
              className="accent-accent"
            />
            Pin to top
          </label>

          <div className="flex items-center gap-4">
            {error && (
              <span className="font-mono text-[0.65rem] uppercase tracking-widest text-signal">
                {error}
              </span>
            )}
            <button
              type="submit"
              disabled={!authed || submitting || !body.trim()}
              className="border border-accent px-4 py-1.5 font-mono text-[0.65rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {submitting ? 'Saving…' : 'Save note'}
            </button>
          </div>
        </div>
      </form>
    </section>
  );
}
