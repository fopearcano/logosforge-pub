import { useAuth } from '@/auth/AuthContext';
import { EditableField } from './EditableField';
import { SidebarSection } from './SidebarSection';
import type { Manuscript } from '@/types/manuscript';
import type { ManuscriptPatch } from '@/api/manuscripts';

interface MetadataPanelProps {
  manuscript: Manuscript;
  onPatch: (patch: ManuscriptPatch) => Promise<void>;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  });
}

export function MetadataPanel({ manuscript, onPatch }: MetadataPanelProps) {
  const { status } = useAuth();
  const canEdit = status === 'authenticated';

  return (
    <SidebarSection title="Metadata">
      <dl className="grid grid-cols-[auto,1fr] gap-x-6 gap-y-4 text-sm">
        <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Genre
        </dt>
        <dd className="font-serif text-parchment">
          <EditableField
            value={manuscript.genre ?? ''}
            canEdit={canEdit}
            placeholder="Genre"
            emptyLabel="Unassigned"
            onSave={(v) => onPatch({ genre: v.trim() || null })}
          />
        </dd>

        <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Language
        </dt>
        <dd className="font-serif text-parchment">
          <EditableField
            value={manuscript.language}
            canEdit={canEdit}
            placeholder="en"
            onSave={(v) => onPatch({ language: v.trim() || 'en' })}
          />
        </dd>

        <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Word count
        </dt>
        <dd className="font-serif text-parchment">
          <EditableField
            value={manuscript.word_count?.toString() ?? ''}
            canEdit={canEdit}
            type="number"
            placeholder="0"
            emptyLabel="Unrecorded"
            onSave={async (v) => {
              if (v.trim() === '') {
                await onPatch({ word_count: null });
                return;
              }
              const n = Number(v);
              if (!Number.isFinite(n) || n < 0) {
                throw new Error('Word count must be a positive number.');
              }
              await onPatch({ word_count: Math.round(n) });
            }}
          />
        </dd>

        <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Created
        </dt>
        <dd className="font-mono text-[0.72rem] uppercase tracking-wider text-parchment-muted">
          {formatDate(manuscript.created_at)}
        </dd>

        <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Updated
        </dt>
        <dd className="font-mono text-[0.72rem] uppercase tracking-wider text-parchment-muted">
          {formatDate(manuscript.updated_at)}
        </dd>
      </dl>
    </SidebarSection>
  );
}
