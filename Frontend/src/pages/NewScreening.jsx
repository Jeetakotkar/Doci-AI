import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { runScreening } from '../utils/apiClient';
import { generateCaseId } from '../utils/format';
import LivenessCapture from '../components/LivenessCapture';
import './NewScreening.css';

const DOC_TYPES = ['Aadhaar Card', 'PAN Card', 'Passport', 'Driving Licence', 'Voter ID'];

const PROCESS_STEPS = [
  'Reading document fields',
  'Comparing live capture to document photo',
  'Checking for signs of tampering',
  'Cross-checking issuing authority',
  'Screening against watchlists',
];

function FileDrop({ label, hint, file, onChange }) {
  const [preview, setPreview] = useState(null);

  function handleFile(f) {
    if (!f) return;
    onChange(f);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result);
    reader.readAsDataURL(f);
  }

  return (
    <label className="file-drop">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => handleFile(e.target.files[0])}
        hidden
      />
      {preview ? (
        <img src={preview} alt="" className="file-drop-preview" />
      ) : (
        <div className="file-drop-icon">+</div>
      )}
      <div>
        <div className="file-drop-label">{file ? file.name : label}</div>
        <div className="file-drop-hint">{hint}</div>
      </div>
    </label>
  );
}

export default function NewScreening() {
  const { addScreening, screenings } = useData();
  const navigate = useNavigate();

  const [applicant, setApplicant] = useState({ fullName: '', dob: '', idNumber: '', docType: DOC_TYPES[0] });
  const [idFile, setIdFile] = useState(null);
  const [liveCapture, setLiveCapture] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [activeStep, setActiveStep] = useState(-1);
  const [errors, setErrors] = useState({});

  function update(field) {
    return (e) => setApplicant((a) => ({ ...a, [field]: e.target.value }));
  }

  function validate() {
    const errs = {};
    if (!applicant.fullName.trim()) errs.fullName = 'Enter the applicant\u2019s full name.';
    if (!applicant.idNumber.trim()) errs.idNumber = 'Enter the document number.';
    if (!applicant.dob) errs.dob = 'Enter the date of birth.';
    if (!idFile) errs.idFile = 'Upload a photo of the ID document.';
    if (!liveCapture) errs.liveCapture = 'Capture a live photo using the camera for the face match.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;
    setProcessing(true);
    setActiveStep(0);

    PROCESS_STEPS.forEach((_, i) => {
      setTimeout(() => setActiveStep(i), i * 650);
    });

    setTimeout(async () => {
      const { checks, trustScore, verdict } = await runScreening(applicant, idFile, liveCapture);
      const record = {
        id: generateCaseId(screenings.length),
        applicant,
        createdAt: new Date().toISOString(),
        officer: 'You',
        verdict,
        trustScore,
        checks,
        resolution: verdict === 'verified' ? 'Approved' : 'Pending review',
      };
      addScreening(record);
      navigate(`/app/report/${record.id}`);
    }, PROCESS_STEPS.length * 650 + 500);
  }

  if (processing) {
    return (
      <div className="processing-screen">
        <p className="page-eyebrow">Screening in progress</p>
        <h1 className="page-title" style={{ marginBottom: 'var(--sp-6)' }}>
          Running checks on {applicant.fullName || 'this applicant'}
        </h1>
        <ul className="process-list">
          {PROCESS_STEPS.map((step, i) => (
            <li key={step} className={i <= activeStep ? 'done' : i === activeStep + 1 ? 'active' : ''}>
              <span className="process-index mono">{String(i + 1).padStart(2, '0')}</span>
              {step}
              {i <= activeStep && <span className="process-check">&#10003;</span>}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <p className="page-eyebrow">New case</p>
          <h1 className="page-title">Screen an identity document</h1>
          <p className="page-subtitle">Enter the applicant's details, upload the ID document, and capture a live photo with the camera to run the automated checks.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="screening-form">
        <div className="card screening-form-fields">
          <h2 className="form-section-title">Applicant details</h2>
          <div className="form-grid">
            <div className="field">
              <label htmlFor="fullName">Full name</label>
              <input id="fullName" value={applicant.fullName} onChange={update('fullName')} placeholder="As printed on the document" />
              {errors.fullName && <span className="field-error">{errors.fullName}</span>}
            </div>
            <div className="field">
              <label htmlFor="dob">Date of birth</label>
              <input id="dob" type="date" value={applicant.dob} onChange={update('dob')} />
              {errors.dob && <span className="field-error">{errors.dob}</span>}
            </div>
            <div className="field">
              <label htmlFor="docType">Document type</label>
              <select id="docType" value={applicant.docType} onChange={update('docType')}>
                {DOC_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="field">
              <label htmlFor="idNumber">Document number</label>
              <input id="idNumber" value={applicant.idNumber} onChange={update('idNumber')} placeholder="e.g. 4821 9931 0053" />
              {errors.idNumber && <span className="field-error">{errors.idNumber}</span>}
            </div>
          </div>
        </div>

        <div className="card screening-form-fields">
          <h2 className="form-section-title">Photo capture</h2>
          <div className="form-grid">
            <div className="field">
              <FileDrop label="Upload ID document photo" hint="Front side, clearly lit, JPG or PNG" file={idFile} onChange={setIdFile} />
              {errors.idFile && <span className="field-error">{errors.idFile}</span>}
            </div>
            <div className="field">
              <label>Live camera face capture</label>
              <LivenessCapture
                captured={liveCapture}
                onCapture={async (frames, challengeType) => {
                  // Build a preview from the middle frame — same frame the
                  // backend uses for the actual face-match comparison.
                  const middleFrame = frames[Math.floor(frames.length / 2)];
                  const previewUrl = URL.createObjectURL(middleFrame);
                  setLiveCapture({ frames, challenge: challengeType, previewUrl });
                }}
                onRetake={() => setLiveCapture(null)}
              />
              {errors.liveCapture && <span className="field-error">{errors.liveCapture}</span>}
            </div>
          </div>
        </div>

        <div className="screening-form-actions">
          <p className="field-hint">The uploaded photo and camera capture stay in your browser for this demo &mdash; nothing is sent anywhere.</p>
          <button className="btn btn-primary" type="submit">Run screening</button>
        </div>
      </form>
    </div>
  );
}
