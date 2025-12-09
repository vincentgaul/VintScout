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
        <nav className="bg-white shadow px-5 py-3 mb-6 flex flex-wrap items-center justify-between gap-3 rounded">
          <div className="flex gap-4 flex-wrap text-blue-600 font-medium">
            <Link to="/alerts">My Alerts</Link>
            <Link to="/alerts/new">Create Alert</Link>
          </div>
          {currentUser && (
            <div className="relative">
              <button
                className="text-blue-600 font-medium max-w-[200px] truncate"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDropdown(!showDropdown);
                }}
                title={currentUser.email}
              >
                {currentUser.email}
              </button>
              {showDropdown && (
                <div className="absolute right-0 mt-1 bg-white border rounded shadow z-10 min-w-[150px]">
                  <button
                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                    onClick={handleLogout}
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </nav>
      )}

      <div className="max-w-5xl mx-auto px-4 pb-10">
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
