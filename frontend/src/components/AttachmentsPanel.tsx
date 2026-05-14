import { useEffect, useState, type FormEvent } from 'react';
import { Eyebrow } from './Eyebrow';
import { SidebarSection } from './SidebarSection';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import {
  createPlaceholderAttachment,
  fetchAttachments,
} from '@/api/attachments';
import {
  ATTACHMENT_KINDS,
  ATTACHMENT_KIND_LABEL,
  type Attachment,
  type AttachmentKind,
} from '@/types/attachment';

interface AttachmentsPanelProps {
  manuscriptId: string;
  readOnly?: boolean;
}

function formatSize(bytes: number): string {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function AttachmentsPanel({
  manuscriptId,
  readOnly = false,
}: AttachmentsPanelProps) {
  const { status } = useAuth();
  const authed = !readOnly && status === 'authenticated';

  const [items, setItems] = useState<Attachment[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [filename, setFilename] = useState('');
  const [kind, setKind] = useState<AttachmentKind>('manuscript_draft');
  const [description, setDescription] = useState('');

  useEffect(() => {
    let cancelled = false;
    fetchAttachments({ manuscript_id: manuscriptId, limit: 100 })
      .then((page) => {
        if (cancelled) return;
        setItems(page.items);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof ApiError ? e.message : 'Failed to load.');
      });
    return () => {
      cancelled = true;
    };
  }, [manuscriptId]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!authed || !filename.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const created = await createPlaceholderAttachment({
        manuscript_id: manuscriptId,
        filename: filename.trim(),
        kind,
        description: description.trim() || null,
      });
      setItems((prev) => [created, ...(prev ?? [])]);
      setFilename('');
      setDescription('');
      setKind('manuscript_draft');
      setAdding(false);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not record file.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <SidebarSection
      title="Manuscript files"
      meta={
        items === null
          ? '—'
          : items.length === 0
            ? 'None on file'
            : `${items.length} ${items.length === 1 ? 'item' : 'items'}`
      }
    >
      {items === null && !error && (
        <p className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Loading…
        </p>
      )}

      {items !== null && items.length === 0 && !adding && (
        <p className="font-serif text-sm italic leading-relaxed text-parchment-muted">
          No files recorded for this manuscript.
        </p>
      )}

      {items !== null && items.length > 0 && (
        <ul className="flex flex-col gap-3">
          {items.map((a) => (
            <li
              key={a.id}
              className="border-t border-rule pt-3 first:border-t-0 first:pt-0"
            >
              <div className="flex items-baseline justify-between gap-2">
                <span className="break-all font-mono text-[0.78rem] text-parchment">
                  {a.filename}
                </span>
                {a.is_placeholder && (
                  <span className="border border-rule px-2 py-0.5 font-mono text-[0.55rem] uppercase tracking-widest text-parchment-dim">
                    Placeholder
                  </span>
                )}
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                <span>{ATTACHMENT_KIND_LABEL[a.kind]}</span>
                <span className="text-parchment-dim/40">·</span>
                <span>{formatSize(a.size_bytes)}</span>
                <span className="text-parchment-dim/40">·</span>
                <span>{formatDate(a.created_at)}</span>
                {a.uploader_name && (
                  <>
                    <span className="text-parchment-dim/40">·</span>
                    <span>{a.uploader_name}</span>
                  </>
                )}
              </div>
              {a.description && (
                <p className="mt-2 font-serif text-[0.85rem] italic leading-relaxed text-parchment-muted">
                  {a.description}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}

      {!adding && (
        <button
          type="button"
          onClick={() => setAdding(true)}
          disabled={!authed}
          className="mt-5 w-full border border-rule px-3 py-2 font-mono text-[0.65rem] uppercase tracking-widest text-parchment-muted transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-50"
          title={
            readOnly
              ? 'Archived · read-only'
              : !authed
                ? 'Sign in to record a file'
                : undefined
          }
        >
          {readOnly
            ? 'Archived · read-only'
            : !authed
              ? 'Sign in to record a file'
              : 'Record a file…'}
        </button>
      )}

      {adding && (
        <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-3">
          <label className="flex flex-col gap-1">
            <span className="font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
              Filename
            </span>
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="draft-v2.docx"
              required
              className="border border-rule bg-ink-800 px-3 py-1.5 font-mono text-[0.8rem] text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none"
            />
          </label>

          <label className="flex flex-col gap-1">
            <span className="font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
              Kind
            </span>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as AttachmentKind)}
              className="border border-rule bg-ink-800 px-3 py-1.5 font-mono text-[0.72rem] uppercase tracking-wider text-parchment focus:border-accent focus:outline-none"
            >
              {ATTACHMENT_KINDS.map((k) => (
                <option key={k} value={k}>
                  {ATTACHMENT_KIND_LABEL[k]}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-1">
            <span className="font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
              Description
            </span>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder="What this file is, or where it's expected from…"
              className="resize-none border border-rule bg-ink-800 px-3 py-1.5 font-serif text-[0.9rem] leading-relaxed text-parchment placeholder:text-parchment-dim/60 focus:border-accent focus:outline-none"
            />
          </label>

          {error && (
            <span className="font-mono text-[0.62rem] uppercase tracking-widest text-red-300">
              {error}
            </span>
          )}

          <div className="flex items-center justify-between">
            <span className="font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
              Placeholder · no bytes
            </span>
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => {
                  setAdding(false);
                  setError(null);
                }}
                disabled={submitting}
                className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment-muted"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !filename.trim()}
                className="border border-accent px-3 py-1 font-mono text-[0.62rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:opacity-40"
              >
                {submitting ? 'Recording…' : 'Record'}
              </button>
            </div>
          </div>
        </form>
      )}

      <p className="mt-4 font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim/80">
        <Eyebrow>Note</Eyebrow>{' '}
        <span className="ml-1 normal-case tracking-normal">
          Real uploads use the&nbsp;
          <code className="text-parchment-muted">/api/attachments/upload</code>{' '}
          endpoint.
        </span>
      </p>
    </SidebarSection>
  );
}
