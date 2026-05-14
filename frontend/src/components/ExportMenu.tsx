import { manuscriptExportUrl } from '@/api/exports';
import { Eyebrow } from './Eyebrow';

interface ExportMenuProps {
  manuscriptId: string;
}

export function ExportMenu({ manuscriptId }: ExportMenuProps) {
  return (
    <div className="flex flex-col gap-2 sm:items-end">
      <Eyebrow>Export</Eyebrow>
      <div className="flex items-center gap-3 font-mono text-[0.65rem] uppercase tracking-widest">
        <a
          href={manuscriptExportUrl(manuscriptId, 'markdown')}
          className="border border-rule px-3 py-1 text-parchment-muted transition-colors hover:border-accent hover:text-accent"
        >
          Markdown
        </a>
        <a
          href={manuscriptExportUrl(manuscriptId, 'json')}
          className="border border-rule px-3 py-1 text-parchment-muted transition-colors hover:border-accent hover:text-accent"
        >
          JSON
        </a>
        <span
          className="border border-rule/40 px-3 py-1 text-parchment-dim/60"
          title="PDF export is not yet implemented."
        >
          PDF · soon
        </span>
      </div>
    </div>
  );
}
