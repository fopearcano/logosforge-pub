import { SidebarSection } from './SidebarSection';

export function AttachmentsPlaceholder() {
  return (
    <SidebarSection title="Manuscript files" meta="Not yet enabled">
      <p className="font-serif text-sm italic leading-relaxed text-parchment-muted">
        Drafts, proofs, and cover artwork will live here. The archive
        intake is still being plumbed.
      </p>

      <ul className="mt-4 flex flex-col gap-2 font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
        <li className="flex items-center justify-between border-b border-rule pb-2">
          <span>Manuscript draft</span>
          <span>—</span>
        </li>
        <li className="flex items-center justify-between border-b border-rule pb-2">
          <span>Editor's marked copy</span>
          <span>—</span>
        </li>
        <li className="flex items-center justify-between">
          <span>Cover artwork</span>
          <span>—</span>
        </li>
      </ul>

      <button
        type="button"
        disabled
        className="mt-5 w-full border border-rule px-3 py-2 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim opacity-60"
        title="File attachments are not yet implemented."
      >
        Attach file
      </button>
    </SidebarSection>
  );
}
