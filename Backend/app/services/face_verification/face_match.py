"""
Face verification: compares the face on the identity document against the
burst of live-captured frames.

Why the previous version produced false rejections on real documents
--------------------------------------------------------------------
1. It compared ONE live frame. The pipeline already captures 12. A single
   frame may be mid-blink, motion-blurred, or off-angle. We now score all
   frames, keep the best few, and aggregate.

2. It fed the FULL document image to DeepFace. An Aadhaar/passport scan is
   mostly text; the actual portrait is a small, low-resolution, halftone-
   printed region. Detectors align poorly on it. We now crop the document
   face first, upscale it, and normalize contrast before embedding.

3. It used DeepFace's DEFAULT threshold. Those thresholds are calibrated on
   selfie-vs-selfie benchmarks (LFW etc.). Document-photo-vs-selfie is a
   different, harder domain: print halftoning, lamination glare, age gap
   between the ID photo and today. Genuine pairs routinely land 15-30%
   above the stock threshold. We apply an explicit, documented tolerance
   rather than silently inheriting a mismatched one.

4. It used a single model. ArcFace alone is noisy on degraded print. We
   average two independent models (ArcFace + Facenet512), which cuts
   variance substantially.

SECURITY NOTE - read before tuning
----------------------------------
DOC_VS_LIVE_TOLERANCE loosens the match threshold. Loosening reduces false
REJECTS (your current problem) but increases false ACCEPTS - i.e. an
impostor passing. In a fraud-screening tool the false-accept direction is
the dangerous one. Do not raise this value past ~1.35 without measuring it
against a labelled set of genuine AND impostor pairs. Tuning it until your
own face passes is not calibration; it will pass other people's faces too.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

from deepface import DeepFace

# --- models -----------------------------------------------------------
# DeepFace's published cosine thresholds for each model. These are the
# selfie-vs-selfie operating points we scale from.
MODELS: dict[str, float] = {
    "ArcFace": 0.68,
    "Facenet512": 0.30,
}

DETECTOR_BACKEND = "retinaface"
FALLBACK_DETECTOR_BACKEND = "opencv"
DISTANCE_METRIC = "cosine"

# See SECURITY NOTE above before changing.
DOC_VS_LIVE_TOLERANCE = 1.25

# Above the match threshold but below this = INCONCLUSIVE, not MISMATCH.
INCONCLUSIVE_CEILING = 1.45

# How many of the 12 burst frames to actually embed, best-quality first.
MAX_LIVE_FRAMES = 5
# Minimum pixel height for a face crop before embedding.
MIN_FACE_SIZE = 160
# Padding around the detected document face, as a fraction of box size.
FACE_CROP_PADDING = 0.25


@dataclass
class FaceMatchResult:
    matched: bool
    similarity: float          # 0-1. 0.5 == exactly at the decision threshold.
    distance: float            # aggregated, threshold-normalized ratio
    threshold: float           # always 1.0 in normalized space
    reason: str
    status: str = "MISMATCH"   # MATCH | INCONCLUSIVE | MISMATCH
    frames_used: int = 0
    frames_total: int = 0
    per_model: dict[str, float] = field(default_factory=dict)


# ----------------------------------------------------------------------
# DOCUMENT PHOTO PREPROCESSING
# ----------------------------------------------------------------------

def _enhance_for_embedding(face: np.ndarray) -> np.ndarray:
    """
    Printed ID photos are low-contrast, halftoned and small. Upscale and
    equalize luminance so the embedding model sees something closer to the
    camera-quality faces it was trained on.
    """
    height = face.shape[0]
    if height < MIN_FACE_SIZE:
        scale = MIN_FACE_SIZE / float(height)
        face = cv2.resize(
            face, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )

    # CLAHE on luminance only, so we don't shift skin tone / colour balance.
    lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lightness = clahe.apply(lightness)
    face = cv2.cvtColor(cv2.merge((lightness, a_channel, b_channel)),
                        cv2.COLOR_LAB2BGR)

    # Mild unsharp mask to recover edge detail lost to print screening.
    blurred = cv2.GaussianBlur(face, (0, 0), 3)
    return cv2.addWeighted(face, 1.5, blurred, -0.5, 0)


def _crop_document_face(document_img: np.ndarray) -> tuple[np.ndarray, str]:
    """
    Isolate the portrait from a full document scan.

    Returns (image, note). Falls back to the full image if no face is found,
    so a detector miss degrades rather than hard-fails.
    """
    for backend in (DETECTOR_BACKEND, FALLBACK_DETECTOR_BACKEND):
        try:
            faces = DeepFace.extract_faces(
                img_path=document_img,
                detector_backend=backend,
                enforce_detection=True,
                align=True,
            )
        except Exception:
            continue

        if not faces:
            continue

        # The portrait is the largest face on the card.
        best = max(faces, key=lambda f: f["facial_area"]["w"] * f["facial_area"]["h"])
        area = best["facial_area"]
        x, y, w, h = area["x"], area["y"], area["w"], area["h"]

        pad_x = int(w * FACE_CROP_PADDING)
        pad_y = int(h * FACE_CROP_PADDING)
        img_h, img_w = document_img.shape[:2]

        x0 = max(0, x - pad_x)
        y0 = max(0, y - pad_y)
        x1 = min(img_w, x + w + pad_x)
        y1 = min(img_h, y + h + pad_y)

        crop = document_img[y0:y1, x0:x1]
        if crop.size == 0:
            continue

        return _enhance_for_embedding(crop), f"document face cropped ({backend})"

    return _enhance_for_embedding(document_img), "document face not isolated; used full image"


# ----------------------------------------------------------------------
# LIVE FRAME QUALITY SELECTION
# ----------------------------------------------------------------------

def _sharpness(frame: np.ndarray) -> float:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _rank_live_frames(frames: list[np.ndarray]) -> list[np.ndarray]:
    """
    Pick the most usable frames from the burst.

    Reuses the same mediapipe landmarks liveness.py already computes:
    a good matching frame is sharp, frontal (nose centred between the face
    edges) and eyes-open (high eye-aspect-ratio, i.e. not mid-blink).
    """
    try:
        from .liveness import (
            LEFT_EYE, RIGHT_EYE, _eye_aspect_ratio, _normalized_nose_x,
        )
        import mediapipe as mp
    except Exception:
        # Landmarks unavailable - fall back to sharpness alone.
        ranked = sorted(frames, key=_sharpness, reverse=True)
        return ranked[:MAX_LIVE_FRAMES]

    mp_face_mesh = mp.solutions.face_mesh
    scored: list[tuple[float, int, np.ndarray]] = []

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:
        sharp_values = [_sharpness(f) for f in frames]
        max_sharp = max(sharp_values) or 1.0

        for index, frame in enumerate(frames):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb)
            if not result.multi_face_landmarks:
                continue

            landmarks = result.multi_face_landmarks[0].landmark
            h, w = frame.shape[:2]

            ear = (
                _eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
                + _eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
            ) / 2.0

            # 1.0 when perfectly frontal, falling off as the head turns.
            frontality = 1.0 - min(1.0, abs(_normalized_nose_x(landmarks) - 0.5) * 4)
            eyes_open = min(1.0, ear / 0.25)
            sharpness = sharp_values[index] / max_sharp

            score = (0.45 * frontality) + (0.35 * eyes_open) + (0.20 * sharpness)
            scored.append((score, index, frame))

    if not scored:
        return sorted(frames, key=_sharpness, reverse=True)[:MAX_LIVE_FRAMES]

    scored.sort(key=lambda item: item[0], reverse=True)
    return [frame for _, _, frame in scored[:MAX_LIVE_FRAMES]]


# ----------------------------------------------------------------------
# EMBEDDINGS
# ----------------------------------------------------------------------

def _embed(image: np.ndarray, model_name: str, already_cropped: bool) -> np.ndarray | None:
    """
    Return a single L2-normalized embedding.
    Converts OpenCV BGR -> RGB before DeepFace.
    """

    # IMPORTANT: OpenCV loads images in BGR, DeepFace expects RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    backends = (
        ["skip"]
        if already_cropped
        else [DETECTOR_BACKEND, FALLBACK_DETECTOR_BACKEND]
    )

    for backend in backends:
        try:
            representations = DeepFace.represent(
                img_path=image,
                model_name=model_name,
                detector_backend=backend,
                enforce_detection=False,
                align=True,
            )
        except Exception:
            continue

        if not representations:
            continue

        vector = np.asarray(representations[0]["embedding"], dtype=np.float64)
        norm = np.linalg.norm(vector)
        if norm == 0:
            continue

        return vector / norm

    return None


def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(1.0 - np.dot(a, b))


# ----------------------------------------------------------------------
# PUBLIC API
# ----------------------------------------------------------------------

def verify_faces(
    document_face_img: np.ndarray,
    live_frames: np.ndarray | list[np.ndarray],
) -> FaceMatchResult:
    """
    document_face_img : BGR image of the document (full scan is fine - we crop).
    live_frames       : list of BGR frames from the capture burst.
                        A single ndarray is accepted for backward compatibility.
    """
    if isinstance(live_frames, np.ndarray):
        live_frames = [live_frames]

    frames_total = len(live_frames)
    if frames_total == 0:
        return FaceMatchResult(
            matched=False, similarity=0.0, distance=1.0, threshold=1.0,
            reason="No live frames supplied.",
            frames_used=0, frames_total=0,
        )

    document_face, crop_note = _crop_document_face(document_face_img)
    selected = _rank_live_frames(live_frames)

    per_model_best: dict[str, float] = {}
    frames_matched = 0

    for model_name, base_threshold in MODELS.items():
        document_vector = _embed(document_face, model_name, already_cropped=True)
        if document_vector is None:
            continue

        threshold = base_threshold * DOC_VS_LIVE_TOLERANCE
        ratios: list[float] = []

        for frame in selected:
            live_vector = _embed(frame, model_name, already_cropped=False)
            if live_vector is None:
                continue
            # Normalize by this model's threshold so models are comparable:
            # < 1.0 means "this model says match".
            ratios.append(_cosine_distance(document_vector, live_vector) / threshold)

        if ratios:
            per_model_best[model_name] = float(min(ratios))
            frames_matched = max(frames_matched, len(ratios))

    if not per_model_best:
        return FaceMatchResult(
            matched=False, similarity=0.0, distance=1.0, threshold=1.0,
            reason=(
                "Could not extract a face embedding from the document photo "
                f"or any live frame ({crop_note}). Ask for a clearer document "
                "scan and better lighting."
            ),
            frames_used=0, frames_total=frames_total,
        )

    # Consensus across models. Best-frame (min) per model, then averaged -
    # one bad model or one bad frame can no longer sink a genuine match.
    aggregated = float(np.mean(list(per_model_best.values())))

    # Three-state outcome. A binary match/no-match cannot express the most
    # common real-world case: a genuine person whose ID photo is too old or
    # too degraded to confirm. Forcing those to PASS means accepting
    # impostors; forcing them to FAIL means rejecting genuine applicants.
    # Both are wrong, so we surface them for human review instead.
    if aggregated < 1.0:
        status = "MATCH"
    elif aggregated < INCONCLUSIVE_CEILING:
        status = "INCONCLUSIVE"
    else:
        status = "MISMATCH"

    matched = status == "MATCH"

    # 0.5 sits exactly on the decision boundary, so the number is readable:
    # above 0.5 = match, and how far above tells you the margin.
    similarity = float(np.clip(1.0 - (aggregated / 2.0), 0.0, 1.0))

    if status == "MATCH":
        reason = "Face embeddings match within threshold."
    elif status == "INCONCLUSIVE":
        reason = (
            "Inconclusive — embeddings fall in the uncertainty band. This is "
            "the expected result when the document photo is significantly "
            "older than the applicant (common on IDs issued in childhood), or "
            "when the scan is degraded. Not evidence of impersonation. "
            "Route to manual review."
        )
    else:
        reason = (
            "Face embeddings differ beyond acceptable threshold — possible "
            "mismatch or impersonation."
        )

    print(
    f"[FACE] status={status} | "
    f"distance={aggregated:.3f} | "
    f"similarity={similarity:.3f} | "
    f"models={per_model_best}"
    )

    return FaceMatchResult(
        matched=matched,
        status=status,
        similarity=similarity,
        distance=aggregated,
        threshold=1.0,
        reason=f"{reason} ({crop_note})",
        frames_used=frames_matched,
        frames_total=frames_total,
        per_model={name: round(value, 4) for name, value in per_model_best.items()},
    )


def verify_faces_from_bytes(
    document_bytes: bytes,
    live_frame_bytes: list[bytes],
) -> dict[str, Any]:
    """Convenience wrapper for the API layer: bytes in, plain dict out."""
    def decode(data: bytes) -> np.ndarray | None:
        buffer = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    document = decode(document_bytes)
    if document is None:
        return {"matched": False, "similarity": 0.0, "reason": "Document image could not be decoded."}

    frames = [f for f in (decode(b) for b in live_frame_bytes) if f is not None]
    result = verify_faces(document, frames)

    return {
        "matched": result.matched,
        "status": result.status,
        "similarity": round(result.similarity, 4),
        "distance": round(result.distance, 4),
        "threshold": result.threshold,
        "reason": result.reason,
        "frames_used": result.frames_used,
        "frames_total": result.frames_total,
        "per_model": result.per_model,
    }
