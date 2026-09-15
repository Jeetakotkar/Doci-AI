"""
Face verification: compares the face on the identity document against
a live-captured frame of the person.

Uses DeepFace (https://github.com/serengil/deepface) as the model runner.
We use ArcFace as the recognition model - good accuracy/speed tradeoff and
it's a name you can defend in a Q&A round ("why ArcFace?" -> state-of-the-art
margin-based loss for face embeddings, widely used in production KYC systems).

DeepFace handles:
- face detection + alignment internally (we use 'retinaface' or 'opencv' backend)
- embedding extraction
- distance calculation + threshold decision

We wrap it so the rest of the app doesn't depend on DeepFace's API shape directly -
useful if you swap models later (e.g. to face_recognition/dlib for a lighter demo laptop).
"""

from dataclasses import dataclass
import numpy as np

from deepface import DeepFace

MODEL_NAME = "ArcFace"
DETECTOR_BACKEND = "opencv"   # fast, no GPU needed - good for hackathon laptops.
                              # swap to "retinaface" for better accuracy if you have GPU/time.
DISTANCE_METRIC = "cosine"


@dataclass
class FaceMatchResult:
    matched: bool
    similarity: float        # 0-1, higher = more similar (we invert DeepFace's distance)
    distance: float          # raw distance from DeepFace
    threshold: float
    reason: str


def verify_faces(document_face_img: np.ndarray, live_face_img: np.ndarray) -> FaceMatchResult:
    """
    document_face_img, live_face_img: BGR images (numpy arrays, e.g. from cv2.imdecode)
    """
    try:
        result = DeepFace.verify(
            img1_path=document_face_img,
            img2_path=live_face_img,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            distance_metric=DISTANCE_METRIC,
            enforce_detection=True,
        )
    except ValueError as e:
        # DeepFace raises ValueError when it can't detect a face in one of the images
        return FaceMatchResult(
            matched=False, similarity=0.0, distance=1.0, threshold=0.0,
            reason=f"Face detection failed: {str(e)}",
        )

    distance = result["distance"]
    threshold = result["threshold"]
    matched = result["verified"]

    # cosine distance: 0 = identical, ~1+ = very different. Convert to a 0-1 similarity score.
    similarity = float(np.clip(1 - (distance / (threshold * 2)), 0, 1))

    reason = (
        "Face embeddings match within threshold."
        if matched else
        "Face embeddings differ beyond acceptable threshold — possible mismatch or impersonation."
    )

    return FaceMatchResult(
        matched=matched, similarity=similarity, distance=distance,
        threshold=threshold, reason=reason,
    )
