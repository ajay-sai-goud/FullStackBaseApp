/**
 * Permission constants matching backend permissions.
 * These should match the permissions defined in backend_fastapi/app/core/constants.py
 */

export const Permissions = {
  // Audio permissions
  READ_AUDIO: 'read:audio',
  WRITE_AUDIO: 'write:audio',
  DELETE_AUDIO: 'delete:audio',

  // User permissions
  READ_USER: 'read:user',
  WRITE_USER: 'write:user',
  DELETE_USER: 'delete:user',

  // Admin permission
  ADMIN: 'admin',
} as const;

export type Permission = typeof Permissions[keyof typeof Permissions];

/**
 * All available permissions list
 */
export const ALL_PERMISSIONS: Permission[] = [
  Permissions.READ_AUDIO,
  Permissions.WRITE_AUDIO,
  Permissions.DELETE_AUDIO,
  Permissions.READ_USER,
  Permissions.WRITE_USER,
  Permissions.DELETE_USER,
  Permissions.ADMIN,
];

