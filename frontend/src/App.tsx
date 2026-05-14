import { useState } from 'react';
import { AppShell } from '@/layouts/AppShell';
import { AuthProvider } from '@/auth/AuthContext';
import { Dashboard } from '@/pages/Dashboard';
import { ManuscriptView } from '@/pages/ManuscriptView';

type View = { name: 'dashboard' } | { name: 'manuscript'; id: string };

export default function App() {
  const [view, setView] = useState<View>({ name: 'dashboard' });

  return (
    <AuthProvider>
      <AppShell
        onHome={() => setView({ name: 'dashboard' })}
        activeView={view.name}
      >
        {view.name === 'dashboard' ? (
          <Dashboard
            onOpenManuscript={(id) => setView({ name: 'manuscript', id })}
          />
        ) : (
          <ManuscriptView
            manuscriptId={view.id}
            onBack={() => setView({ name: 'dashboard' })}
          />
        )}
      </AppShell>
    </AuthProvider>
  );
}
