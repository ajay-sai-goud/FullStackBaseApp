/**
 * Validation utilities for form inputs.
 * Centralized validation logic to avoid duplication.
 */

/**
 * Validate password strength according to backend requirements.
 * 
 * Requirements:
 * - Minimum 6 characters
 * - At least one uppercase letter (A-Z)
 * - At least one lowercase letter (a-z)
 * - At least one digit (0-9)
 * - At least one special character (@$!%*?&#)
 * 
 * @param password - Password string to validate
 * @returns Empty string if valid, error message if invalid
 */
export const validatePasswordStrength = (password: string): string => {
  if (password.length < 6) {
    return 'Password must be at least 6 characters long';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one number';
  }
  if (!/[@$!%*?&#]/.test(password)) {
    return 'Password must contain at least one special character (@$!%*?&#)';
  }
  return '';
};

/**
 * Validate email format.
 * 
 * @param email - Email string to validate
 * @returns Empty string if valid, error message if invalid
 */
export const validateEmailFormat = (email: string): string => {
  if (!email.trim()) {
    return 'Email is required';
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return 'Invalid email format';
  }
  return '';
};

