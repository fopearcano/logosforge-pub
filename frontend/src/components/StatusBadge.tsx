import { STATUS_LABELS, type WorkflowStatus } from '@/types/workflow';

type Tone = 'cold' | 'warm' | 'live' | 'rest' | 'closed';

const STATUS_TONE: Record<WorkflowStatus, Tone> = {
  submitted: 'cold',
  under_review: 'cold',
  accepted: 'warm',
  rejected: 'closed',
  development_editing: 'warm',
  copy_editing: 'warm',
  proofreading: 'warm',
  layout: 'live',
  cover_design: 'live',
  prepress: 'live',
  published: 'live',
  archived: 'rest',
};

const TONE_CLASSES: Record<Tone, { border: string; dot: string; text: string }> = {
  cold: {
    border: 'border-parchment-muted/40',
    dot: 'bg-parchment-muted',
    text: 'text-parchment-muted',
  },
  warm: {
    border: 'border-accent/50',
    dot: 'bg-accent/80',
    text: 'text-accent',
  },
  live: {
    border: 'border-accent',
    dot: 'bg-accent',
    text: 'text-parchment',
  },
  rest: {
    border: 'border-rule',
    dot: 'bg-parchment-dim',
    text: 'text-parchment-dim',
  },
  closed: {
    border: 'border-red-400/30',
    dot: 'bg-red-400/70',
    text: 'text-red-300/80',
  },
};

interface StatusBadgeProps {
  status: WorkflowStatus;
  size?: 'sm' | 'md';
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const tone = TONE_CLASSES[STATUS_TONE[status]];
  const pad = size === 'sm' ? 'px-2 py-0.5 text-[0.6rem]' : 'px-3 py-1 text-[0.68rem]';
  return (
    <span
      className={`inline-flex items-center gap-2 border ${tone.border} ${tone.text} ${pad} font-mono uppercase tracking-widest`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${tone.dot}`} aria-hidden />
      {STATUS_LABELS[status]}
    </span>
  );
}
