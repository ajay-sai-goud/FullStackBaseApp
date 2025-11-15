import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Permissions } from '../utils/permissions';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, hasAnyPermission } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);

  const handleLogout = (): void => {
    logout();
    navigate('/login');
  };

  const toggleMobileMenu = (): void => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const isActive = (path: string): boolean => {
    return location.pathname === path;
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="sidebar-mobile-toggle"
        onClick={toggleMobileMenu}
        aria-label="Toggle menu"
      >
        <span className="hamburger-icon">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${isMobileMenuOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18V5l12-2v13"></path>
              <circle cx="6" cy="18" r="3"></circle>
              <circle cx="18" cy="16" r="3"></circle>
            </svg>
            <h2>Audio Manager</h2>
          </div>
        </div>

        <nav className="sidebar-nav">
          {hasAnyPermission(Permissions.READ_AUDIO, Permissions.ADMIN) && (
            <Link
              to="/audio"
              className={`sidebar-link ${isActive('/audio') ? 'active' : ''}`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 18V5l12-2v13"></path>
                <circle cx="6" cy="18" r="3"></circle>
                <circle cx="18" cy="16" r="3"></circle>
              </svg>
              <span>Audio List</span>
            </Link>
          )}

          {hasAnyPermission(Permissions.WRITE_AUDIO, Permissions.ADMIN) && (
            <Link
              to="/upload"
              className={`sidebar-link ${isActive('/upload') ? 'active' : ''}`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <span>Upload Audio</span>
            </Link>
          )}

          {hasAnyPermission(Permissions.READ_USER, Permissions.ADMIN) && (
            <Link
              to="/users"
              className={`sidebar-link ${isActive('/users') || isActive('/users/create') || location.pathname.startsWith('/users/') ? 'active' : ''}`}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              <span>User Management</span>
            </Link>
          )}
        </nav>

        <div className="sidebar-footer">
          <button
            onClick={handleLogout}
            className="sidebar-logout-btn"
          >
            <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isMobileMenuOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </>
  );
};

export default Sidebar;

