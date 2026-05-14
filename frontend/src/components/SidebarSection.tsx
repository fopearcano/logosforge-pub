import type { ReactNode } from 'react';
import { Eyebrow } from './Eyebrow';

interface SidebarSectionProps {
  title: string;
  meta?: ReactNode;
  children: ReactNode;
}

export function SidebarSection({ title, meta, children }: SidebarSectionProps) {
  return (
    <section className="border border-rule p-6">
      <div className="flex items-baseline justify-between gap-3">
        <Eyebrow>{title}</Eyebrow>
        {meta && (
          <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
            {meta}
          </span>
        )}
      </div>
      <div className="mt-5">{children}</div>
    </section>
  );
}
