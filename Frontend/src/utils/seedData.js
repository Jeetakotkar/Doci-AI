const NAMES = [
  'Ravi Kumar Sharma', 'Ananya Iyer', 'Mohammed Faizan', 'Priya Nair',
  'Arjun Deshmukh', 'Simran Kaur', 'Vikram Rathore', 'Neha Joshi',
  'Sandeep Verma', 'Divya Menon', 'Karan Malhotra', 'Sneha Pillai',
  'Rohit Bansal', 'Fatima Sheikh', 'Aditya Chauhan', 'Lakshmi Reddy',
];

const DOC_TYPES = ['Aadhaar Card', 'PAN Card', 'Passport', 'Driving Licence', 'Voter ID'];

function seededRandom(seed) {
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}
function pick(seed, arr) {
  return arr[Math.floor(seededRandom(seed) * arr.length)];
}
function pickNum(seed, min, max) {
  return Math.round(min + seededRandom(seed) * (max - min));
}

export function buildSeedScreenings() {
  const now = Date.now();
  const records = [];

  for (let i = 0; i < 24; i++) {
    const seed = i * 17.31 + 3;
    const failRoll = seededRandom(seed + 100);
    let verdict = 'verified';
    if (failRoll < 0.16) verdict = 'flagged';
    else if (failRoll < 0.3) verdict = 'review';

    const trustScore =
      verdict === 'flagged' ? pickNum(seed + 1, 20, 48) :
      verdict === 'review' ? pickNum(seed + 1, 55, 74) :
      pickNum(seed + 1, 85, 99);

    const daysAgo = pickNum(seed + 2, 0, 29);
    const officer = ['R. Sharma', 'A. Iyer', 'M. Faizan', 'S. Kaur'][i % 4];

    const checks = [
      { key: 'ocr', name: 'Document data extraction', status: 'pass', confidence: pickNum(seed + 3, 90, 99) },
      {
        key: 'face', name: 'Face match',
        status: verdict === 'flagged' ? 'fail' : verdict === 'review' ? 'warning' : 'pass',
        confidence: verdict === 'flagged' ? pickNum(seed + 4, 30, 50) : verdict === 'review' ? pickNum(seed + 4, 55, 74) : pickNum(seed + 4, 85, 99),
      },
      {
        key: 'tamper', name: 'Document tamper detection',
        status: verdict === 'flagged' ? pick(seed + 5, ['fail', 'warning']) : 'pass',
        confidence: verdict === 'flagged' ? pickNum(seed + 5, 25, 60) : pickNum(seed + 5, 85, 99),
      },
      {
        key: 'database', name: 'Issuing authority cross-check',
        status: verdict === 'flagged' ? pick(seed + 6, ['fail', 'warning']) : 'pass',
        confidence: verdict === 'flagged' ? pickNum(seed + 6, 20, 55) : pickNum(seed + 6, 85, 99),
      },
      {
        key: 'watchlist', name: 'Watchlist screening',
        status: verdict === 'flagged' && seededRandom(seed + 7) < 0.5 ? 'fail' : 'pass',
        confidence: pickNum(seed + 7, 70, 100),
      },
    ];

    records.push({
      id: `FIS-2026-${String(100 + i).padStart(6, '0')}`,
      applicant: {
        fullName: pick(seed + 8, NAMES),
        idNumber: `ID${pickNum(seed + 9, 100000000, 999999999)}`,
        docType: pick(seed + 10, DOC_TYPES),
        dob: `19${pickNum(seed + 11, 65, 99)}-0${pickNum(seed + 12, 1, 9)}-1${pickNum(seed + 13, 0, 8)}`,
      },
      createdAt: new Date(now - daysAgo * 86400000 - pickNum(seed + 14, 0, 80000) * 1000).toISOString(),
      officer,
      verdict,
      trustScore,
      checks,
      resolution: verdict === 'flagged' ? pick(seed + 15, ['Rejected', 'Escalated', 'Pending review']) : verdict === 'review' ? pick(seed + 16, ['Pending review', 'Approved after review']) : 'Approved',
    });
  }

  return records.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}
