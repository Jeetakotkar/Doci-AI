import { useEffect, useRef, useState } from 'react';
import './CameraCapture.css';

export default function CameraCapture({ capturedImage, onCapture, onRetake }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [status, setStatus] = useState('idle'); // idle | starting | live | error
  const [error, setError] = useState('');

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }

  async function startCamera() {
    setStatus('starting');
    setError('');
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

  function handleCapture() {
    const video = videoRef.current;
    if (!video || !video.videoWidth) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    // Flip horizontally so the captured photo matches what the person saw (mirror preview)
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
    stopCamera();
    setStatus('idle');
    onCapture(dataUrl);
  }

  function handleRetake() {
    onRetake();
    startCamera();
  }

  // Stop the camera if the component unmounts while still streaming
  useEffect(() => () => stopCamera(), []);

  if (capturedImage) {
    return (
      <div className="camera-box">
        <div className="camera-frame">
          <img src={capturedImage} alt="Captured for face match" className="camera-captured-img" />
        </div>
        <div className="camera-actions">
          <span className="camera-status-tag camera-status-done">
            <span className="camera-dot" /> photo captured
          </span>
          <button type="button" className="btn btn-outline btn-sm" onClick={handleRetake}>Retake photo</button>
        </div>
      </div>
    );
  }

  return (
    <div className="camera-box">
      <div className={`camera-frame ${status === 'live' ? 'is-live' : ''}`}>
        <video ref={videoRef} className="camera-video" muted playsInline />
        {status !== 'live' && (
          <div className="camera-overlay">
            <div className="camera-overlay-icon">
              <svg width="22" height="18" viewBox="0 0 22 18" fill="none">
                <rect x="1" y="4" width="20" height="13" rx="2" stroke="currentColor" strokeWidth="1.4" />
                <path d="M7 4L9 1H13L15 4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="11" cy="10.5" r="3.5" stroke="currentColor" strokeWidth="1.4" />
              </svg>
            </div>
            <div className="camera-overlay-label">Live camera face capture</div>
            <div className="camera-overlay-hint">
              {status === 'error' ? error : 'Your browser will ask permission to use the camera.'}
            </div>
          </div>
        )}
      </div>

      <div className="camera-actions">
        {status === 'live' ? (
          <>
            <span className="camera-status-tag camera-status-live">
              <span className="camera-dot" /> live
            </span>
            <button type="button" className="btn btn-primary btn-sm" onClick={handleCapture}>Capture photo</button>
          </>
        ) : (
          <button type="button" className="btn btn-outline btn-sm" onClick={startCamera} disabled={status === 'starting'}>
            {status === 'starting' ? 'Starting camera…' : status === 'error' ? 'Try again' : 'Start camera'}
          </button>
        )}
      </div>
    </div>
  );
}
