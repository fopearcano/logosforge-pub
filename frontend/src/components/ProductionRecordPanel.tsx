import { useState } from 'react';
import { EditableField } from './EditableField';
import { SidebarSection } from './SidebarSection';
import { StreamStatusBadge } from './StreamStatusBadge';
import { ApiError } from '@/api/client';
import {
  createProductionRecord,
  patchProductionRecord,
} from '@/api/productionRecords';
import {
  ALL_STREAMS,
  FORMAT_STREAMS,
  STAGE_STREAMS,
  STREAM_STATUSES,
  STREAM_STATUS_LABEL,
  type ProductionRecord,
  type StreamKey,
  type StreamStatus,
} from '@/types/production';

interface ProductionRecordPanelProps {
  manuscriptId: string;
  record: ProductionRecord | null;
  canEdit: boolean;
  onChange: (record: ProductionRecord) => void;
}

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function ProductionRecordPanel({
  manuscriptId,
  record,
  canEdit,
  onChange,
}: ProductionRecordPanelProps) {
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (record === null) {
    return (
      <SidebarSection title="Production record" meta="None yet">
        <p className="font-serif text-sm italic leading-relaxed text-parchment-muted">
          No production record has been opened for this manuscript.
        </p>
        {error && (
          <p className="mt-3 font-mono text-[0.62rem] uppercase tracking-widest text-signal">
            {error}
          </p>
        )}
        <button
          type="button"
          disabled={!canEdit || starting}
          onClick={async () => {
            setStarting(true);
            setError(null);
            try {
              const created = await createProductionRecord({
                manuscript_id: manuscriptId,
              });
              onChange(created);
            } catch (e) {
              setError(
                e instanceof ApiError ? e.message : 'Could not start record.',
              );
            } finally {
              setStarting(false);
            }
          }}
          className="mt-5 w-full border border-accent px-3 py-2 font-mono text-[0.65rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {!canEdit
            ? 'Sign in to open a record'
            : starting
              ? 'Opening…'
              : 'Open production record'}
        </button>
      </SidebarSection>
    );
  }

  const patch = async (updates: Partial<ProductionRecord>) => {
    const updated = await patchProductionRecord(record.id, updates);
    onChange(updated);
  };

  const setStream = async (key: StreamKey, value: StreamStatus) => {
    await patch({ [key]: value } as Partial<ProductionRecord>);
  };

  return (
    <SidebarSection title="Production record" meta={record.isbn ?? 'No ISBN'}>
      <dl className="grid grid-cols-[auto,1fr] gap-x-6 gap-y-4 text-sm">
        <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          ISBN
        </dt>
        <dd className="font-mono text-[0.85rem] text-parchment">
          <EditableField
            value={record.isbn ?? ''}
            canEdit={canEdit}
            placeholder="978-…"
            emptyLabel="Not assigned"
            onSave={(v) => patch({ isbn: v.trim() || null })}
            inputClassName="font-mono text-[0.85rem] text-parchment"
          />
        </dd>

        <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Release date
        </dt>
        <dd className="font-mono text-[0.85rem] text-parchment">
          <EditableField
            value={record.release_date ?? ''}
            canEdit={canEdit}
            placeholder="YYYY-MM-DD"
            emptyLabel="Unscheduled"
            onSave={(v) => patch({ release_date: v.trim() || null })}
            inputClassName="font-mono text-[0.85rem] text-parchment"
          />
          {record.release_date && (
            <div className="mt-1 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              {formatDate(record.release_date)}
            </div>
          )}
        </dd>
      </dl>

      <div className="mt-7">
        <h4 className="label-eyebrow">Formats</h4>
        <ul className="mt-3 flex flex-col gap-2">
          {FORMAT_STREAMS.map(({ key, label }) => (
            <StreamRow
              key={key}
              streamKey={key}
              label={label}
              value={record[key]}
              canEdit={canEdit}
              onChange={(v) => setStream(key, v)}
            />
          ))}
        </ul>
      </div>

      <div className="mt-6">
        <h4 className="label-eyebrow">Stages</h4>
        <ul className="mt-3 flex flex-col gap-2">
          {STAGE_STREAMS.map(({ key, label }) => (
            <StreamRow
              key={key}
              streamKey={key}
              label={label}
              value={record[key]}
              canEdit={canEdit}
              onChange={(v) => setStream(key, v)}
            />
          ))}
        </ul>
      </div>

      <div className="mt-6">
        <h4 className="label-eyebrow">Notes</h4>
        <div className="mt-3 font-serif text-[0.92rem] leading-relaxed text-parchment/90">
          <EditableField
            value={record.notes ?? ''}
            canEdit={canEdit}
            type="multiline"
            placeholder="Production notes…"
            emptyLabel={canEdit ? 'Add notes…' : '—'}
            onSave={(v) => patch({ notes: v.trim() || null })}
            inputClassName="font-serif text-[0.92rem] leading-relaxed text-parchment/90"
          />
        </div>
      </div>
    </SidebarSection>
  );
}

interface StreamRowProps {
  streamKey: StreamKey;
  label: string;
  value: StreamStatus;
  canEdit: boolean;
  onChange: (value: StreamStatus) => Promise<void>;
}

function StreamRow({ label, value, canEdit, onChange }: StreamRowProps) {
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = async (next: StreamStatus) => {
    if (next === value) {
      setEditing(false);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await onChange(next);
      setEditing(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed.');
    } finally {
      setSaving(false);
    }
  };

  if (!canEdit || !editing) {
    return (
      <li className="flex items-center justify-between gap-3">
        <span className="font-serif text-[0.95rem] text-parchment">{label}</span>
        <button
          type="button"
          onClick={() => canEdit && setEditing(true)}
          disabled={!canEdit}
          className={
            canEdit
              ? 'transition-opacity hover:opacity-80'
              : 'cursor-default'
          }
          title={canEdit ? 'Click to change' : undefined}
        >
          <StreamStatusBadge status={value} />
        </button>
      </li>
    );
  }

  return (
    <li className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-3">
        <span className="font-serif text-[0.95rem] text-parchment">{label}</span>
        <select
          value={value}
          onChange={(e) => void handleSelect(e.target.value as StreamStatus)}
          disabled={saving}
          className="border border-rule bg-ink-800 px-2 py-1 font-mono text-[0.62rem] uppercase tracking-widest text-parchment focus:border-accent focus:outline-none disabled:opacity-50"
        >
          {STREAM_STATUSES.map((s) => (
            <option key={s} value={s}>
              {STREAM_STATUS_LABEL[s]}
            </option>
          ))}
        </select>
      </div>
      {error && (
        <span className="text-right font-mono text-[0.6rem] uppercase tracking-widest text-signal">
          {error}
        </span>
      )}
      {!error && (
        <button
          type="button"
          onClick={() => setEditing(false)}
          disabled={saving}
          className="text-right font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment-muted"
        >
          Done
        </button>
      )}
    </li>
  );
}

export { ALL_STREAMS };
