import { useCallback, useEffect, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { EditableField } from '@/components/EditableField';
import { ProductionTimeline } from '@/components/ProductionTimeline';
import { SectionHeading } from '@/components/SectionHeading';
import { SidebarSection } from '@/components/SidebarSection';
import { StatusBadge } from '@/components/StatusBadge';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import {
  fetchManuscript,
  fetchProductionItem,
  fetchProductionItems,
  patchProductionItem,
} from '@/api/manuscripts';
import {
  PRODUCTION_STAGE_LABEL,
  PRODUCTION_STATUS_LABEL,
  type ProductionItem,
  type ProductionItemStatus,
} from '@/types/editorial';
import type { Manuscript } from '@/types/manuscript';

interface ProductionItemViewProps {
  itemId: string;
  onBack: () => void;
  onOpenManuscript: (id: string) => void;
}

const PRODUCTION_ITEM_STATUSES: ProductionItemStatus[] = [
  'pending',
  'in_progress',
  'blocked',
  'done',
];

const STATUS_TONE: Record<ProductionItemStatus, string> = {
  pending: 'text-parchment-muted border-parchment-muted/40',
  in_progress: 'text-accent border-accent/60',
  blocked: 'text-signal/80 border-signal/30',
  done: 'text-parchment-dim border-rule',
};

function formatDate(iso: string | null): string {
  if (!iso) return 'No due date';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

function daysUntil(iso: string): { label: string; tone: string } {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(iso);
  const diff = Math.round((target.getTime() - today.getTime()) / 86_400_000);
  if (diff < 0) {
    const n = Math.abs(diff);
    return { label: `${n} day${n === 1 ? '' : 's'} overdue`, tone: 'text-accent' };
  }
  if (diff === 0) return { label: 'Due today', tone: 'text-accent' };
  if (diff <= 7) return { label: `Due in ${diff} days`, tone: 'text-parchment' };
  return { label: `Due in ${diff} days`, tone: 'text-parchment-muted' };
}

export function ProductionItemView({
  itemId,
  onBack,
  onOpenManuscript,
}: ProductionItemViewProps) {
  const { status: authStatus } = useAuth();
  const canEdit = authStatus === 'authenticated';

  const [item, setItem] = useState<ProductionItem | null>(null);
  const [manuscript, setManuscript] = useState<Manuscript | null>(null);
  const [siblings, setSiblings] = useState<ProductionItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const current = await fetchProductionItem(itemId);
      setItem(current);
      const [m, allItemsPage] = await Promise.all([
        fetchManuscript(current.manuscript_id),
        fetchProductionItems(current.manuscript_id),
      ]);
      setManuscript(m);
      setSiblings(allItemsPage.items);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Failed to load.');
    }
  }, [itemId]);

  useEffect(() => {
    setItem(null);
    setManuscript(null);
    setSiblings([]);
    void load();
  }, [load]);

  const patch = async (updates: Parameters<typeof patchProductionItem>[1]) => {
    if (!item) return;
    const updated = await patchProductionItem(item.id, updates);
    setItem(updated);
    setSiblings((prev) => prev.map((s) => (s.id === updated.id ? updated : s)));
  };

  if (error) {
    return (
      <div>
        <button
          type="button"
          onClick={onBack}
          className="mb-8 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment"
        >
          ← Back
        </button>
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-signal">
          {error}
        </p>
      </div>
    );
  }

  if (!item || !manuscript) {
    return (
      <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
        Loading…
      </p>
    );
  }

  const days = item.due_date && item.status !== 'done'
    ? daysUntil(item.due_date)
    : null;

  return (
    <div>
      <button
        type="button"
        onClick={onBack}
        className="font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment"
      >
        ← Back to production
      </button>

      <header className="mt-6 flex flex-col gap-4 border-b border-rule pb-10">
        <Eyebrow>Production item · {PRODUCTION_STAGE_LABEL[item.stage]}</Eyebrow>
        <button
          type="button"
          onClick={() => onOpenManuscript(manuscript.id)}
          className="block text-left font-serif text-4xl leading-tight text-parchment transition-colors hover:text-accent"
        >
          {manuscript.title}
        </button>
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim">
          <StatusBadge status={manuscript.status} size="sm" />
          <span>Created · {formatDate(item.created_at)}</span>
          <span>Updated · {formatDate(item.updated_at)}</span>
        </div>
      </header>

      <div className="mt-12 grid grid-cols-1 gap-16 lg:grid-cols-[2fr,1fr]">
        <div className="flex flex-col gap-12">
          <section>
            <SectionHeading
              eyebrow="Schedule"
              title="Due date and status"
              meta={days ? days.label : undefined}
            />
            <div className="mt-6 flex flex-col gap-4 border border-rule p-6">
              <div className="flex flex-wrap items-baseline justify-between gap-3">
                <span className="label-eyebrow">Status</span>
                <select
                  value={item.status}
                  disabled={!canEdit}
                  onChange={(e) =>
                    void patch({ status: e.target.value as ProductionItemStatus })
                  }
                  className={`border ${STATUS_TONE[item.status]} bg-ink-800 px-3 py-1.5 font-mono text-[0.65rem] uppercase tracking-widest focus:border-accent focus:outline-none disabled:opacity-60`}
                >
                  {PRODUCTION_ITEM_STATUSES.map((s) => (
                    <option key={s} value={s}>
                      {PRODUCTION_STATUS_LABEL[s]}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-wrap items-baseline justify-between gap-3">
                <span className="label-eyebrow">Due date</span>
                <div className="text-right">
                  <EditableField
                    value={item.due_date ?? ''}
                    canEdit={canEdit}
                    placeholder="YYYY-MM-DD"
                    emptyLabel="No due date"
                    onSave={(v) => patch({ due_date: v.trim() || null })}
                    inputClassName="font-mono text-[0.85rem] text-parchment"
                  />
                  {item.due_date && (
                    <div className="mt-1 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                      {formatDate(item.due_date)}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <span className="label-eyebrow">Notes</span>
                <div className="mt-2 font-serif text-[0.95rem] leading-relaxed text-parchment/90">
                  <EditableField
                    value={item.notes ?? ''}
                    canEdit={canEdit}
                    type="multiline"
                    placeholder="Production notes for this item…"
                    emptyLabel={canEdit ? 'Add notes…' : '—'}
                    onSave={(v) => patch({ notes: v.trim() || null })}
                    inputClassName="font-serif text-[0.95rem] leading-relaxed text-parchment/90"
                  />
                </div>
              </div>
            </div>
          </section>

          <section>
            <SectionHeading
              eyebrow="Chronicle"
              title="Production timeline"
              meta={`${siblings.length} item${siblings.length === 1 ? '' : 's'}`}
            />
            <div className="mt-6">
              <ProductionTimeline
                items={siblings}
                highlightId={item.id}
              />
            </div>
          </section>
        </div>

        <aside className="flex flex-col gap-8">
          <SidebarSection title="Assignment">
            <p className="font-serif text-[1.05rem] text-parchment">
              {item.assignee_name ?? 'Unassigned'}
            </p>
            <p className="mt-2 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Reassignment is not yet wired through.
            </p>
          </SidebarSection>

          <SidebarSection title="Stage">
            <p className="font-serif text-[1.05rem] text-parchment">
              {PRODUCTION_STAGE_LABEL[item.stage]}
            </p>
            <p className="mt-2 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Stages are structural and cannot be reassigned in place.
            </p>
          </SidebarSection>

          <SidebarSection title="Manuscript">
            <button
              type="button"
              onClick={() => onOpenManuscript(manuscript.id)}
              className="block text-left font-serif text-[1.05rem] text-parchment transition-colors hover:text-accent"
            >
              {manuscript.title}
            </button>
            <p className="mt-2 font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
              Open the manuscript for the full record.
            </p>
          </SidebarSection>
        </aside>
      </div>
    </div>
  );
}
