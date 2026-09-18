import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', department: '' });
  const [error, setError] = useState('');

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    try {
      signup(form);
      navigate('/app');
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <Link to="/" className="auth-back">&larr; Back to overview</Link>
        <h1 className="auth-title">Create your screening account</h1>
        <p className="auth-subtitle">Include the word "admin" in your email to unlock the analytics panel in this demo.</p>

        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="name">Full name</label>
            <input id="name" required value={form.name} onChange={update('name')} placeholder="Ravi Sharma" />
          </div>
          <div className="field">
            <label htmlFor="email">Work email</label>
            <input id="email" type="email" required value={form.email} onChange={update('email')} placeholder="you@fis.gov.in" />
          </div>
          <div className="field">
            <label htmlFor="department">Department / desk</label>
            <input id="department" value={form.department} onChange={update('department')} placeholder="District Screening Desk" />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" required value={form.password} onChange={update('password')} placeholder="Create a password" />
          </div>
          {error && <p className="field-error" style={{ marginBottom: 'var(--sp-4)' }}>{error}</p>}
          <button className="btn btn-primary btn-full" type="submit">Create account</button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
