export type AttachmentKind =
  | 'manuscript_draft'
  | 'editor_marked_copy'
  | 'cover_artwork'
  | 'proof'
  | 'contract_scan'
  | 'other';

export const ATTACHMENT_KINDS: AttachmentKind[] = [
  'manuscript_draft',
  'editor_marked_copy',
  'cover_artwork',
  'proof',
  'contract_scan',
  'other',
];

export const ATTACHMENT_KIND_LABEL: Record<AttachmentKind, string> = {
  manuscript_draft: 'Manuscript draft',
  editor_marked_copy: "Editor's marked copy",
  cover_artwork: 'Cover artwork',
  proof: 'Proof',
  contract_scan: 'Contract scan',
  other: 'Other',
};

export interface Attachment {
  id: string;
  created_at: string;
  updated_at: string;
  manuscript_id: string;
  uploader_id: string | null;
  uploader_name: string | null;
  filename: string;
  content_type: string;
  size_bytes: number;
  kind: AttachmentKind;
  storage_key: string;
  sha256: string | null;
  description: string | null;
  is_placeholder: boolean;
}

export type ExportFormat = 'markdown' | 'json' | 'pdf';

export interface ExportFormatDescriptor {
  format: ExportFormat;
  media_type: string;
  extension: string;
}
