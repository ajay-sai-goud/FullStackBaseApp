import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import {
  LoginResponse,
  AudioFilesResponse,
  PlaybackUrlResponse,
  UploadResponse,
  PermissionsResponse,
  CreateUserRequest,
  CreateUserResponse,
  User,
  UpdateUserRequest,
  UpdateAudioFileRequest,
  AudioFile,
} from '../types';

// Get backend URL from environment variable (defaults to localhost:8000)
// Note: Environment variables must be prefixed with REACT_APP_ in Create React App
const REACT_APP_API_BASE_URL: string = 
  (process.env.REACT_APP_API_BASE_URL as string) || 'http://localhost:8000';

// Create axios instance with base URL
const api: AxiosInstance = axios.create({
  baseURL: REACT_APP_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      // Only redirect if we're not already on the login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API Functions

/**
 * Login user and get JWT token
 * @param email - User email
 * @param password - User password
 * @returns Promise with access token and token type
 */
export const login = async (email: string, password: string): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/api/login', {
    email,
    password,
  });
  return response.data;
};

/**
 * Get list of audio files for authenticated user
 * @param skip - Number of records to skip (pagination)
 * @param limit - Maximum number of records to return
 * @returns Promise with audio files list
 */
export const getAudioFiles = async (skip: number = 0, limit: number = 100): Promise<AudioFilesResponse> => {
  const response = await api.get<AudioFilesResponse>('/api/audio', {
    params: {
      skip,
      limit,
    },
  });
  return response.data;
};

/**
 * Get signed URL for audio file playback
 * @param fileId - File ID
 * @returns Promise with signed URL and expiration time
 */
export const getPlaybackUrl = async (fileId: string): Promise<PlaybackUrlResponse> => {
  const response = await api.get<PlaybackUrlResponse>(`/api/audio/${fileId}/play`);
  return response.data;
};

/**
 * Upload audio file
 * @param file - Audio file to upload
 * @returns Promise with uploaded file details
 */
export const uploadAudioFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/api/audio/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Get list of all available permissions
 * @returns Promise with list of permissions
 */
export const getPermissions = async (): Promise<PermissionsResponse> => {
  const response = await api.get<PermissionsResponse>('/api/users/permissions');
  return response.data;
};

/**
 * Create a new user
 * @param userData - User creation data including password and confirm_password
 * @returns Promise with created user details
 */
export const createUser = async (userData: CreateUserRequest): Promise<CreateUserResponse> => {
  const response = await api.post<CreateUserResponse>('/api/users', userData);
  return response.data;
};

/**
 * Get list of all users
 * @param skip - Number of records to skip (pagination)
 * @param limit - Maximum number of records to return
 * @returns Promise with list of users
 */
export const listUsers = async (skip: number = 0, limit: number = 100): Promise<User[]> => {
  const response = await api.get<User[]>('/api/users', {
    params: {
      skip,
      limit,
    },
  });
  return response.data;
};

/**
 * Get a user by ID
 * @param userId - User ID
 * @returns Promise with user details
 */
export const getUser = async (userId: string): Promise<User> => {
  const response = await api.get<User>(`/api/users/${userId}`);
  return response.data;
};

/**
 * Update a user
 * @param userId - User ID
 * @param userData - User update data
 * @returns Promise with updated user details
 */
export const updateUser = async (userId: string, userData: UpdateUserRequest): Promise<User> => {
  const response = await api.put<User>(`/api/users/${userId}`, userData);
  return response.data;
};

/**
 * Delete a user
 * @param userId - User ID
 * @returns Promise that resolves when user is deleted
 */
export const deleteUser = async (userId: string): Promise<void> => {
  await api.delete(`/api/users/${userId}`);
};

/**
 * Update an audio file
 * @param fileId - File ID
 * @param updateData - Audio file update data
 * @returns Promise with updated audio file details
 */
export const updateAudioFile = async (fileId: string, updateData: UpdateAudioFileRequest): Promise<AudioFile> => {
  const response = await api.put<AudioFile>(`/api/audio/${fileId}`, updateData);
  return response.data;
};

/**
 * Delete an audio file
 * @param fileId - File ID
 * @returns Promise that resolves when audio file is deleted
 */
export const deleteAudioFile = async (fileId: string): Promise<void> => {
  await api.delete(`/api/audio/${fileId}`);
};

export default api;

