import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useData } from '../context/DataContext';
import StatusBadge from '../components/StatusBadge';
import { formatDate } from '../utils/format';
import './Dashboard.css';

export default function Dashboard() {
  const { user } = useAuth();
  const { screenings } = useData();

  const total = screenings.length;
  const flagged = screenings.filter((s) => s.verdict === 'flagged').length;
  const review = screenings.filter((s) => s.verdict === 'review').length;
  const verified = screenings.filter((s) => s.verdict === 'verified').length;
  const avgTrust = total ? Math.round(screenings.reduce((sum, s) => sum + s.trustScore, 0) / total) : 0;

  const recent = screenings.slice(0, 6);

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">{user?.department}</p>
          <h1 className="page-title">Good to see you, {user?.name?.split(' ')[0]}.</h1>
          <p className="page-subtitle">Here's how screening at your desk looks over the last 30 days.</p>
        </div>
        <Link to="/app/screen" className="btn btn-primary">Start new screening</Link>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{total}</div>
          <div className="stat-label">Cases screened</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--verified)' }}>{verified}</div>
          <div className="stat-label">Verified</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--pending)' }}>{review}</div>
          <div className="stat-label">Awaiting manual review</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--flagged)' }}>{flagged}</div>
          <div className="stat-label">Flagged for fraud signals</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{avgTrust}</div>
          <div className="stat-label">Average trust score</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 'var(--sp-6)' }}>
        <div className="card-list-header">
          <h2 style={{ fontSize: 'var(--step-1)' }}>Recent cases</h2>
          <Link to="/app/history" className="table-link">View all history &rarr;</Link>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Case</th>
              <th>Applicant</th>
              <th>Document</th>
              <th>Trust score</th>
              <th>Status</th>
              <th>Screened</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((s) => (
              <tr key={s.id}>
                <td><Link to={`/app/report/${s.id}`} className="mono table-link">{s.id}</Link></td>
                <td>{s.applicant.fullName}</td>
                <td>{s.applicant.docType}</td>
                <td className="mono">{s.trustScore}</td>
                <td><StatusBadge status={s.verdict} small /></td>
                <td className="stat-muted">{formatDate(s.createdAt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
