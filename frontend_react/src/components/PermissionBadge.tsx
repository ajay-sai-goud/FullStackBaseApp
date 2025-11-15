import React from 'react';
import './PermissionBadge.css';

interface PermissionBadgeProps {
  permission: string;
  variant?: 'default' | 'admin';
}

/**
 * Professional permission badge component
 * Displays permissions with appropriate styling
 */
const PermissionBadge: React.FC<PermissionBadgeProps> = ({ permission, variant = 'default' }) => {
  // Determine if this is an admin permission
  const isAdmin = permission.toLowerCase() === 'admin' || variant === 'admin';
  
  // Format permission text for display
  const formatPermission = (perm: string): string => {
    // Convert "read:audio" to "Read Audio" format
    if (perm.includes(':')) {
      const [action, resource] = perm.split(':');
      const actionFormatted = action.charAt(0).toUpperCase() + action.slice(1);
      const resourceFormatted = resource.charAt(0).toUpperCase() + resource.slice(1);
      return `${actionFormatted} ${resourceFormatted}`;
    }
    // Capitalize first letter
    return perm.charAt(0).toUpperCase() + perm.slice(1);
  };

  return (
    <span className={`permission-badge ${isAdmin ? 'permission-badge-admin' : ''}`}>
      {formatPermission(permission)}
    </span>
  );
};

interface PermissionBadgeListProps {
  permissions: string[];
  maxVisible?: number;
}

/**
 * Container component for displaying multiple permission badges
 */
export const PermissionBadgeList: React.FC<PermissionBadgeListProps> = ({ 
  permissions, 
  maxVisible = 10 
}) => {
  const visiblePermissions = permissions.slice(0, maxVisible);
  const remainingCount = permissions.length - maxVisible;

  return (
    <div className="permission-badge-list">
      {visiblePermissions.map((permission) => (
        <PermissionBadge 
          key={permission} 
          permission={permission}
          variant={permission.toLowerCase() === 'admin' ? 'admin' : 'default'}
        />
      ))}
      {remainingCount > 0 && (
        <span className="permission-badge-more">
          +{remainingCount} more
        </span>
      )}
    </div>
  );
};

export default PermissionBadge;

