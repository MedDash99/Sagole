import React, { useState } from 'react';
import { useAppContext } from './contexts/AppContext';

const LoginPage = () => {
  const { login } = useAppContext();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Mock authentication logic
    if (username === 'admin' && password === 'admin') {
      login('demo-token', 'admin');
    } else if (username === 'user' && password === 'user') {
      login('demo-token', 'user');
    } else {
      setError('Invalid credentials');
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
        Demo: <b>admin/admin</b> or <b>user/user</b>
      </p>
    </div>
  );
};

export default LoginPage; 