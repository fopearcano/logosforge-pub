import { useState } from 'react';
import { useAuth } from '@/auth/AuthContext';
import { ApiError } from '@/api/client';
import { ROLE_LABELS } from '@/types/auth';

export function LoginPanel() {
  const { user, status, signIn, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState('helena.pryce@logosforge.local');
  const [password, setPassword] = useState('logosforge');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (status === 'authenticated' && user) {
    return (
      <div className="flex items-center gap-4">
        <div className="text-right leading-tight">
          <div className="font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim">
            {ROLE_LABELS[user.role]}
          </div>
          <div className="text-sm text-parchment">{user.full_name}</div>
        </div>
        <button
          type="button"
          onClick={signOut}
          className="font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment"
        >
          Sign out
        </button>
      </div>
    );
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="border border-rule px-4 py-2 font-mono text-[0.68rem] uppercase tracking-widest text-parchment-muted transition-colors hover:border-parchment-muted hover:text-parchment"
      >
        Sign in
      </button>
    );
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signIn(email, password);
      setOpen(false);
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message || 'Sign-in failed.');
      } else {
        setError('Sign-in failed.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col items-end gap-2 border border-rule bg-ink-700 p-4 text-right shadow-lg"
    >
      <label className="flex flex-col items-start gap-1 text-left">
        <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Email
        </span>
        <input
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-72 border border-rule bg-ink-800 px-3 py-1.5 text-sm text-parchment focus:border-accent focus:outline-none"
          required
        />
      </label>
      <label className="flex flex-col items-start gap-1 text-left">
        <span className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim">
          Password
        </span>
        <input
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-72 border border-rule bg-ink-800 px-3 py-1.5 text-sm text-parchment focus:border-accent focus:outline-none"
          required
        />
      </label>
      {error && (
        <p className="font-mono text-[0.68rem] uppercase tracking-widest text-red-400/80">
          {error}
        </p>
      )}
      <div className="flex items-center gap-3 pt-2">
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="font-mono text-[0.68rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment-muted"
          disabled={submitting}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={submitting}
          className="border border-accent px-4 py-1.5 font-mono text-[0.68rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:opacity-50"
        >
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </div>
    </form>
  );
}
