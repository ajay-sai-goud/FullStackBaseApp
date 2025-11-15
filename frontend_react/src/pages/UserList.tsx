import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { listUsers, deleteUser } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Permissions } from '../utils/permissions';
import ConfirmDialog from '../components/ConfirmDialog';
import ActionButton from '../components/ActionButton';
import { PermissionBadgeList } from '../components/PermissionBadge';
import Button from '../components/Button';
import { User } from '../types';

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<{ isOpen: boolean; userId: string | null; email: string }>({
    isOpen: false,
    userId: null,
    email: '',
  });
  const navigate = useNavigate();
  const { hasAnyPermission } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async (): Promise<void> => {
    try {
      setLoading(true);
      setError('');
      const data = await listUsers(0, 100);
      setUsers(data);
    } catch (err) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (userId: string, email: string): void => {
    setConfirmDelete({
      isOpen: true,
      userId,
      email,
    });
  };

  const handleConfirmDelete = async (): Promise<void> => {
    if (!confirmDelete.userId) return;

    try {
      setDeletingId(confirmDelete.userId);
      setError('');
      await deleteUser(confirmDelete.userId);
      setUsers(users.filter((user) => user.id !== confirmDelete.userId));
      setConfirmDelete({ isOpen: false, userId: null, email: '' });
    } catch (err) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeletingId(null);
    }
  };

  const handleCancelDelete = (): void => {
    setConfirmDelete({ isOpen: false, userId: null, email: '' });
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="loading-spinner">Loading users...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="user-list-header">
        <h1>User Management</h1>
        {hasAnyPermission(Permissions.WRITE_USER, Permissions.ADMIN) && (
          <div className="header-actions">
            <Button onClick={() => navigate('/users/create')} variant="primary">
              Create User
            </Button>
          </div>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {users.length === 0 ? (
        <div className="empty-state">
          <p>No users found. Create your first user!</p>
          {hasAnyPermission(Permissions.WRITE_USER, Permissions.ADMIN) && (
            <Button onClick={() => navigate('/users/create')} variant="primary">
              Create User
            </Button>
          )}
        </div>
      ) : (
        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Permissions</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>
                    <strong>{user.first_name} {user.last_name}</strong>
                  </td>
                  <td>{user.email}</td>
                  <td>
                    <PermissionBadgeList permissions={user.permissions} />
                  </td>
                  <td>{formatDate(user.created_at)}</td>
                  <td>
                    <div className="table-actions">
                      {hasAnyPermission(Permissions.WRITE_USER, Permissions.ADMIN) && (
                        <ActionButton
                          variant="edit"
                          onClick={() => navigate(`/users/${user.id}/edit`)}
                          title="Edit user"
                        />
                      )}
                      {hasAnyPermission(Permissions.DELETE_USER, Permissions.ADMIN) && (
                        <ActionButton
                          variant="delete"
                          onClick={() => handleDelete(user.id, user.email)}
                          disabled={deletingId === user.id}
                          title="Delete user"
                        />
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        isOpen={confirmDelete.isOpen}
        title="Delete User"
        message={`Are you sure you want to delete user "${confirmDelete.email}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        variant="danger"
      />
    </div>
  );
};

export default UserList;

