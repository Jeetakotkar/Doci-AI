from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
import mediapipe as mp

# ---------------- Render + Windows compatible ----------------
try:
    mp_face_mesh = mp.solutions.face_mesh
except AttributeError:
    from mediapipe.python import solutions as mp_solutions
    mp_face_mesh = mp_solutions.face_mesh
# -------------------------------------------------------------

# Landmark indices for Mediapipe FaceMesh (468 landmarks)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
NOSE_TIP = 1
LEFT_FACE_EDGE = 234
RIGHT_FACE_EDGE = 454

EAR_BLINK_THRESHOLD = 0.21
EAR_DROP_MIN = 0.06
HEAD_TURN_MIN_DELTA = 0.12


class ChallengeType(str, Enum):
    BLINK = "blink"
    HEAD_TURN = "head_turn"


@dataclass
class LivenessResult:
    passed: bool
    challenge: str
    confidence: float
    reason: str
    frames_with_face: int
    frames_total: int


def _eye_aspect_ratio(landmarks, eye_indices, image_w, image_h):
    pts = np.array([
        (landmarks[i].x * image_w, landmarks[i].y * image_h)
        for i in eye_indices
    ])

    v1 = np.linalg.norm(pts[1] - pts[5])
    v2 = np.linalg.norm(pts[2] - pts[4])
    h = np.linalg.norm(pts[0] - pts[3])

    if h == 0:
        return 0.0

    return (v1 + v2) / (2.0 * h)


def _normalized_nose_x(landmarks):
    nose_x = landmarks[NOSE_TIP].x
    left_x = landmarks[LEFT_FACE_EDGE].x
    right_x = landmarks[RIGHT_FACE_EDGE].x

    span = right_x - left_x
    if span == 0:
        return 0.5

    return (nose_x - left_x) / span


def analyze_liveness(frames: list[np.ndarray], challenge: ChallengeType) -> LivenessResult:
    """
    Analyze blink or head-turn liveness from a sequence of BGR frames.
    """

    if len(frames) < 5:
        return LivenessResult(
            passed=False,
            challenge=challenge.value,
            confidence=0.0,
            reason="Not enough frames submitted (need at least 5).",
            frames_with_face=0,
            frames_total=len(frames),
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
            passed=False,
            challenge=challenge.value,
            confidence=0.0,
            reason=f"Face detected in only {frames_with_face}/{len(frames)} frames. Ask user to stay centered and well-lit.",
            frames_with_face=frames_with_face,
            frames_total=len(frames),
        )

    if challenge == ChallengeType.BLINK:
        return _check_blink(ear_series, frames_with_face, len(frames))

    return _check_head_turn(nose_x_series, frames_with_face, len(frames))


def _check_blink(ear_series, frames_with_face, frames_total):
    ear = np.array(ear_series)

    baseline = np.percentile(ear, 90)
    min_ear = ear.min()
    drop = baseline - min_ear

    dipped = np.any(ear < EAR_BLINK_THRESHOLD)
    sufficient_drop = drop >= EAR_DROP_MIN

    passed = bool(dipped and sufficient_drop)
    confidence = float(np.clip(drop / (EAR_DROP_MIN * 2), 0, 1))

    reason = (
        "Blink detected: eye-aspect-ratio dipped and recovered."
        if passed
        else "No clear blink detected in the frame sequence."
    )

    return LivenessResult(
        passed=passed,
        challenge=ChallengeType.BLINK.value,
        confidence=confidence,
        reason=reason,
        frames_with_face=frames_with_face,
        frames_total=frames_total,
    )


def _check_head_turn(nose_x_series, frames_with_face, frames_total):
    nose = np.array(nose_x_series)

    delta = nose.max() - nose.min()

    passed = bool(delta >= HEAD_TURN_MIN_DELTA)
    confidence = float(np.clip(delta / (HEAD_TURN_MIN_DELTA * 2), 0, 1))

    reason = (
        "Head turn detected: nose position shifted significantly across frames."
        if passed
        else "No significant head movement detected."
    )

    return LivenessResult(
        passed=passed,
        challenge=ChallengeType.HEAD_TURN.value,
        confidence=confidence,
        reason=reason,
        frames_with_face=frames_with_face,
        frames_total=frames_total,
    )