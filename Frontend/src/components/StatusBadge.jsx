import './StatusBadge.css';

const CONFIG = {
  verified: { label: 'Verified', className: 'badge-verified' },
  flagged: { label: 'Flagged', className: 'badge-flagged' },
  review: { label: 'Manual review', className: 'badge-review' },
  pass: { label: 'Pass', className: 'badge-verified' },
  fail: { label: 'Fail', className: 'badge-flagged' },
  warning: { label: 'Warning', className: 'badge-review' },
};

export default function StatusBadge({ status, small }) {
  const cfg = CONFIG[status] || { label: status, className: '' };
  return (
    <span className={`status-badge ${cfg.className} ${small ? 'status-badge-sm' : ''}`}>
      <span className="status-dot" />
      {cfg.label}
    </span>
  );
}
