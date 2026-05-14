import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { Eyebrow } from './Eyebrow';
import { RelationshipPreview } from './RelationshipPreview';
import { SidebarSection } from './SidebarSection';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import {
  createManuscriptLink,
  deleteManuscriptLink,
  fetchEntities,
  fetchManuscriptLinks,
} from '@/api/knowledge';
import {
  ENTITY_KIND_LABEL,
  MANUSCRIPT_LINK_ROLES,
  MANUSCRIPT_LINK_ROLE_LABEL,
  type KnowledgeEntity,
  type ManuscriptEntityLink,
  type ManuscriptLinkRole,
} from '@/types/knowledge';

interface SemanticPanelProps {
  manuscriptId: string;
  readOnly?: boolean;
}

const ROLE_ORDER: ManuscriptLinkRole[] = [
  'tagged',
  'features',
  'references',
  'set_in',
  'derived_from',
  'other',
];

export function SemanticPanel({
  manuscriptId,
  readOnly = false,
}: SemanticPanelProps) {
  const { status } = useAuth();
  const authed = !readOnly && status === 'authenticated';

  const [links, setLinks] = useState<ManuscriptEntityLink[] | null>(null);
  const [entities, setEntities] = useState<KnowledgeEntity[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [adding, setAdding] = useState(false);
  const [draftEntity, setDraftEntity] = useState('');
  const [draftRole, setDraftRole] = useState<ManuscriptLinkRole>('tagged');
  const [submitting, setSubmitting] = useState(false);

  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetchManuscriptLinks(manuscriptId),
      fetchEntities({ limit: 200 }),
    ])
      .then(([linkRows, entityPage]) => {
        if (cancelled) return;
        setLinks(linkRows);
        setEntities(entityPage.items);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof ApiError ? e.message : 'Failed to load.');
      });
    return () => {
      cancelled = true;
    };
  }, [manuscriptId]);

  const grouped = useMemo(() => {
    const result: Record<ManuscriptLinkRole, ManuscriptEntityLink[]> = {
      tagged: [],
      features: [],
      references: [],
      set_in: [],
      derived_from: [],
      other: [],
    };
    for (const link of links ?? []) {
      result[link.role].push(link);
    }
    return result;
  }, [links]);

  const handleAdd = async (event: FormEvent) => {
    event.preventDefault();
    if (!authed || !draftEntity) return;
    setSubmitting(true);
    setError(null);
    try {
      const created = await createManuscriptLink(manuscriptId, {
        entity_id: draftEntity,
        role: draftRole,
      });
      setLinks((prev) => [created, ...(prev ?? [])]);
      setAdding(false);
      setDraftEntity('');
      setDraftRole('tagged');
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not link entity.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemove = async (link: ManuscriptEntityLink) => {
    if (!authed) return;
    try {
      await deleteManuscriptLink(manuscriptId, link.id);
      setLinks((prev) => prev?.filter((l) => l.id !== link.id) ?? null);
      if (selected === link.entity_id) setSelected(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Could not remove link.');
    }
  };

  const totalLinks = links?.length ?? 0;
  const linkedEntityIds = new Set(links?.map((l) => l.entity_id) ?? []);
  const candidateEntities = entities.filter((e) => !linkedEntityIds.has(e.id));
  const selectedLink = links?.find((l) => l.entity_id === selected) ?? null;

  return (
    <SidebarSection
      title="Semantic web"
      meta={
        links === null
          ? '—'
          : totalLinks === 0
            ? 'None linked'
            : `${totalLinks} link${totalLinks === 1 ? '' : 's'}`
      }
    >
      <p className="font-serif text-[0.9rem] italic leading-relaxed text-parchment-muted">
        Tag this manuscript with knowledge entities — themes, motifs,
        places, persons. Tap an entity to inspect its neighbourhood.
      </p>

      {error && (
        <p className="mt-3 font-mono text-[0.62rem] uppercase tracking-widest text-signal">
          {error}
        </p>
      )}

      {links !== null && totalLinks === 0 && !adding && (
        <p className="mt-4 font-serif text-[0.88rem] italic leading-relaxed text-parchment-muted">
          No entities linked to this manuscript yet.
        </p>
      )}

      {totalLinks > 0 && (
        <div className="mt-5 flex flex-col gap-5">
          {ROLE_ORDER.map((role) => {
            const items = grouped[role];
            if (items.length === 0) return null;
            return (
              <div key={role}>
                <Eyebrow>{MANUSCRIPT_LINK_ROLE_LABEL[role]}</Eyebrow>
                <div className="mt-2 flex flex-wrap gap-2">
                  {items.map((link) => {
                    const isSelected = selected === link.entity_id;
                    return (
                      <span
                        key={link.id}
                        className={`inline-flex items-center gap-1 border px-2 py-0.5 font-mono text-[0.62rem] uppercase tracking-widest transition-colors ${
                          isSelected
                            ? 'border-accent text-accent'
                            : 'border-rule text-parchment-muted hover:border-parchment-muted/60'
                        }`}
                      >
                        <button
                          type="button"
                          onClick={() =>
                            setSelected(isSelected ? null : link.entity_id)
                          }
                          className="text-left"
                          title={
                            link.entity_kind
                              ? ENTITY_KIND_LABEL[link.entity_kind]
                              : undefined
                          }
                        >
                          {link.entity_name ?? '—'}
                        </button>
                        {authed && (
                          <button
                            type="button"
                            onClick={() => void handleRemove(link)}
                            className="text-parchment-dim hover:text-signal"
                            aria-label={`Remove link to ${link.entity_name}`}
                          >
                            ×
                          </button>
                        )}
                      </span>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedLink && selectedLink.entity_name && (
        <div className="mt-6 border-t border-rule pt-4">
          <RelationshipPreview
            entityId={selectedLink.entity_id}
            entityName={selectedLink.entity_name}
          />
        </div>
      )}

      {!adding && (
        <button
          type="button"
          onClick={() => setAdding(true)}
          disabled={!authed || candidateEntities.length === 0}
          className="mt-5 w-full border border-rule px-3 py-2 font-mono text-[0.62rem] uppercase tracking-widest text-parchment-muted transition-colors hover:border-accent hover:text-accent disabled:cursor-not-allowed disabled:opacity-50"
          title={
            readOnly
              ? 'Archived · read-only'
              : !authed
                ? 'Sign in to link entities'
                : undefined
          }
        >
          {readOnly
            ? 'Archived · read-only'
            : !authed
              ? 'Sign in to link entities'
              : candidateEntities.length === 0
                ? 'No entities available'
                : 'Link an entity…'}
        </button>
      )}

      {adding && (
        <form onSubmit={handleAdd} className="mt-5 flex flex-col gap-3">
          <label className="flex flex-col gap-1">
            <span className="font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
              Entity
            </span>
            <select
              value={draftEntity}
              onChange={(e) => setDraftEntity(e.target.value)}
              required
              className="border border-rule bg-ink-800 px-3 py-1.5 font-serif text-[0.9rem] text-parchment focus:border-accent focus:outline-none"
            >
              <option value="">Choose an entity…</option>
              {candidateEntities.map((entity) => (
                <option key={entity.id} value={entity.id}>
                  {entity.name} · {ENTITY_KIND_LABEL[entity.kind]}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-1">
            <span className="font-mono text-[0.58rem] uppercase tracking-widest text-parchment-dim">
              Role
            </span>
            <select
              value={draftRole}
              onChange={(e) => setDraftRole(e.target.value as ManuscriptLinkRole)}
              className="border border-rule bg-ink-800 px-3 py-1.5 font-mono text-[0.72rem] uppercase tracking-wider text-parchment focus:border-accent focus:outline-none"
            >
              {MANUSCRIPT_LINK_ROLES.map((role) => (
                <option key={role} value={role}>
                  {MANUSCRIPT_LINK_ROLE_LABEL[role]}
                </option>
              ))}
            </select>
          </label>

          <div className="flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => {
                setAdding(false);
                setError(null);
              }}
              disabled={submitting}
              className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim hover:text-parchment-muted"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !draftEntity}
              className="border border-accent px-3 py-1 font-mono text-[0.62rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:opacity-40"
            >
              {submitting ? 'Linking…' : 'Link'}
            </button>
          </div>
        </form>
      )}
    </SidebarSection>
  );
}
