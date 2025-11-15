// API Response Types
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface AudioFile {
  id: string;
  user_id: string;
  file_name: string;
  file_url: string;
  file_type: string;
  file_metadata?: {
    duration?: number;
    size?: number;
    [key: string]: unknown;
  };
  created_at: string;
  updated_at: string;
}

export interface AudioFilesResponse {
  files: AudioFile[];
  total?: number;
}

export interface PlaybackUrlResponse {
  signed_url: string;
  expires_in: number;
}

export interface UploadResponse {
  id: string;
  file_name: string;
  file_url: string;
  file_type: string;
  file_metadata?: {
    duration?: number;
    size?: number;
    [key: string]: unknown;
  };
  created_at: string;
  updated_at: string;
}

export interface PermissionsResponse {
  permissions: string[];
}

export interface CreateUserRequest {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
  permissions?: string[];
}

export interface CreateUserResponse {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  permissions: string[];
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  permissions: string[];
  created_at: string;
  updated_at: string;
}

export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  password?: string;
  permissions?: string[];
}

export interface UpdateAudioFileRequest {
  file_name?: string;
}

// Auth Context Types
export interface AuthContextType {
  token: string | null;
  permissions: string[];
  login: (token: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
  isLoading: boolean;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (...permissions: string[]) => boolean;
  hasAllPermissions: (...permissions: string[]) => boolean;
}

// Component Props Types
export interface AudioPlayerProps {
  fileId: string;
  fileName: string;
}

export interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
}

export interface AuthProviderProps {
  children: React.ReactNode;
}

