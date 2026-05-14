import { STATUS_LABELS, WORKFLOW_STATUSES, type WorkflowStatus } from '@/types/workflow';
import type { StatusCount } from '@/types/dashboard';

interface StatusCountsTableProps {
  counts: StatusCount[];
}

export function StatusCountsTable({ counts }: StatusCountsTableProps) {
  const by_status = new Map<WorkflowStatus, number>(
    counts.map((c) => [c.status, c.count]),
  );
  const max = Math.max(1, ...counts.map((c) => c.count));

  return (
    <table className="w-full border-collapse">
      <tbody>
        {WORKFLOW_STATUSES.map((status) => {
          const value = by_status.get(status) ?? 0;
          const ratio = value / max;
          return (
            <tr key={status} className="border-t border-rule">
              <td className="w-1/3 py-2.5 pr-4 font-serif text-[0.95rem] text-parchment">
                {STATUS_LABELS[status]}
              </td>
              <td className="py-2.5 pr-4">
                <div className="h-px w-full bg-rule">
                  {value > 0 && (
                    <div
                      className="h-px bg-accent"
                      style={{ width: `${ratio * 100}%` }}
                    />
                  )}
                </div>
              </td>
              <td className="w-12 py-2.5 text-right font-mono text-[0.85rem] text-parchment">
                {value}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
