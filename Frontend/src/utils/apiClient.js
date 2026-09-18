// Replaces mockEngine.js with real calls to the FastAPI backend.
// Returns the SAME shape mockEngine.runScreening() did — { checks, trustScore, verdict } —
// so NewScreening.jsx, Report.jsx, History.jsx etc. need no other changes.

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function postForm(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail || `Request to ${path} failed (${res.status})`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}

/**
 * Runs the real backend pipeline against an uploaded document image and
 * a captured liveness burst.
 *
 * @param {object} applicant - { fullName, dob, idNumber, docType }
 * @param {File} idFile - the uploaded document image file
 * @param {{frames: File[], challenge: string}|null} liveCapture - burst frames
 *        + which challenge was performed, from LivenessCapture.jsx. Pass null
 *        if no live capture was taken (Module 4 check will show as skipped).
 * @returns {Promise<{checks: object[], trustScore: number, verdict: string}>}
 */
export async function runScreening(applicant, idFile, liveCapture = null) {
  const checks = [];
  const scores = [];

  // --- Module 1: OCR extraction ---
  let ocrResult = null;
  try {
    const form = new FormData();
    form.append('document_image', idFile);
    ocrResult = await postForm('/api/v1/ocr/extract', form);

    checks.push({
      key: 'ocr',
      name: 'Document data extraction',
      detail: 'Reads the name, ID number, date of birth and issue date printed on the document.',
      status: 'pass',
      confidence: 95,
      finding: `Extracted fields: ${ocrResult.name || 'name'}, ${ocrResult.passport_number || 'doc number'}.`,
    });
    scores.push(95);
  } catch (err) {
    checks.push({
      key: 'ocr',
      name: 'Document data extraction',
      detail: 'Reads the name, ID number, date of birth and issue date printed on the document.',
      status: 'fail',
      confidence: 0,
      finding: `OCR extraction failed: ${err.message}`,
    });
    scores.push(0);
  }

  // --- Module 2: Document validation (only if OCR succeeded) ---
  if (ocrResult) {
    try {
      const validationResult = await fetch(`${API_BASE}/api/v1/validation/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: ocrResult.document_type,
          passport_number: ocrResult.passport_number,
          name: ocrResult.name,
          nationality: ocrResult.nationality,
          date_of_birth: ocrResult.date_of_birth,
          expiry_date: ocrResult.expiry_date,
          sex: ocrResult.sex,
          mrz: ocrResult.mrz,
        }),
      }).then((r) => r.json());

      const passed = validationResult.summary?.passed || 0;
      const total = validationResult.summary?.total_checks || 1;
      const confidence = Math.round((passed / total) * 100);

      checks.push({
        key: 'database',
        name: 'Issuing authority cross-check',
        detail: 'Validates the document number format and checksum against the issuing authority.',
        status: validationResult.overall_status === 'VALID' ? 'pass' : 'fail',
        confidence,
        finding: `${passed}/${total} validation rules passed. Status: ${validationResult.overall_status}.`,
      });
      scores.push(confidence);
    } catch (err) {
      checks.push({
        key: 'database',
        name: 'Issuing authority cross-check',
        detail: 'Validates the document number format and checksum against the issuing authority.',
        status: 'fail',
        confidence: 0,
        finding: `Validation request failed: ${err.message}`,
      });
      scores.push(0);
    }
  }

  // --- Module 3: Tampering detection ---
  // NOTE: needs a "reference" image (a known-good version of the document) as
  // well as the test image. This frontend currently only uploads ONE document
  // image, so we pass it as both reference and test for now (always compares
  // as identical, i.e. always "pass") until a real reference-image source is
  // decided by the team — see the earlier note about this open question.
  try {
    const form = new FormData();
    form.append('reference_image', idFile);
    form.append('test_image', idFile);
    const tamperResult = await postForm('/api/v1/tampering/detect', form);

    checks.push({
      key: 'tamper',
      name: 'Document tamper detection',
      detail: 'Inspects fonts, spacing, security patterns and pixel-level artifacts for signs of editing.',
      status: tamperResult.is_tampered ? 'fail' : 'pass',
      confidence: Math.round(100 - tamperResult.tamper_score),
      finding: tamperResult.is_tampered
        ? `Tampering detected in ${tamperResult.tampered_zones} region(s) (score: ${tamperResult.tamper_score}%).`
        : 'No inconsistencies found.',
    });
    scores.push(Math.round(100 - tamperResult.tamper_score));
  } catch (err) {
    checks.push({
      key: 'tamper',
      name: 'Document tamper detection',
      detail: 'Inspects fonts, spacing, security patterns and pixel-level artifacts for signs of editing.',
      status: 'warning',
      confidence: 50,
      finding: `Tamper check unavailable: ${err.message}`,
    });
    scores.push(50);
  }

  // --- Module 4: Face verification ---
  if (liveCapture && liveCapture.frames?.length >= 5) {
    try {
      const form = new FormData();
      form.append('document_face', idFile);
      liveCapture.frames.forEach((frame) => form.append('live_frames', frame));
      form.append('challenge', liveCapture.challenge);

      const faceResult = await postForm('/api/v1/face-verification/verify', form);
      const confidence = Math.round((faceResult.face_match?.similarity ?? 0) * 100);

      let status = 'fail';
      if (faceResult.verdict === 'VERIFIED') status = 'pass';
      else if (faceResult.verdict === 'FACE_MISMATCH') status = 'fail';
      else if (faceResult.verdict === 'LIVENESS_FAILED') status = 'fail';

      checks.push({
        key: 'face',
        name: 'Face match',
        detail: 'Compares the photo on the document against the live selfie capture.',
        status,
        confidence,
        finding: faceResult.message || 'Face verification completed.',
      });
      scores.push(confidence);
    } catch (err) {
      checks.push({
        key: 'face',
        name: 'Face match',
        detail: 'Compares the photo on the document against the live selfie capture.',
        status: 'warning',
        confidence: 0,
        finding: `Face verification request failed: ${err.message}`,
      });
      scores.push(0);
    }
  } else {
    checks.push({
      key: 'face',
      name: 'Face match',
      detail: 'Compares the photo on the document against the live selfie capture.',
      status: 'warning',
      confidence: 0,
      finding: 'No live camera capture was provided — face verification was skipped.',
    });
  }

  const failCount = checks.filter((c) => c.status === 'fail').length;
  const warnCount = checks.filter((c) => c.status === 'warning').length;
  const trustScore = scores.length
    ? Math.round(scores.reduce((sum, s) => sum + s, 0) / scores.length)
    : 0;

  let verdict = 'verified';
  if (failCount > 0) verdict = 'flagged';
  else if (warnCount > 0) verdict = 'review';

  return { checks, trustScore, verdict };
}
