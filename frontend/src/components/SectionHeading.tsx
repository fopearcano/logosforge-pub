import type { ReactNode } from 'react';
import { Eyebrow } from './Eyebrow';

interface SectionHeadingProps {
  eyebrow: string;
  title: string;
  meta?: ReactNode;
}

export function SectionHeading({ eyebrow, title, meta }: SectionHeadingProps) {
  return (
    <header className="flex flex-wrap items-baseline justify-between gap-3">
      <div>
        <Eyebrow>{eyebrow}</Eyebrow>
        <h3 className="mt-2 font-serif text-2xl leading-tight text-parchment">
          {title}
        </h3>
      </div>
      {meta && (
        <span className="font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
          {meta}
        </span>
      )}
    </header>
  );
}
