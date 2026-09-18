// Lightweight deterministic-ish hash so the same input tends to reproduce
// a similar result during a demo, with a touch of randomness layered on top.
function seededRandom(seed) {
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

function hashString(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (h << 5) - h + str.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

function pick(seed, min, max) {
  return Math.round(min + seededRandom(seed) * (max - min));
}

// Checks known to raise suspicion when present in a document number or name,
// purely so the demo has a repeatable way to show a flagged case.
const SUSPECT_MARKERS = ['test', 'fake', '0000', 'xxxx', 'sample'];

export function runScreening(applicant, fileNames = {}) {
  const seedBase = hashString(
    (applicant.fullName || '') + (applicant.idNumber || '') + Date.now().toString().slice(0, 6)
  );

  const idLower = (applicant.idNumber || '').toLowerCase();
  const nameLower = (applicant.fullName || '').toLowerCase();
  const looksSuspect = SUSPECT_MARKERS.some((m) => idLower.includes(m) || nameLower.includes(m));

  const checks = [];

  // 1. OCR field extraction
  checks.push({
    key: 'ocr',
    name: 'Document data extraction',
    detail: 'Reads the name, ID number, date of birth and issue date printed on the document.',
    status: 'pass',
    confidence: pick(seedBase + 1, 92, 99),
    finding: 'All required fields were located and matched the expected layout for the selected document type.',
  });

  // 2. Face match
  const faceConfidence = looksSuspect ? pick(seedBase + 2, 30, 55) : pick(seedBase + 2, 82, 99);
  checks.push({
    key: 'face',
    name: 'Face match',
    detail: 'Compares the photo on the document against the live camera capture.',
    status: faceConfidence >= 75 ? 'pass' : faceConfidence >= 55 ? 'warning' : 'fail',
    confidence: faceConfidence,
    finding:
      faceConfidence >= 75
        ? 'The live capture and document photo show consistent facial landmarks.'
        : faceConfidence >= 55
        ? 'Some facial landmarks differ. Lighting or angle may be the cause — recommend a second capture.'
        : 'The live capture and document photo do not appear to show the same person.',
  });

  // 3. Tamper / forgery detection
  const tamperConfidence = looksSuspect ? pick(seedBase + 3, 20, 45) : pick(seedBase + 3, 85, 99);
  checks.push({
    key: 'tamper',
    name: 'Document tamper detection',
    detail: 'Inspects fonts, spacing, security patterns and pixel-level artifacts for signs of editing.',
    status: tamperConfidence >= 80 ? 'pass' : tamperConfidence >= 60 ? 'warning' : 'fail',
    confidence: tamperConfidence,
    finding:
      tamperConfidence >= 80
        ? 'No inconsistencies found in fonts, spacing or the security watermark.'
        : tamperConfidence >= 60
        ? 'Minor irregularities in character spacing near the date field — within tolerance but noted.'
        : 'Font inconsistency and watermark misalignment detected, consistent with digital editing.',
  });

  // 4. Issuing authority cross-check
  const dbConfidence = looksSuspect ? pick(seedBase + 4, 10, 40) : pick(seedBase + 4, 88, 99);
  checks.push({
    key: 'database',
    name: 'Issuing authority cross-check',
    detail: 'Validates the document number format and checksum against the issuing authority.',
    status: dbConfidence >= 75 ? 'pass' : dbConfidence >= 50 ? 'warning' : 'fail',
    confidence: dbConfidence,
    finding:
      dbConfidence >= 75
        ? 'Document number format and checksum are valid for the declared issuing authority.'
        : dbConfidence >= 50
        ? 'Checksum passed but the record could not be reached for live confirmation.'
        : 'Document number format is invalid or does not match any known issuing series.',
  });

  // 5. Watchlist screening
  const watchlistHit = looksSuspect ? pick(seedBase + 5, 0, 100) < 70 : pick(seedBase + 5, 0, 100) < 4;
  checks.push({
    key: 'watchlist',
    name: 'Watchlist screening',
    detail: 'Checks the applicant name and document number against known fraud watchlists.',
    status: watchlistHit ? 'fail' : 'pass',
    confidence: watchlistHit ? pick(seedBase + 6, 60, 90) : pick(seedBase + 6, 95, 100),
    finding: watchlistHit
      ? 'A partial match was found on an internal watchlist. Manual review is required before proceeding.'
      : 'No matches found on any monitored watchlist.',
  });

  const failCount = checks.filter((c) => c.status === 'fail').length;
  const warnCount = checks.filter((c) => c.status === 'warning').length;

  const trustScore = Math.round(
    checks.reduce((sum, c) => sum + c.confidence, 0) / checks.length
  );

  let verdict = 'verified';
  if (failCount > 0) verdict = 'flagged';
  else if (warnCount > 0) verdict = 'review';

  return { checks, trustScore, verdict };
}

export const VERDICT_LABEL = {
  verified: 'Verified',
  flagged: 'Flagged',
  review: 'Manual review',
};
