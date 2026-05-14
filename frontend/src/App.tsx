import { useState } from 'react';
import { AppShell, type AppView } from '@/layouts/AppShell';
import { AuthProvider } from '@/auth/AuthContext';
import { Dashboard } from '@/pages/Dashboard';
import { ManuscriptView } from '@/pages/ManuscriptView';
import { SearchPage } from '@/pages/SearchPage';
import { ArchivePage } from '@/pages/ArchivePage';
import { ProductionBoard } from '@/pages/ProductionBoard';
import { ReleaseCalendar } from '@/pages/ReleaseCalendar';
import { ProductionItemView } from '@/pages/ProductionItemView';

type View =
  | { name: 'dashboard' }
  | { name: 'manuscript'; id: string }
  | { name: 'search' }
  | { name: 'archive' }
  | { name: 'production' }
  | { name: 'calendar' }
  | { name: 'production-item'; id: string };

export default function App() {
  const [view, setView] = useState<View>({ name: 'dashboard' });

  const openManuscript = (id: string) => setView({ name: 'manuscript', id });
  const openProductionItem = (id: string) =>
    setView({ name: 'production-item', id });

  const navigate = (target: AppView) => {
    if (target === 'manuscript' || target === 'production-item') return;
    setView({ name: target } as View);
  };

  return (
    <AuthProvider>
      <AppShell onNavigate={navigate} activeView={view.name}>
        {view.name === 'dashboard' && (
          <Dashboard onOpenManuscript={openManuscript} />
        )}
        {view.name === 'manuscript' && (
          <ManuscriptView
            manuscriptId={view.id}
            onBack={() => setView({ name: 'dashboard' })}
            onOpenProductionItem={openProductionItem}
          />
        )}
        {view.name === 'search' && (
          <SearchPage onOpenManuscript={openManuscript} />
        )}
        {view.name === 'archive' && (
          <ArchivePage onOpenManuscript={openManuscript} />
        )}
        {view.name === 'production' && (
          <ProductionBoard onOpenManuscript={openManuscript} />
        )}
        {view.name === 'calendar' && (
          <ReleaseCalendar onOpenManuscript={openManuscript} />
        )}
        {view.name === 'production-item' && (
          <ProductionItemView
            itemId={view.id}
            onBack={() => setView({ name: 'production' })}
            onOpenManuscript={openManuscript}
          />
        )}
      </AppShell>
    </AuthProvider>
  );
}
