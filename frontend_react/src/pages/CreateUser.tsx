import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPermissions, createUser } from '../services/api';
import { validatePasswordStrength, validateEmailFormat } from '../utils/validation';
import Button from '../components/Button';
import { Permissions } from '../utils/permissions';

const CreateUser: React.FC = () => {
  const navigate = useNavigate();
  
  // Form state
  const [firstName, setFirstName] = useState<string>('');
  const [lastName, setLastName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([Permissions.READ_AUDIO]);
  const [isPermissionsOpen, setIsPermissionsOpen] = useState<boolean>(false);
  
  // UI state
  const [availablePermissions, setAvailablePermissions] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [fetchingPermissions, setFetchingPermissions] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Fetch permissions on mount
  useEffect(() => {
    const fetchPermissions = async (): Promise<void> => {
      try {
        setFetchingPermissions(true);
        const response = await getPermissions();
        setAvailablePermissions(response.permissions);
      } catch (err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || 'Failed to load permissions');
      } finally {
        setFetchingPermissions(false);
      }
    };

    fetchPermissions();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      const target = event.target as HTMLElement;
      if (
        isPermissionsOpen &&
        !target.closest('.multi-select-container')
      ) {
        setIsPermissionsOpen(false);
      }
    };

    if (isPermissionsOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isPermissionsOpen]);

  // Password validation is now imported from utils/validation.ts

  // Validate form
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!firstName.trim()) {
      errors.firstName = 'First name is required';
    }

    if (!lastName.trim()) {
      errors.lastName = 'Last name is required';
    }

    const emailError = validateEmailFormat(email);
    if (emailError) {
      errors.email = emailError;
    }

    const passwordError = validatePasswordStrength(password);
    if (passwordError) {
      errors.password = passwordError;
    }

    if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    if (selectedPermissions.length === 0) {
      errors.permissions = 'At least one permission is required';
    } else if (!selectedPermissions.includes(Permissions.READ_AUDIO)) {
      errors.permissions = 'read:audio is a required permission';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle permission toggle
  const handlePermissionToggle = (permission: string): void => {
    if (permission === Permissions.READ_AUDIO) {
      return; // Prevent unchecking read:audio
    }
    if (selectedPermissions.includes(permission)) {
      setSelectedPermissions(selectedPermissions.filter((p) => p !== permission));
    } else {
      setSelectedPermissions([...selectedPermissions, permission]);
    }
  };

  // Handle select all permissions
  const handleSelectAll = (): void => {
    if (selectedPermissions.length === availablePermissions.length) {
      setSelectedPermissions([Permissions.READ_AUDIO]);
    } else {
      setSelectedPermissions([...availablePermissions]);
    }
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setValidationErrors({});

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const userData = {
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        password,
        confirm_password: confirmPassword,
        permissions: selectedPermissions.length > 0 ? selectedPermissions : undefined,
      };

      await createUser(userData);
      setSuccess('User created successfully!');
      
      // Clear form
      setFirstName('');
      setLastName('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setSelectedPermissions([]);
      setIsPermissionsOpen(false);
      
      // Redirect after 2 seconds
      setTimeout(() => {
        navigate('/users');
      }, 2000);
    } catch (err) {
      const axiosError = err as { response?: { data?: { detail?: string | string[] } } };
      const errorDetail = axiosError.response?.data?.detail;
      
      if (Array.isArray(errorDetail)) {
        setError(errorDetail.join(', '));
      } else {
        setError(errorDetail || 'Failed to create user. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (fetchingPermissions) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner">Loading permissions...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="create-user-header">
        <h1>Create New User</h1>
      </div>

      <div className="create-user-card">
        <form onSubmit={handleSubmit} className="create-user-form" noValidate>
          {/* First Name */}
          <div className="form-group">
            <label htmlFor="firstName">First Name *</label>
            <input
              type="text"
              id="firstName"
              value={firstName}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setFirstName(e.target.value)}
              required
              placeholder="Enter first name"
              disabled={loading}
            />
            {validationErrors.firstName && (
              <span className="field-error">{validationErrors.firstName}</span>
            )}
          </div>

          {/* Last Name */}
          <div className="form-group">
            <label htmlFor="lastName">Last Name *</label>
            <input
              type="text"
              id="lastName"
              value={lastName}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setLastName(e.target.value)}
              required
              placeholder="Enter last name"
              disabled={loading}
            />
            {validationErrors.lastName && (
              <span className="field-error">{validationErrors.lastName}</span>
            )}
          </div>

          {/* Email */}
          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              required
              placeholder="Enter email address"
              disabled={loading}
            />
            {validationErrors.email && (
              <span className="field-error">{validationErrors.email}</span>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              required
              placeholder="Enter password"
              disabled={loading}
            />
            <small className="form-hint">
              Must contain: 1 uppercase, 1 lowercase, 1 number, 1 special character (@$!%*?&#)
            </small>
            {validationErrors.password && (
              <span className="field-error">{validationErrors.password}</span>
            )}
          </div>

          {/* Confirm Password */}
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password *</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
              required
              placeholder="Confirm password"
              disabled={loading}
            />
            {validationErrors.confirmPassword && (
              <span className="field-error">{validationErrors.confirmPassword}</span>
            )}
          </div>

          {/* Permissions */}
          <div className="form-group">
            <label htmlFor="permissions">Permissions *</label>
            <div className="multi-select-container">
              <button
                type="button"
                className={`multi-select-trigger ${isPermissionsOpen ? 'open' : ''} ${validationErrors.permissions ? 'error' : ''}`}
                onClick={() => setIsPermissionsOpen(!isPermissionsOpen)}
                disabled={loading}
              >
                <span className="multi-select-value">
                  {selectedPermissions.length === 0
                    ? 'Select permissions'
                    : selectedPermissions.join(', ')}
                </span>
                <svg
                  className={`multi-select-arrow ${isPermissionsOpen ? 'open' : ''}`}
                  viewBox="0 0 12 12"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M3 4.5L6 7.5L9 4.5" />
                </svg>
              </button>
              {isPermissionsOpen && (
                <div className="multi-select-dropdown">
                  <div className="multi-select-header">
                    <button
                      type="button"
                      className="multi-select-select-all"
                      onClick={handleSelectAll}
                    >
                      {selectedPermissions.length === availablePermissions.length
                        ? 'Deselect All'
                        : 'Select All'}
                    </button>
                  </div>
                  <div className="multi-select-options">
                    {availablePermissions.map((permission) => (
                      <label
                        key={permission}
                        className={`multi-select-option ${
                          selectedPermissions.includes(permission) ? 'selected' : ''
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={selectedPermissions.includes(permission)}
                          onChange={() => handlePermissionToggle(permission)}
                          disabled={loading || permission === Permissions.READ_AUDIO}
                        />
                        <span>{permission}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
            {validationErrors.permissions && (
              <span className="field-error">{validationErrors.permissions}</span>
            )}
          </div>

          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="form-actions">
            <Button type="submit" variant="primary" isLoading={loading} disabled={loading}>
              {loading ? 'Creating User...' : 'Create User'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/audio')}
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateUser;

