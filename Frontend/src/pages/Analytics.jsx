import { useMemo } from 'react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, PieChart, Pie, Cell,
} from 'recharts';
import { useData } from '../context/DataContext';
import { formatDateShort } from '../utils/format';
import './Analytics.css';

const COLORS = {
  ink: '#12171b',
  verified: '#1b7a5a',
  flagged: '#ab3a20',
  pending: '#b07f1f',
  focus: '#2f5fd6',
  line: '#d7dad5',
  slate: '#5c6670',
};

const CHECK_LABELS = {
  ocr: 'Document extraction',
  face: 'Face match',
  tamper: 'Tamper detection',
  database: 'Authority cross-check',
  watchlist: 'Watchlist screening',
};

export default function Analytics() {
  const { screenings } = useData();

  const volumeByDay = useMemo(() => {
    const days = {};
    screenings.forEach((s) => {
      const key = formatDateShort(s.createdAt);
      days[key] = (days[key] || 0) + 1;
    });
    return Object.entries(days)
      .map(([date, count]) => ({ date, count }))
      .slice(-14);
  }, [screenings]);

  const verdictBreakdown = useMemo(() => {
    const counts = { verified: 0, review: 0, flagged: 0 };
    screenings.forEach((s) => { counts[s.verdict] = (counts[s.verdict] || 0) + 1; });
    return [
      { name: 'Verified', value: counts.verified, color: COLORS.verified },
      { name: 'Manual review', value: counts.review, color: COLORS.pending },
      { name: 'Flagged', value: counts.flagged, color: COLORS.flagged },
    ];
  }, [screenings]);

  const failuresByCheck = useMemo(() => {
    const counts = {};
    screenings.forEach((s) => {
      s.checks.forEach((c) => {
        if (c.status !== 'pass') {
          counts[c.key] = (counts[c.key] || 0) + 1;
        }
      });
    });
    return Object.entries(counts).map(([key, count]) => ({ name: CHECK_LABELS[key] || key, count }));
  }, [screenings]);

  const docTypeBreakdown = useMemo(() => {
    const counts = {};
    screenings.forEach((s) => {
      const type = s.applicant.docType;
      counts[type] = (counts[type] || 0) + 1;
    });
    return Object.entries(counts).map(([name, count]) => ({ name, count }));
  }, [screenings]);

  const total = screenings.length;
  const flagRate = total ? Math.round((verdictBreakdown[2].value / total) * 100) : 0;

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">Administrator view</p>
          <h1 className="page-title">Screening analytics</h1>
          <p className="page-subtitle">Aggregate patterns across every case run in this browser's demo data.</p>
        </div>
      </div>

      <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="stat-card">
          <div className="stat-value">{total}</div>
          <div className="stat-label">Total cases</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--flagged)' }}>{flagRate}%</div>
          <div className="stat-label">Flag rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{failuresByCheck.reduce((s, c) => s + c.count, 0)}</div>
          <div className="stat-label">Total check failures / warnings</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{docTypeBreakdown.length}</div>
          <div className="stat-label">Document types seen</div>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="card">
          <h2 className="form-section-title">Screening volume</h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={volumeByDay} margin={{ left: -20 }}>
              <CartesianGrid stroke={COLORS.line} vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: COLORS.slate }} axisLine={{ stroke: COLORS.line }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: COLORS.slate }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4, border: `1px solid ${COLORS.line}` }} />
              <Line type="monotone" dataKey="count" stroke={COLORS.focus} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="form-section-title">Verdict breakdown</h2>
          <div className="donut-wrap">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={verdictBreakdown} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
                  {verdictBreakdown.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4, border: `1px solid ${COLORS.line}` }} />
              </PieChart>
            </ResponsiveContainer>
            <ul className="donut-legend">
              {verdictBreakdown.map((v) => (
                <li key={v.name}>
                  <span className="legend-dot" style={{ background: v.color }} />
                  {v.name}
                  <span className="legend-value mono">{v.value}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="card">
          <h2 className="form-section-title">Where checks fail most</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={failuresByCheck} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={COLORS.line} horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: COLORS.slate }} axisLine={false} tickLine={false} allowDecimals={false} />
              <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 11, fill: COLORS.ink }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4, border: `1px solid ${COLORS.line}` }} />
              <Bar dataKey="count" fill={COLORS.flagged} radius={[0, 3, 3, 0]} barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="form-section-title">Cases by document type</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={docTypeBreakdown} margin={{ left: -20 }}>
              <CartesianGrid stroke={COLORS.line} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: COLORS.slate }} axisLine={{ stroke: COLORS.line }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: COLORS.slate }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 4, border: `1px solid ${COLORS.line}` }} />
              <Bar dataKey="count" fill={COLORS.ink} radius={[3, 3, 0, 0]} barSize={28} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
