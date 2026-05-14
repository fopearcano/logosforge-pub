import { useEffect, useState } from 'react';
import { Eyebrow } from './Eyebrow';
import { ApiError } from '@/api/client';
import { fetchNeighborhood } from '@/api/knowledge';
import {
  ENTITY_KIND_LABEL,
  RELATIONSHIP_KIND_LABEL,
  type NeighborhoodNode,
  type NeighborhoodResult,
} from '@/types/knowledge';

interface RelationshipPreviewProps {
  entityId: string;
  entityName: string;
}

/**
 * A text-mode neighborhood placeholder.
 *
 * The eventual graph view will live elsewhere; this preview is a
 * library-card register of an entity's first-hop relationships,
 * suitable for the manuscript sidebar.
 */
export function RelationshipPreview({
  entityId,
  entityName,
}: RelationshipPreviewProps) {
  const [data, setData] = useState<NeighborhoodResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchNeighborhood(entityId, 1)
      .then((result) => {
        if (cancelled) return;
        setData(result);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof ApiError ? e.message : 'Failed to load.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [entityId]);

  if (loading) {
    return (
      <p className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
        Loading neighbourhood…
      </p>
    );
  }

  if (error) {
    return (
      <p className="font-mono text-[0.62rem] uppercase tracking-widest text-signal">
        {error}
      </p>
    );
  }

  if (!data) return null;

  const nodes = new Map<string, NeighborhoodNode>();
  for (const n of data.nodes) nodes.set(n.id, n);

  const neighbours = data.edges.map((edge) => {
    const other =
      edge.source_id === entityId
        ? nodes.get(edge.target_id)
        : nodes.get(edge.source_id);
    const direction = edge.source_id === entityId ? 'out' : 'in';
    return { edge, other, direction };
  });

  if (neighbours.length === 0) {
    return (
      <p className="font-serif text-[0.85rem] italic text-parchment-muted">
        {entityName} has no relationships on file yet.
      </p>
    );
  }

  return (
    <div>
      <div className="flex items-baseline justify-between">
        <Eyebrow>Neighbourhood · 1 hop</Eyebrow>
        <span className="font-mono text-[0.6rem] uppercase tracking-widest text-parchment-dim">
          {neighbours.length} {neighbours.length === 1 ? 'edge' : 'edges'}
        </span>
      </div>

      <ul className="mt-3 flex flex-col gap-2">
        {neighbours.map(({ edge, other, direction }) => (
          <li
            key={edge.id}
            className="border-l border-rule pl-3 font-mono text-[0.68rem] uppercase tracking-wider text-parchment-muted"
          >
            <span className="text-parchment-dim">
              {direction === 'out' ? '→ ' : '← '}
            </span>
            <span className="text-accent/90">
              {RELATIONSHIP_KIND_LABEL[edge.kind]}
            </span>
            <span className="text-parchment-dim"> · </span>
            <span className="font-serif text-[0.85rem] text-parchment normal-case tracking-normal">
              {other?.name ?? '—'}
            </span>
            {other?.kind && (
              <span className="ml-2 text-parchment-dim/80">
                ({ENTITY_KIND_LABEL[other.kind]})
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
