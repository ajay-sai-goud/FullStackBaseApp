import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';
import { Permissions } from './utils/permissions';
import Login from './pages/Login';
import AudioList from './pages/AudioList';
import Upload from './pages/Upload';
import UserList from './pages/UserList';
import CreateUser from './pages/CreateUser';
import EditUser from './pages/EditUser';
import './App.css';

// Layout component for authenticated pages with sidebar
const AuthenticatedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-main-content">
        {children}
      </main>
    </div>
  );
};

const App: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/audio"
            element={
              <ProtectedRoute requiredPermission={Permissions.READ_AUDIO}>
                <AuthenticatedLayout>
                  <AudioList />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute requiredPermission={Permissions.WRITE_AUDIO}>
                <AuthenticatedLayout>
                  <Upload />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute requiredPermission={Permissions.READ_USER}>
                <AuthenticatedLayout>
                  <UserList />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/users/create"
            element={
              <ProtectedRoute requiredPermission={Permissions.WRITE_USER}>
                <AuthenticatedLayout>
                  <CreateUser />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/users/:id/edit"
            element={
              <ProtectedRoute requiredPermission={Permissions.WRITE_USER}>
                <AuthenticatedLayout>
                  <EditUser />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              isAuthenticated() ? (
                <Navigate to="/audio" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;

