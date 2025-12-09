import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import * as api from '../services/api';

export default function RegisterPage() {
  const inputClass = 'w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await api.register(email, password);
      // Auto-login after registration
      const response = await api.login(email, password);
      localStorage.setItem('token', response.access_token);
      navigate('/alerts');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-md mx-auto mt-12">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={inputClass}
          />
        </div>
        <div className="space-y-2">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className={inputClass}
          />
        </div>
        <div className="space-y-2">
          <label>Confirm Password</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className={inputClass}
          />
        </div>
        {error && <div className="text-red-600 text-sm mt-2">{error}</div>}
        <button type="submit" disabled={loading} className="mt-2 w-full bg-blue-600 text-white py-2 rounded disabled:bg-gray-400">
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
      <p className="text-sm mt-5 text-center">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
}
