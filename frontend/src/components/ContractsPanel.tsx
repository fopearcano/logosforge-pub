import { SidebarSection } from './SidebarSection';
import {
  CONTRACT_STATUS_LABEL,
  type Contract,
  type ContractStatus,
} from '@/types/editorial';

interface ContractsPanelProps {
  contracts: Contract[];
}

const STATUS_TONE: Record<ContractStatus, string> = {
  draft: 'text-parchment-muted border-parchment-muted/40',
  sent: 'text-parchment-muted border-parchment-muted/40',
  signed: 'text-accent border-accent/60',
  terminated: 'text-red-300/80 border-red-400/30',
};

function formatDate(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

function formatRoyalty(rate: number | null): string {
  if (rate == null) return '—';
  return `${(rate * 100).toFixed(0)}%`;
}

function formatAdvance(amount: string | null, currency: string): string {
  if (!amount) return '—';
  return `${currency} ${Number(amount).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function ContractsPanel({ contracts }: ContractsPanelProps) {
  return (
    <SidebarSection
      title="Contracts"
      meta={contracts.length === 0 ? 'None' : `${contracts.length} on file`}
    >
      {contracts.length === 0 ? (
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
          No contracts drafted yet.
        </p>
      ) : (
        <ul className="flex flex-col gap-5">
          {contracts.map((c) => (
            <li key={c.id} className="border-t border-rule pt-4 first:border-t-0 first:pt-0">
              <div className="flex items-center justify-between">
                <span
                  className={`inline-flex items-center border ${STATUS_TONE[c.status]} px-2 py-0.5 font-mono text-[0.6rem] uppercase tracking-widest`}
                >
                  {CONTRACT_STATUS_LABEL[c.status]}
                </span>
                <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                  {formatDate(c.signed_at)}
                </span>
              </div>

              <dl className="mt-3 grid grid-cols-[auto,1fr] gap-x-4 gap-y-2 text-sm">
                <dt className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                  Advance
                </dt>
                <dd className="font-serif text-parchment">
                  {formatAdvance(c.advance_amount, c.currency)}
                </dd>
                <dt className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                  Royalty
                </dt>
                <dd className="font-serif text-parchment">{formatRoyalty(c.royalty_rate)}</dd>
                {c.rights_territory && (
                  <>
                    <dt className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
                      Territory
                    </dt>
                    <dd className="font-mono text-[0.78rem] uppercase tracking-wider text-parchment">
                      {c.rights_territory}
                    </dd>
                  </>
                )}
              </dl>

              {c.terms && (
                <p className="mt-3 font-serif text-[0.85rem] italic leading-relaxed text-parchment-muted">
                  {c.terms}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </SidebarSection>
  );
}
