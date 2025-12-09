import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AlertsPage from './pages/AlertsPage';
import CreateAlertPage from './pages/CreateAlertPage';
import AlertDetailPage from './pages/AlertDetailPage';
import * as api from './services/api';
import type { User } from './types';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      // Fetch current user info when authenticated
      api.getCurrentUser()
        .then(user => setCurrentUser(user))
        .catch(err => {
          console.error('Failed to fetch user:', err);
          // Token might be invalid, log out
          localStorage.removeItem('token');
          setIsAuthenticated(false);
          setCurrentUser(null);
        });
    } else {
      setCurrentUser(null);
    }
  }, [isAuthenticated]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowDropdown(false);
    if (showDropdown) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showDropdown]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setCurrentUser(null);
    setShowDropdown(false);
    navigate('/login');
  };

  return (
    <>
      {isAuthenticated && (
        <nav className="app-nav">
          <div className="nav-links">
            <Link to="/alerts">My Alerts</Link>
            <Link to="/alerts/new">Create Alert</Link>
          </div>
          {currentUser && (
            <div className="user-menu">
              <button
                className="user-button"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDropdown(!showDropdown);
                }}
                title={currentUser.email}
              >
                {currentUser.email}
              </button>
              {showDropdown && (
                <div className="user-dropdown">
                  <button className="dropdown-item" onClick={handleLogout}>
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </nav>
      )}

      <div className="container">
        <Routes>
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/alerts" /> : <LoginPage onLogin={() => setIsAuthenticated(true)} />
          } />
          <Route path="/register" element={
            isAuthenticated ? <Navigate to="/alerts" /> : <RegisterPage />
          } />
          <Route path="/alerts" element={
            isAuthenticated ? <AlertsPage /> : <Navigate to="/login" />
          } />
          <Route path="/alerts/new" element={
            isAuthenticated ? <CreateAlertPage /> : <Navigate to="/login" />
          } />
          <Route path="/alerts/:id" element={
            isAuthenticated ? <AlertDetailPage /> : <Navigate to="/login" />
          } />
          <Route path="/" element={<Navigate to={isAuthenticated ? "/alerts" : "/login"} />} />
        </Routes>
      </div>
    </>
  );
}

export default App;
