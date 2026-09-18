import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useData } from '../context/DataContext';
import StatusBadge from '../components/StatusBadge';
import { formatDate } from '../utils/format';
import './Dashboard.css';
import './History.css';

const FILTERS = [
  { key: 'all', label: 'All cases' },
  { key: 'verified', label: 'Verified' },
  { key: 'review', label: 'Manual review' },
  { key: 'flagged', label: 'Flagged' },
];

export default function History() {
  const { screenings } = useData();
  const [filter, setFilter] = useState('all');
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    return screenings.filter((s) => {
      const matchesFilter = filter === 'all' || s.verdict === filter;
      const q = query.trim().toLowerCase();
      const matchesQuery =
        !q ||
        s.applicant.fullName.toLowerCase().includes(q) ||
        s.id.toLowerCase().includes(q) ||
        s.applicant.idNumber.toLowerCase().includes(q);
      return matchesFilter && matchesQuery;
    });
  }, [screenings, filter, query]);

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Case history</p>
          <h1 className="page-title">All screenings</h1>
          <p className="page-subtitle">Search and filter every case run at your desk.</p>
        </div>
      </div>

      <div className="history-controls">
        <input
          className="history-search"
          placeholder="Search by name, case ID or document number"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="history-filters">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              className={'history-filter' + (filter === f.key ? ' active' : '')}
              onClick={() => setFilter(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Case</th>
              <th>Applicant</th>
              <th>Document</th>
              <th>Trust score</th>
              <th>Status</th>
              <th>Resolution</th>
              <th>Screened</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => (
              <tr key={s.id}>
                <td><Link to={`/app/report/${s.id}`} className="mono table-link">{s.id}</Link></td>
                <td>{s.applicant.fullName}</td>
                <td>{s.applicant.docType}</td>
                <td className="mono">{s.trustScore}</td>
                <td><StatusBadge status={s.verdict} small /></td>
                <td className="stat-muted">{s.resolution}</td>
                <td className="stat-muted">{formatDate(s.createdAt)}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="stat-muted" style={{ padding: 'var(--sp-5)' }}>No cases match your search.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
