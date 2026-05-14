import { useState } from 'react';
import { AppShell, type AppView } from '@/layouts/AppShell';
import { AuthProvider } from '@/auth/AuthContext';
import { Dashboard } from '@/pages/Dashboard';
import { ManuscriptView } from '@/pages/ManuscriptView';
import { SearchPage } from '@/pages/SearchPage';
import { ArchivePage } from '@/pages/ArchivePage';

type View =
  | { name: 'dashboard' }
  | { name: 'manuscript'; id: string }
  | { name: 'search' }
  | { name: 'archive' };

export default function App() {
  const [view, setView] = useState<View>({ name: 'dashboard' });

  const openManuscript = (id: string) => setView({ name: 'manuscript', id });
  const navigate = (target: AppView) => {
    if (target === 'manuscript') return;
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
          />
        )}
        {view.name === 'search' && (
          <SearchPage onOpenManuscript={openManuscript} />
        )}
        {view.name === 'archive' && (
          <ArchivePage onOpenManuscript={openManuscript} />
        )}
      </AppShell>
    </AuthProvider>
  );
}
