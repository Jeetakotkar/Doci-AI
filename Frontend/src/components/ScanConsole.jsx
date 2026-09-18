import './ScanConsole.css';

const ROWS = [
  { label: 'Document data extraction', delay: '0.2s' },
  { label: 'Face match', delay: '1.1s' },
  { label: 'Tamper detection', delay: '2.0s' },
  { label: 'Authority cross-check', delay: '2.9s' },
  { label: 'Watchlist screening', delay: '3.8s' },
];

export default function ScanConsole() {
  return (
    <div className="scan-console" role="img" aria-label="Animated preview of the identity screening checks running">
      <div className="scan-console-header">
        <span className="mono">CASE FIS-2026-004821</span>
        <span className="scan-live">
          <span className="scan-live-dot" /> running
        </span>
      </div>

      <div className="scan-doc">
        <div className="scan-doc-photo" />
        <div className="scan-doc-lines">
          <div className="scan-doc-line" style={{ width: '70%' }} />
          <div className="scan-doc-line" style={{ width: '45%' }} />
          <div className="scan-doc-line" style={{ width: '85%' }} />
          <div className="scan-doc-line" style={{ width: '55%' }} />
        </div>
        <div className="scan-sweep" />
      </div>

      <ul className="scan-checklist">
        {ROWS.map((row) => (
          <li key={row.label} style={{ animationDelay: row.delay }}>
            <span className="scan-check-icon">
              <svg width="11" height="9" viewBox="0 0 11 9" fill="none">
                <path d="M1 4.5L4 7.5L10 1" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            {row.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
