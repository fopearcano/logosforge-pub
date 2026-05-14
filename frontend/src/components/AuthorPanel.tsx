import { SidebarSection } from './SidebarSection';
import type { Author } from '@/types/manuscript';

interface AuthorPanelProps {
  author: Author | null;
}

export function AuthorPanel({ author }: AuthorPanelProps) {
  if (!author) {
    return (
      <SidebarSection title="Author">
        <p className="font-mono text-[0.7rem] uppercase tracking-widest text-parchment-dim">
          Author record unavailable.
        </p>
      </SidebarSection>
    );
  }

  return (
    <SidebarSection title="Author">
      <p className="font-serif text-lg text-parchment">{author.full_name}</p>
      <dl className="mt-4 grid grid-cols-[auto,1fr] gap-x-6 gap-y-3 text-sm">
        {author.country && (
          <>
            <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              Country
            </dt>
            <dd className="font-serif text-parchment-muted">{author.country}</dd>
          </>
        )}
        {author.email && (
          <>
            <dt className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
              Email
            </dt>
            <dd className="break-all font-mono text-[0.72rem] tracking-wide text-parchment-muted">
              {author.email}
            </dd>
          </>
        )}
      </dl>
      {author.biography && (
        <p className="mt-4 max-w-prose font-serif text-sm italic leading-relaxed text-parchment-muted">
          {author.biography}
        </p>
      )}
    </SidebarSection>
  );
}
