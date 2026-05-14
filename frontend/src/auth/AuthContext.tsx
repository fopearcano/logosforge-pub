import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { fetchMe, login as apiLogin } from '@/api/auth';
import { TOKEN_STORAGE_KEY } from '@/api/client';
import type { CurrentUser } from '@/types/auth';

interface AuthState {
  user: CurrentUser | null;
  status: 'idle' | 'loading' | 'authenticated' | 'anonymous';
  signIn: (email: string, password: string) => Promise<CurrentUser>;
  signOut: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

function readStoredToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeToken(token: string | null): void {
  try {
    if (token) window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
    else window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch {
    /* private mode etc. */
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [status, setStatus] = useState<AuthState['status']>('idle');

  useEffect(() => {
    const token = readStoredToken();
    if (!token) {
      setStatus('anonymous');
      return;
    }
    setStatus('loading');
    let cancelled = false;
    fetchMe()
      .then((me) => {
        if (cancelled) return;
        setUser(me);
        setStatus('authenticated');
      })
      .catch(() => {
        if (cancelled) return;
        writeToken(null);
        setUser(null);
        setStatus('anonymous');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const response = await apiLogin(email, password);
    writeToken(response.access_token);
    setUser(response.user);
    setStatus('authenticated');
    return response.user;
  }, []);

  const signOut = useCallback(() => {
    writeToken(null);
    setUser(null);
    setStatus('anonymous');
  }, []);

  const value = useMemo<AuthState>(
    () => ({ user, status, signIn, signOut }),
    [user, status, signIn, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>.');
  return ctx;
}
