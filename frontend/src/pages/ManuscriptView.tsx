import { useCallback, useEffect, useState } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { StatusBadge } from '@/components/StatusBadge';
import { EditableField } from '@/components/EditableField';
import { WorkflowTimeline } from '@/components/WorkflowTimeline';
import { TransitionControl } from '@/components/TransitionControl';
import { MetadataPanel } from '@/components/MetadataPanel';
import { AuthorPanel } from '@/components/AuthorPanel';
import { ContractsPanel } from '@/components/ContractsPanel';
import { ProductionPanel } from '@/components/ProductionPanel';
import { ProductionRecordPanel } from '@/components/ProductionRecordPanel';
import { ReviewsList } from '@/components/ReviewsList';
import { EditorialNotesPanel } from '@/components/EditorialNotesPanel';
import { AttachmentsPanel } from '@/components/AttachmentsPanel';
import { AIPanel } from '@/components/AIPanel';
import { ExportMenu } from '@/components/ExportMenu';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import {
  fetchAuthor,
  fetchContracts,
  fetchEditorialNotes,
  fetchManuscript,
  fetchProductionItems,
  fetchReviews,
  fetchTransitionsMap,
  fetchWorkflowHistory,
  patchManuscript,
  type ManuscriptPatch,
} from '@/api/manuscripts';
import { fetchProductionRecordByManuscript } from '@/api/productionRecords';
import type { Author, Manuscript } from '@/types/manuscript';
import type {
  Contract,
  EditorialNote,
  ProductionItem,
  Review,
} from '@/types/editorial';
import type { ProductionRecord } from '@/types/production';
import type {
  TransitionResponse,
  TransitionsMap,
  WorkflowEvent,
} from '@/types/workflow';

interface ManuscriptViewProps {
  manuscriptId: string;
  onBack: () => void;
  onOpenProductionItem?: (id: string) => void;
}

