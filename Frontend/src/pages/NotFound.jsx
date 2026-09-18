import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 'var(--sp-4)' }}>
      <p className="mono" style={{ color: 'var(--slate)' }}>404</p>
      <h1 className="page-title">This page doesn't exist.</h1>
      <Link to="/" className="btn btn-primary">Back to overview</Link>
    </div>
  );
}
