import { useEffect, useRef, useState } from 'react';
import './CameraCapture.css';

const CHALLENGES = [
  { type: 'blink', label: 'Please blink' },
  { type: 'head_turn', label: 'Please turn your head slightly' },
];

const BURST_FRAME_COUNT = 12;
const BURST_INTERVAL_MS = 150; // ~12 frames * 150ms = ~1.8s burst window

/**
 * Captures a short burst of webcam frames while the user performs a
 * liveness challenge (blink or head-turn), instead of a single still photo.
 *
 * Produces:
 *   - frames: File[]  — a burst of JPEG frames, ready to append to FormData
 *   - challenge: 'blink' | 'head_turn'  — which challenge was used
 * via onCapture(frames, challenge), matching what
 * POST /api/v1/face-verification/verify expects (live_frames[] + challenge).
 */
export default function LivenessCapture({ captured, onCapture, onRetake }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [status, setStatus] = useState('idle'); // idle | starting | live | counting | capturing | error
  const [error, setError] = useState('');
  const [challenge, setChallenge] = useState(null);
  const [countdown, setCountdown] = useState(0);
  const [captureProgress, setCaptureProgress] = useState(0);

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  async function startCamera() {
    setStatus('starting');
    setError('');
    // Pick a random challenge each attempt
    setChallenge(CHALLENGES[Math.floor(Math.random() * CHALLENGES.length)]);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 480 }, height: { ideal: 360 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setStatus('live');
    } catch (err) {
      setStatus('error');
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError('Camera access was blocked. Allow camera permission for this site and try again.');
      } else if (err.name === 'NotFoundError') {
        setError('No camera was found on this device.');
      } else {
        setError('Could not start the camera on this device or browser.');
      }
    }
  }

  function grabFrame() {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return null;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    // Flip horizontally so captured frames match what the person saw (mirror preview)
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas;
  }

  function canvasToFile(canvas, index) {
    return new Promise((resolve) => {
      canvas.toBlob(
        (blob) => resolve(new File([blob], `frame_${index}.jpg`, { type: 'image/jpeg' })),
        'image/jpeg',
        0.85
      );
    });
  }

  async function runBurstCapture() {
    setStatus('counting');
    // Give the user a beat to read the instruction before frames start.
    for (let c = 2; c >= 1; c--) {
      setCountdown(c);
      await new Promise((r) => setTimeout(r, 500));
    }
    setCountdown(0);
    setStatus('capturing');

    const frames = [];
    for (let i = 0; i < BURST_FRAME_COUNT; i++) {
      const canvas = grabFrame();
      if (canvas) {
        const file = await canvasToFile(canvas, i);
        frames.push(file);
      }
      setCaptureProgress(Math.round(((i + 1) / BURST_FRAME_COUNT) * 100));
      await new Promise((r) => setTimeout(r, BURST_INTERVAL_MS));
    }

    stopCamera();
    setStatus('idle');
    setCaptureProgress(0);

    if (frames.length < 5) {
      setStatus('error');
      setError('Could not capture enough frames. Please try again.');
      return;
    }

    onCapture(frames, challenge.type);
  }

  function handleRetake() {
    onRetake();
    startCamera();
  }

  // Stop the camera if the component unmounts while still streaming
  useEffect(() => () => stopCamera(), []);

  if (captured) {
    return (
      <div className="camera-box">
        <div className="camera-frame">
          <img src={captured.previewUrl} alt="Captured for face match" className="camera-captured-img" />
        </div>
        <div className="camera-actions">
          <span className="camera-status-tag camera-status-done">
            <span className="camera-dot" /> {captured.frames.length} frames captured ({captured.challenge.replace('_', ' ')})
          </span>
          <button type="button" className="btn btn-outline btn-sm" onClick={handleRetake}>Retake</button>
        </div>
      </div>
    );
  }

  return (
    <div className="camera-box">
      <div className={`camera-frame ${status === 'live' || status === 'counting' || status === 'capturing' ? 'is-live' : ''}`}>
        <video ref={videoRef} className="camera-video" muted playsInline />
        {status === 'idle' || status === 'starting' || status === 'error' ? (
          <div className="camera-overlay">
            <div className="camera-overlay-icon">
              <svg width="22" height="18" viewBox="0 0 22 18" fill="none">
                <rect x="1" y="4" width="20" height="13" rx="2" stroke="currentColor" strokeWidth="1.4" />
                <path d="M7 4L9 1H13L15 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="11" cy="10.5" r="3.5" stroke="currentColor" strokeWidth="1.4" />
              </svg>
            </div>
            <div className="camera-overlay-label">Live liveness capture</div>
            <div className="camera-overlay-hint">
              {status === 'error' ? error : 'Your browser will ask permission to use the camera.'}
            </div>
          </div>
        ) : null}

        {status === 'counting' && (
          <div className="camera-overlay">
            <div className="camera-overlay-label" style={{ fontSize: '1.4rem' }}>
              {challenge?.label}
            </div>
            <div className="camera-overlay-hint">Starting in {countdown}…</div>
          </div>
        )}

        {status === 'capturing' && (
          <div className="camera-overlay" style={{ justifyContent: 'flex-end', paddingBottom: 'var(--sp-3)' }}>
            <div className="camera-overlay-label">{challenge?.label} — hold steady</div>
            <div style={{ width: '80%', height: 4, background: 'rgba(255,255,255,0.2)', borderRadius: 2 }}>
              <div style={{ width: `${captureProgress}%`, height: '100%', background: 'var(--focus)', borderRadius: 2, transition: 'width 0.15s linear' }} />
            </div>
          </div>
        )}
      </div>

      <div className="camera-actions">
        {status === 'live' ? (
          <>
            <span className="camera-status-tag camera-status-live">
              <span className="camera-dot" /> live — {challenge?.label.toLowerCase()}
            </span>
            <button type="button" className="btn btn-primary btn-sm" onClick={runBurstCapture}>Start capture</button>
          </>
        ) : status === 'counting' || status === 'capturing' ? (
          <span className="camera-status-tag camera-status-live">
            <span className="camera-dot" /> {status === 'counting' ? 'get ready…' : 'capturing…'}
          </span>
        ) : (
          <button type="button" className="btn btn-outline btn-sm" onClick={startCamera} disabled={status === 'starting'}>
            {status === 'starting' ? 'Starting camera…' : status === 'error' ? 'Try again' : 'Start camera'}
          </button>
        )}
      </div>
    </div>
  );
}
