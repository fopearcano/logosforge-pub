import type { ReactNode } from 'react';
import { Eyebrow } from '@/components/Eyebrow';
import { LoginPanel } from '@/components/LoginPanel';

export type AppView = 'dashboard' | 'manuscript' | 'search' | 'archive';

interface AppShellProps {
  children: ReactNode;
  onNavigate: (view: AppView) => void;
  activeView: AppView;
}

interface NavLinkProps {
  label: string;
  active: boolean;
  onClick: () => void;
}

function NavLink({ label, active, onClick }: NavLinkProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        active
          ? 'text-parchment'
          : 'text-parchment-dim transition-colors hover:text-parchment-muted'
      }
    >
      {label}
    </button>
  );
}

export function AppShell({ children, onNavigate, activeView }: AppShellProps) {
  return (
    <div className="min-h-full bg-ink-800">
      <header className="border-b border-rule">
        <div className="mx-auto flex max-w-editorial flex-wrap items-end justify-between gap-6 px-10 pb-6 pt-10">
          <button
            type="button"
            onClick={() => onNavigate('dashboard')}
            className="flex flex-col items-start gap-2 text-left transition-opacity hover:opacity-90 focus:outline-none"
          >
            <Eyebrow>Editio · MMXXVI</Eyebrow>
            <span className="font-serif text-3xl text-parchment">
              LOGOSFORGE
              <span className="ml-3 align-middle font-mono text-[0.65rem] uppercase tracking-widest text-parchment-dim">
                v0.1
              </span>
            </span>
          </button>

          <div className="flex items-center gap-8">
            <nav className="hidden items-center gap-7 font-mono text-[0.72rem] uppercase tracking-widest sm:flex">
              <NavLink
                label="Manuscripts"
                active={activeView === 'dashboard' || activeView === 'manuscript'}
                onClick={() => onNavigate('dashboard')}
              />
              <NavLink
                label="Search"
                active={activeView === 'search'}
                onClick={() => onNavigate('search')}
              />
              <NavLink
                label="Archive"
                active={activeView === 'archive'}
                onClick={() => onNavigate('archive')}
              />
              <span className="text-parchment-dim/60">Authors</span>
              <span className="text-parchment-dim/60">Production</span>
            </nav>

            <LoginPanel />
          </div>
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