export function ManuscriptView({
  manuscriptId,
  onBack,
  onOpenProductionItem,
}: ManuscriptViewProps) {
  const { status: authStatus } = useAuth();
  const authedAndEditable = authStatus === 'authenticated';

  const [manuscript, setManuscript] = useState<Manuscript | null>(null);
  const [author, setAuthor] = useState<Author | null>(null);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [productionItems, setProductionItems] = useState<ProductionItem[]>([]);
  const [editorialNotes, setEditorialNotes] = useState<EditorialNote[]>([]);
  const [productionRecord, setProductionRecord] =
    useState<ProductionRecord | null>(null);
  const [transitions, setTransitions] = useState<TransitionsMap | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [
        m,
        history,
        map,
        reviewsPage,
        contractsPage,
        productionPage,
        notesPage,
      ] = await Promise.all([
        fetchManuscript(manuscriptId),
        fetchWorkflowHistory(manuscriptId),
        fetchTransitionsMap(),
        fetchReviews(manuscriptId),
        fetchContracts(manuscriptId),
        fetchProductionItems(manuscriptId),
        fetchEditorialNotes(manuscriptId),
      ]);
      setManuscript(m);
      setEvents(history);
      setTransitions(map);
      setReviews(reviewsPage.items);
      setContracts(contractsPage.items);
      setProductionItems(productionPage.items);
      setEditorialNotes(notesPage.items);

      // Production record is 1:1 with the manuscript; a 404 means none
      // has been opened yet, which is a normal state.
      const record = await fetchProductionRecordByManuscript(manuscriptId)
        .catch((err: unknown) => {
          if (err instanceof ApiError && err.status === 404) return null;
          throw err;
        });
      setProductionRecord(record);

      const a = await fetchAuthor(m.author_id).catch(() => null);
      setAuthor(a);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load manuscript.');
    }
  }, [manuscriptId]);

  useEffect(() => {
    setManuscript(null);
    setAuthor(null);
    setEvents([]);
    setReviews([]);
    setContracts([]);
    setProductionItems([]);
    setEditorialNotes([]);
    setProductionRecord(null);
    void load();
  }, [load]);

  const handleTransition = (response: TransitionResponse) => {
    setManuscript((prev) =>
      prev ? { ...prev, status: response.status } : prev,
    );
    setEvents((prev) => [...prev, response.event]);
  };

  const handlePatch = async (patch: ManuscriptPatch) => {
    if (!manuscript) return;
    const updated = await patchManuscript(manuscript.id, patch);
    setManuscript(updated);
  };

  const handleNoteCreated = (note: EditorialNote) => {
    setEditorialNotes((prev) => [note, ...prev]);
  };

  if (error) {
    return (
      <div>
        <button
          type="button"
          onClick={onBack}
          className="mb-8 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment"
        >
          ← Back to manuscripts
        </button>
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-signal">
          {error}
        </p>
      </div>
    );
  }

  if (!manuscript || !transitions) {
    return (
      <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
        Loading…
      </p>
    );
  }

  const allowedNext = transitions[manuscript.status] ?? [];
  const archived = manuscript.status === 'archived';
  const canEdit = authedAndEditable && !archived;

  return (
    <div>
      <button
        type="button"
        onClick={onBack}
        className="font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment"
      >
        ← Back to manuscripts
      </button>

      {archived && (
        <div className="mt-6 flex items-center justify-between border border-rule bg-ink-700/40 px-6 py-3">
          <span className="font-mono text-[0.68rem] uppercase tracking-widest text-parchment-muted">
            Archive · read-only
          </span>
          <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
            Editing, transitions, and new notes are disabled.
          </span>
        </div>
      )}

      <header className="mt-6 flex flex-col gap-4 border-b border-rule pb-10">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <Eyebrow>{manuscript.genre ?? 'Untitled folio'}</Eyebrow>
          <ExportMenu manuscriptId={manuscript.id} />
        </div>

        <EditableField
          value={manuscript.title}
          canEdit={canEdit}
          onSave={(v) =>
            v.trim()
              ? handlePatch({ title: v.trim() })
              : Promise.reject(new Error('Title cannot be empty.'))
          }
          displayClassName="font-serif text-4xl leading-tight text-parchment"
          inputClassName="font-serif text-2xl text-parchment"
        />

        <EditableField
          value={manuscript.subtitle ?? ''}
          canEdit={canEdit}
          placeholder="Subtitle (optional)"
          emptyLabel={canEdit ? 'Add subtitle…' : ''}
          onSave={(v) => handlePatch({ subtitle: v.trim() || null })}
          displayClassName="font-serif text-xl italic text-parchment-muted"
          inputClassName="font-serif italic text-parchment-muted"
        />

        <div className="mt-2 flex flex-wrap items-center gap-x-6 gap-y-2 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim">
          {author && <span>By {author.full_name}</span>}
          {manuscript.word_count != null && (
            <span>{manuscript.word_count.toLocaleString()} words</span>
          )}
          <span>{manuscript.language.toUpperCase()}</span>
        </div>

        <div className="mt-2">
          <StatusBadge status={manuscript.status} />
        </div>
      </header>

      <section className="mt-12 max-w-prose">
        <Eyebrow>Synopsis</Eyebrow>
        <div className="mt-4 font-serif text-[1.05rem] leading-relaxed text-parchment/90">
          <EditableField
            value={manuscript.synopsis ?? ''}
            canEdit={canEdit}
            type="multiline"
            placeholder="Write a short synopsis…"
            emptyLabel={canEdit ? 'Add a synopsis…' : 'No synopsis recorded.'}
            onSave={(v) => handlePatch({ synopsis: v.trim() || null })}
            inputClassName="font-serif text-[1.05rem] leading-relaxed text-parchment/90"
          />
        </div>
      </section>

      <div className="mt-16 grid grid-cols-1 gap-16 lg:grid-cols-[2fr,1fr]">
        <div className="flex flex-col gap-20">
          <section>
            <div className="flex items-baseline justify-between">
              <Eyebrow>Workflow chronicle</Eyebrow>
              <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                {events.length} {events.length === 1 ? 'entry' : 'entries'}
              </span>
            </div>
            <div className="mt-8">
              <WorkflowTimeline events={events} />
            </div>
          </section>

          <EditorialNotesPanel
            manuscriptId={manuscript.id}
            notes={editorialNotes}
            readOnly={archived}
            onCreate={handleNoteCreated}
          />

          <ReviewsList reviews={reviews} />
        </div>

        <aside className="flex flex-col gap-8">
          <MetadataPanel
            manuscript={manuscript}
            canEdit={canEdit}
            onPatch={handlePatch}
          />
          <AuthorPanel author={author} />
          <TransitionControl
            manuscriptId={manuscript.id}
            currentStatus={manuscript.status}
            allowedNext={allowedNext}
            onTransition={handleTransition}
          />
          <ProductionRecordPanel
            manuscriptId={manuscript.id}
            record={productionRecord}
            canEdit={canEdit}
            onChange={setProductionRecord}
          />
          <ContractsPanel contracts={contracts} />
          <ProductionPanel
            items={productionItems}
            onOpenItem={onOpenProductionItem}
          />
          <AIPanel manuscriptId={manuscript.id} readOnly={archived} />
          <AttachmentsPanel manuscriptId={manuscript.id} readOnly={archived} />
        </aside>
      </div>
    </div>
  );
}
