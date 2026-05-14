import type { ReactNode } from 'react';
import { Eyebrow } from '@/components/Eyebrow';

interface AppShellProps {
  children: ReactNode;
}

const NAV = [
  { label: 'Dashboard', active: true },
  { label: 'Catalogue', active: false },
  { label: 'Manuscripts', active: false },
  { label: 'Authors', active: false },
  { label: 'Production', active: false },
  { label: 'Archive', active: false },
];

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-full bg-ink-800">
      <header className="border-b border-rule">
        <div className="mx-auto flex max-w-editorial items-end justify-between px-10 pb-6 pt-10">
          <div className="flex flex-col gap-2">
            <Eyebrow>Editio · MMXXVI</Eyebrow>
            <h1 className="font-serif text-3xl text-parchment">
              LOGOSFORGE
              <span className="ml-3 align-middle font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                v0.1
              </span>
            </h1>
          </div>
          <nav className="flex items-center gap-7 font-mono text-[0.72rem] uppercase tracking-widest">
            {NAV.map((item) => (
              <span
                key={item.label}
                className={
                  item.active
                    ? 'text-parchment'
                    : 'text-parchment-dim transition-colors hover:text-parchment-muted'
                }
              >
                {item.label}
              </span>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-editorial px-10 py-14">{children}</main>

      <footer className="mt-24 border-t border-rule">
        <div className="mx-auto flex max-w-editorial items-center justify-between px-10 py-6 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim">
          <span>Locally hosted · SQLite</span>
          <span>Editorial Office · Folio I</span>
        </div>
      </footer>
    </div>
  );
}
