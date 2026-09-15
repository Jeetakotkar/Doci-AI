"""
Liveness detection via challenge-response.

Approach:
- Frontend asks the user to do ONE of: blink, or turn head left/right.
- Frontend sends a short burst of frames (e.g. 10-15 frames over ~1.5-2 sec) captured during the challenge.
- We run mediapipe FaceMesh on each frame, track:
    - Eye Aspect Ratio (EAR) over time -> detects a blink (EAR dips then recovers)
    - Nose tip X position relative to face width -> detects head turn
- A REAL person doing the challenge produces motion. A static photo held up to
  the camera produces ~zero motion in these signals -> liveness fails.

This deliberately does NOT try to be a full anti-spoofing deep model (texture/
depth based). That's a valid v2 upgrade, but challenge-response is simpler,
explainable to judges, and demoable live in front of them.
"""

from dataclasses import dataclass
from enum import Enum
import numpy as np
import cv2
import mediapipe as mp

# NOTE: requires mediapipe==0.10.14 (pinned in requirements.txt).
# Newer mediapipe (0.10.2x+) removed mp.solutions.face_mesh in favor of the
# Tasks API (FaceLandmarker + downloadable .task model file). Stick to 0.10.14
# unless you deliberately migrate — don't `pip install -U mediapipe` blindly.
mp_face_mesh = mp.solutions.face_mesh

# Landmark indices for mediapipe's 468-point face mesh
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
NOSE_TIP = 1
LEFT_FACE_EDGE = 234
RIGHT_FACE_EDGE = 454

EAR_BLINK_THRESHOLD = 0.21       # below this = eyes considered closed
EAR_DROP_MIN = 0.06              # min drop from baseline to count as a real blink
HEAD_TURN_MIN_DELTA = 0.12       # min normalized nose-position shift to count as a turn


class ChallengeType(str, Enum):
    BLINK = "blink"
    HEAD_TURN = "head_turn"


@dataclass
class LivenessResult:
    passed: bool
    challenge: str
    confidence: float          # 0-1
    reason: str
    frames_with_face: int
    frames_total: int


def _eye_aspect_ratio(landmarks, eye_indices, image_w, image_h):
    pts = np.array([
        (landmarks[i].x * image_w, landmarks[i].y * image_h)
        for i in eye_indices
    ])
    # vertical distances
    v1 = np.linalg.norm(pts[1] - pts[5])
    v2 = np.linalg.norm(pts[2] - pts[4])
    # horizontal distance
    h = np.linalg.norm(pts[0] - pts[3])
    if h == 0:
        return 0.0
    return (v1 + v2) / (2.0 * h)


def _normalized_nose_x(landmarks):
    """Nose tip X position normalized between the left and right face edges.
    ~0.5 = facing camera. Moves toward 0 or 1 as head turns."""
    nose_x = landmarks[NOSE_TIP].x
    left_x = landmarks[LEFT_FACE_EDGE].x
    right_x = landmarks[RIGHT_FACE_EDGE].x
    span = right_x - left_x
    if span == 0:
        return 0.5
    return (nose_x - left_x) / span


def analyze_liveness(frames: list[np.ndarray], challenge: ChallengeType) -> LivenessResult:
    """
    frames: list of BGR images (as read by cv2.imdecode) in chronological order.
    challenge: which challenge the frontend asked the user to perform.
    """
    if len(frames) < 5:
        return LivenessResult(
            passed=False, challenge=challenge.value, confidence=0.0,
            reason="Not enough frames submitted (need at least 5).",
            frames_with_face=0, frames_total=len(frames),
        )

    ear_series = []
    nose_x_series = []
    frames_with_face = 0

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:
        for frame in frames:
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb)

            if not result.multi_face_landmarks:
                continue

            frames_with_face += 1
            landmarks = result.multi_face_landmarks[0].landmark

            left_ear = _eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
            right_ear = _eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
            ear_series.append((left_ear + right_ear) / 2.0)

            nose_x_series.append(_normalized_nose_x(landmarks))

    if frames_with_face < max(3, len(frames) // 2):
        return LivenessResult(
            passed=False, challenge=challenge.value, confidence=0.0,
            reason=f"Face detected in only {frames_with_face}/{len(frames)} frames. "
                   f"Ask user to stay centered and well-lit.",
            frames_with_face=frames_with_face, frames_total=len(frames),
        )

    if challenge == ChallengeType.BLINK:
        return _check_blink(ear_series, frames_with_face, len(frames))
    else:
        return _check_head_turn(nose_x_series, frames_with_face, len(frames))


def _check_blink(ear_series, frames_with_face, frames_total) -> LivenessResult:
    ear = np.array(ear_series)
    baseline = np.percentile(ear, 90)   # "eyes open" reference level
    min_ear = ear.min()
    drop = baseline - min_ear

    dipped_below_threshold = np.any(ear < EAR_BLINK_THRESHOLD)
    sufficient_drop = drop >= EAR_DROP_MIN

    passed = bool(dipped_below_threshold and sufficient_drop)
    confidence = float(np.clip(drop / (EAR_DROP_MIN * 2), 0, 1))

    reason = (
        "Blink detected: eye-aspect-ratio dipped and recovered."
        if passed else
        "No clear blink detected in the frame sequence — looks static or motion insufficient."
    )

    return LivenessResult(
        passed=passed, challenge=ChallengeType.BLINK.value, confidence=confidence,
        reason=reason, frames_with_face=frames_with_face, frames_total=frames_total,
    )


def _check_head_turn(nose_x_series, frames_with_face, frames_total) -> LivenessResult:
    nose_x = np.array(nose_x_series)
    delta = nose_x.max() - nose_x.min()

    passed = bool(delta >= HEAD_TURN_MIN_DELTA)
    confidence = float(np.clip(delta / (HEAD_TURN_MIN_DELTA * 2), 0, 1))

    reason = (
        "Head turn detected: nose position shifted significantly across frames."
        if passed else
        "No significant head movement detected — looks static."
    )

    return LivenessResult(
        passed=passed, challenge=ChallengeType.HEAD_TURN.value, confidence=confidence,
        reason=reason, frames_with_face=frames_with_face, frames_total=frames_total,
    )
