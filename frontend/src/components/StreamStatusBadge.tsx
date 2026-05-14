import {
  STREAM_STATUS_LABEL,
  type StreamStatus,
} from '@/types/production';

interface StreamStatusBadgeProps {
  status: StreamStatus;
  size?: 'sm' | 'md';
  label?: string;
}

const TONE: Record<StreamStatus, { border: string; dot: string; text: string }> = {
  not_planned: {
    border: 'border-rule',
    dot: 'bg-parchment-dim/60',
    text: 'text-parchment-dim',
  },
  pending: {
    border: 'border-parchment-muted/40',
    dot: 'bg-parchment-muted',
    text: 'text-parchment-muted',
  },
  in_progress: {
    border: 'border-accent/60',
    dot: 'bg-accent',
    text: 'text-accent',
  },
  blocked: {
    border: 'border-red-400/30',
    dot: 'bg-red-400/70',
    text: 'text-red-300/80',
  },
  complete: {
    border: 'border-accent',
    dot: 'bg-accent',
    text: 'text-parchment',
  },
};

export function StreamStatusBadge({
  status,
  size = 'md',
  label,
}: StreamStatusBadgeProps) {
  const tone = TONE[status];
  const pad = size === 'sm' ? 'px-2 py-0.5 text-[0.58rem]' : 'px-2.5 py-1 text-[0.65rem]';
  return (
    <span
      className={`inline-flex items-center gap-2 border ${tone.border} ${tone.text} ${pad} font-mono uppercase tracking-widest`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${tone.dot}`} aria-hidden />
      {label ?? STREAM_STATUS_LABEL[status]}
    </span>
  );
}
