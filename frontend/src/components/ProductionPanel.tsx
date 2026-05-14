import { SidebarSection } from './SidebarSection';
import {
  PRODUCTION_STAGE_LABEL,
  PRODUCTION_STATUS_LABEL,
  type ProductionItem,
  type ProductionItemStatus,
} from '@/types/editorial';

interface ProductionPanelProps {
  items: ProductionItem[];
  onOpenItem?: (id: string) => void;
}

const STATUS_TONE: Record<ProductionItemStatus, string> = {
  pending: 'text-parchment-muted border-parchment-muted/40',
  in_progress: 'text-accent border-accent/60',
  blocked: 'text-signal/80 border-signal/30',
  done: 'text-parchment-dim border-rule',
};

function formatDueDate(iso: string | null): string {
  if (!iso) return 'No due date';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function ProductionPanel({ items, onOpenItem }: ProductionPanelProps) {
  const sorted = [...items].sort((a, b) => {
    const order = { pending: 0, in_progress: 0, blocked: 1, done: 2 };
    return order[a.status] - order[b.status];
  });

  return (
    <SidebarSection
      title="Production"
      meta={items.length === 0 ? 'None' : `${items.length} item${items.length === 1 ? '' : 's'}`}
    >
      {items.length === 0 ? (
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
          No production work scheduled.
        </p>
      ) : (
        <ul className="flex flex-col gap-4">
          {sorted.map((item) => (
            <li
              key={item.id}
              className="border-t border-rule pt-3 first:border-t-0 first:pt-0"
            >
              <div className="flex items-center justify-between gap-3">
                {onOpenItem ? (
                  <button
                    type="button"
                    onClick={() => onOpenItem(item.id)}
                    className="font-serif text-[0.95rem] text-parchment transition-colors hover:text-accent"
                  >
                    {PRODUCTION_STAGE_LABEL[item.stage]}
                  </button>
                ) : (
                  <span className="font-serif text-[0.95rem] text-parchment">
                    {PRODUCTION_STAGE_LABEL[item.stage]}
                  </span>
                )}
                <span
                  className={`inline-flex items-center border ${STATUS_TONE[item.status]} px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-widest`}
                >
                  {PRODUCTION_STATUS_LABEL[item.status]}
                </span>
              </div>

              <div className="mt-2 flex items-center justify-between font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
                <span>{item.assignee_name ?? 'Unassigned'}</span>
                <span>{formatDueDate(item.due_date)}</span>
              </div>

              {item.notes && (
                <p className="mt-2 font-serif text-[0.85rem] italic leading-relaxed text-parchment-muted">
                  {item.notes}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </SidebarSection>
  );
}
