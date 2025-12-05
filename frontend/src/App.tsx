import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AlertsPage from './pages/AlertsPage';
import CreateAlertPage from './pages/CreateAlertPage';
import AlertDetailPage from './pages/AlertDetailPage';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/login');
  };

  return (
    <>
      {isAuthenticated && (
        <nav>
          <Link to="/alerts">My Alerts</Link>
          <Link to="/alerts/new">Create Alert</Link>
          <button onClick={handleLogout} style={{ float: 'right' }}>Logout</button>
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
