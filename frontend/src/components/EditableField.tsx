import {
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactNode,
} from 'react';

type FieldType = 'text' | 'multiline' | 'number';

interface EditableFieldProps {
  value: string;
  onSave: (next: string) => Promise<void>;
  canEdit: boolean;
  type?: FieldType;
  placeholder?: string;
  emptyLabel?: string;
  displayClassName?: string;
  inputClassName?: string;
}

export function EditableField({
  value,
  onSave,
  canEdit,
  type = 'text',
  placeholder,
  emptyLabel = '—',
  displayClassName,
  inputClassName,
}: EditableFieldProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (editing) {
      setDraft(value);
      (type === 'multiline' ? textareaRef : inputRef).current?.focus();
    }
  }, [editing, type, value]);

  const handleSave = async () => {
    if (draft === value) {
      setEditing(false);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await onSave(draft);
      setEditing(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setDraft(value);
    setError(null);
    setEditing(false);
  };

  const onKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      handleCancel();
    } else if (event.key === 'Enter' && type !== 'multiline') {
      event.preventDefault();
      void handleSave();
    }
  };

  if (!editing) {
    const display: ReactNode = value ? (
      value
    ) : (
      <span className="text-parchment-dim">{emptyLabel}</span>
    );
    const interactive = canEdit
      ? 'cursor-text border-b border-dotted border-transparent transition-colors hover:border-rule focus:border-rule'
      : '';

    return (
      <button
        type="button"
        onClick={() => canEdit && setEditing(true)}
        disabled={!canEdit}
        className={`block w-full text-left ${interactive} ${displayClassName ?? ''}`}
        title={canEdit ? 'Click to edit' : undefined}
      >
        {display}
      </button>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {type === 'multiline' ? (
        <textarea
          ref={textareaRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          rows={6}
          className={`resize-none border border-rule bg-ink-700 px-3 py-2 leading-relaxed focus:border-accent focus:outline-none ${inputClassName ?? ''}`}
        />
      ) : (
        <input
          ref={inputRef}
          type={type === 'number' ? 'number' : 'text'}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          className={`border border-rule bg-ink-700 px-3 py-1.5 focus:border-accent focus:outline-none ${inputClassName ?? ''}`}
        />
      )}

      <div className="flex items-center justify-between gap-3">
        <span
          className={`font-mono text-[0.62rem] uppercase tracking-widest ${
            error ? 'text-red-300' : 'text-parchment-dim'
          }`}
        >
          {error ?? (type === 'multiline' ? 'Esc to cancel' : 'Enter to save · Esc to cancel')}
        </span>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleCancel}
            disabled={saving}
            className="font-mono text-[0.62rem] uppercase tracking-widest text-parchment-dim transition-colors hover:text-parchment-muted disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => void handleSave()}
            disabled={saving}
            className="border border-accent px-3 py-1 font-mono text-[0.62rem] uppercase tracking-widest text-accent transition-colors hover:bg-accent hover:text-ink-900 disabled:opacity-40"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
