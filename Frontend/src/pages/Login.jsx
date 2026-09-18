import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      login({ email, password });
      navigate('/app');
    } catch (err) {
      setError(err.message);
    }
  }

  function fillDemo(role) {
    if (role === 'admin') {
      setEmail('admin@fis.gov.in');
      setPassword('demo1234');
    } else {
      setEmail('officer@fis.gov.in');
      setPassword('demo1234');
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <Link to="/" className="auth-back">&larr; Back to overview</Link>
        <h1 className="auth-title">Sign in to your desk</h1>
        <p className="auth-subtitle">Use a seeded demo account below, or sign in with an account you created.</p>

        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="email">Work email</label>
            <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="officer@fis.gov.in" />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          </div>
          {error && <p className="field-error" style={{ marginBottom: 'var(--sp-4)' }}>{error}</p>}
          <button className="btn btn-primary btn-full" type="submit">Sign in</button>
        </form>

        <div className="auth-demo">
          <span>Demo accounts</span>
          <div className="auth-demo-buttons">
            <button type="button" className="btn btn-outline btn-sm" onClick={() => fillDemo('officer')}>Fill officer demo</button>
            <button type="button" className="btn btn-outline btn-sm" onClick={() => fillDemo('admin')}>Fill admin demo</button>
          </div>
          <p className="field-hint">Both use the password <span className="mono">demo1234</span>. Fill and sign in directly.</p>
        </div>

        <p className="auth-switch">
          Don't have an account? <Link to="/signup">Create one</Link>
        </p>
      </div>
    </div>
  );
}
