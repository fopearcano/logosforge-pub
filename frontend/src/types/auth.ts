export type UserRole =
  | 'admin'
  | 'editor'
  | 'reviewer'
  | 'production_manager'
  | 'marketing'
  | 'archive_reader';

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_at: string;
  user: CurrentUser;
}

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Admin',
  editor: 'Editor',
  reviewer: 'Reviewer',
  production_manager: 'Production Manager',
  marketing: 'Marketing',
  archive_reader: 'Archive Reader',
};
