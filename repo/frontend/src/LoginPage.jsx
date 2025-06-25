import React, { useState } from 'react';
import { useAppContext } from './contexts/AppContext';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const LoginPage = () => {
  const { login } = useAppContext();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      const response = await axios.post(`${API_URL}/token`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const { access_token, role } = response.data;
      login(access_token, role);
    } catch (err) {
      setError('Invalid username or password');
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="login-placeholder">
      <h1>Database Admin Panel</h1>
      <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: 320 }}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            autoFocus
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <div className="error-message" style={{ marginBottom: 12 }}>{error}</div>}
        <button type="submit" style={{ width: '100%' }}>Log In</button>
      </form>
      <p style={{ marginTop: 24, opacity: 0.7, fontSize: 14 }}>
        Demo: <b>admin_dev/admin123</b> or <b>user_dev/user123</b>
      </p>
    </div>
  );
};

export default LoginPage; 