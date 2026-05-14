type Tone = 'ok' | 'pending' | 'error';

interface StatusDotProps {
  tone: Tone;
  label: string;
}

const TONE: Record<Tone, string> = {
  ok: 'bg-accent',
  pending: 'bg-parchment-muted',
  error: 'bg-signal/80',
};

export function StatusDot({ tone, label }: StatusDotProps) {
  return (
    <span className="inline-flex items-center gap-2 font-mono text-[0.7rem] uppercase tracking-widest text-parchment-muted">
      <span className={`h-1.5 w-1.5 rounded-full ${TONE[tone]}`} aria-hidden />
      {label}
    </span>
  );
}
