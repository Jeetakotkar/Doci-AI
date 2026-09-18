import { Link } from 'react-router-dom';
import ScanConsole from '../components/ScanConsole';
import './Landing.css';

const STEPS = [
  {
    title: 'Capture',
    body: 'The officer scans the applicant\u2019s ID document and captures a live photo through the camera, right at the point of intake.',
  },
  {
    title: 'Screen',
    body: 'Five automated checks run in parallel: OCR extraction, face match, tamper detection, an authority cross-check, and a watchlist screen.',
  },
  {
    title: 'Decide',
    body: 'A trust score and a plain-language report land in seconds, so the officer can approve, escalate, or reject with evidence in hand.',
  },
];

const CHECKS = [
  { name: 'Document data extraction', body: 'Reads name, ID number, DOB and issue date, and confirms they sit where the document type expects.' },
  { name: 'Face match', body: 'Compares the live camera capture to the document photo and scores how closely the facial landmarks line up.' },
  { name: 'Tamper detection', body: 'Looks for font swaps, spacing shifts and watermark misalignment that signal digital editing.' },
  { name: 'Authority cross-check', body: 'Validates the document number\u2019s format and checksum against the issuing authority\u2019s series.' },
  { name: 'Watchlist screening', body: 'Flags any partial match against known fraud watchlists for manual follow-up.' },
];

export default function Landing() {
  return (
    <div className="landing">
      <header className="landing-nav">
        <div className="container landing-nav-inner">
          <div className="landing-brand mono">FIS / Fake Identity Screening</div>
          <div className="landing-nav-links">
            <Link to="/login" className="btn btn-outline btn-sm">Sign in</Link>
            <Link to="/signup" className="btn btn-primary btn-sm">Get started</Link>
          </div>
        </div>
      </header>

      <section className="landing-hero">
        <div className="container hero-grid">
          <div>
            <p className="page-eyebrow">Smart India Hackathon 2026</p>
            <h1 className="hero-title">
              Catch a forged ID before it becomes someone else's problem.
            </h1>
            <p className="hero-lead">
              A screening desk for front-line officers: upload a document and capture a live
              photo,
              and get a trust score backed by five automated checks in under a minute
              &mdash; no manual squinting at fonts and holograms.
            </p>
            <div className="hero-actions">
              <Link to="/signup" className="btn btn-primary">Try the prototype</Link>
              <Link to="/login" className="btn btn-outline">I already have an account</Link>
            </div>
          </div>
          <div className="hero-visual">
            <ScanConsole />
          </div>
        </div>
      </section>

      <section className="landing-section">
        <div className="container">
          <h2 className="section-title">Manual document checks don't scale, and forgeries keep improving.</h2>
          <div className="reason-grid">
            <div className="reason-card">
              <div className="reason-figure">~30 sec</div>
              <p>is roughly how long a busy front desk can spend per applicant &mdash; not enough time to catch a well-made forgery by eye.</p>
            </div>
            <div className="reason-card">
              <div className="reason-figure">5 checks</div>
              <p>run automatically here in place of a single visual glance: extraction, face match, tamper detection, a database check, and a watchlist screen.</p>
            </div>
            <div className="reason-card">
              <div className="reason-figure">1 report</div>
              <p>gives the officer a plain-language reason for every flag, so the decision is defensible, not a gut call.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-section landing-section-alt">
        <div className="container">
          <h2 className="section-title">Three steps from document to decision.</h2>
          <div className="steps-row">
            {STEPS.map((step, i) => (
              <div className="step-card" key={step.title}>
                <div className="step-index mono">{String(i + 1).padStart(2, '0')}</div>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-section">
        <div className="container">
          <h2 className="section-title">What each check is actually looking for.</h2>
          <div className="checks-list">
            {CHECKS.map((c) => (
              <div className="checks-list-item" key={c.name}>
                <h4>{c.name}</h4>
                <p>{c.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="landing-cta">
        <div className="container landing-cta-inner">
          <div>
            <h2 className="section-title">Run your first screening in the demo.</h2>
            <p className="hero-lead">All data in this prototype is simulated and stored only in your browser.</p>
          </div>
          <Link to="/signup" className="btn btn-primary">Create an account</Link>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="container">
          <span className="mono">FIS &mdash; Fake Identity Screening</span>
          <span>Built for Smart India Hackathon 2026 &middot; Frontend prototype</span>
        </div>
      </footer>
    </div>
  );
}
