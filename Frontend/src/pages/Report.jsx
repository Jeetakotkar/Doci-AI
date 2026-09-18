import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useData } from '../context/DataContext';
import StatusBadge from '../components/StatusBadge';
import { formatDate } from '../utils/format';
import './Report.css';

const VERDICT_COPY = {
  verified: 'All checks are consistent with a genuine document. No further action required.',
  flagged: 'One or more checks found signs consistent with a fraudulent or altered document. Do not approve without a manual review.',
  review: 'Most checks passed, but at least one result was inconclusive. Route this case to a senior officer before deciding.',
};

export default function Report() {
  const { id } = useParams();
  const { getById, updateResolution } = useData();
  const navigate = useNavigate();
  const record = getById(id);
  const [resolution, setResolution] = useState(record?.resolution);

  if (!record) {
    return (
      <div className="card">
        <p>No case found with ID <span className="mono">{id}</span>.</p>
        <Link to="/app/history" className="btn btn-outline" style={{ marginTop: 'var(--sp-4)' }}>Back to history</Link>
      </div>
    );
  }

  function resolve(next) {
    setResolution(next);
    updateResolution(record.id, next);
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow mono">{record.id}</p>
          <h1 className="page-title">{record.applicant.fullName}</h1>
          <p className="page-subtitle">
            {record.applicant.docType} &middot; screened {formatDate(record.createdAt)} by {record.officer}
          </p>
        </div>
        <button className="btn btn-outline" onClick={() => window.print()}>Print report</button>
      </div>

      <div className="report-summary card">
        <div>
          <div className="report-score">{record.trustScore}</div>
          <div className="report-score-label">Trust score out of 100</div>
        </div>
        <div className="report-verdict">
          <StatusBadge status={record.verdict} />
          <p>{VERDICT_COPY[record.verdict]}</p>
        </div>
      </div>

      <div className="report-grid">
        <div className="card">
          <h2 className="form-section-title">Check results</h2>
          <div className="check-list">
            {record.checks.map((c) => (
              <div className="check-row" key={c.key}>
                <div className="check-row-top">
                  <span className="check-name">{c.name}</span>
                  <StatusBadge status={c.status} small />
                </div>
                <div className="confidence-bar">
                  <div
                    className={`confidence-fill confidence-${c.status}`}
                    style={{ width: `${c.confidence}%` }}
                  />
                </div>
                <p className="check-finding">{c.finding || c.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="report-side">
          <div className="card">
            <h2 className="form-section-title">Applicant record</h2>
            <dl className="detail-list">
              <div><dt>Full name</dt><dd>{record.applicant.fullName}</dd></div>
              <div><dt>Date of birth</dt><dd>{record.applicant.dob || '\u2014'}</dd></div>
              <div><dt>Document type</dt><dd>{record.applicant.docType}</dd></div>
              <div><dt>Document number</dt><dd className="mono">{record.applicant.idNumber}</dd></div>
              <div><dt>Case ID</dt><dd className="mono">{record.id}</dd></div>
            </dl>
          </div>

          <div className="card">
            <h2 className="form-section-title">Decision</h2>
            <p className="field-hint" style={{ marginBottom: 'var(--sp-4)' }}>
              Current status: <strong>{resolution}</strong>
            </p>
            <div className="decision-actions">
              <button className="btn btn-primary btn-full" onClick={() => resolve('Approved')}>Approve applicant</button>
              <button className="btn btn-outline btn-full" onClick={() => resolve('Escalated')}>Escalate to senior officer</button>
              <button className="btn btn-danger btn-full" onClick={() => resolve('Rejected')}>Reject application</button>
            </div>
          </div>
        </div>
      </div>

      <button className="btn btn-outline" style={{ marginTop: 'var(--sp-5)' }} onClick={() => navigate('/app/history')}>
        &larr; Back to case history
      </button>
    </div>
  );
}
