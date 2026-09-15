from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.face_verification_schemas import (
    Module4Response, Verdict, LivenessResponse, FaceMatchResponse, ChallengeTypeSchema
)
from app.services.face_verification.liveness import analyze_liveness, ChallengeType
from app.services.face_verification.face_match import verify_faces
from app.utils.image_utils import bytes_to_cv2_image

router = APIRouter(prefix="/api/v1/face-verification", tags=["Module 4 - Face Verification"])


@router.post("/verify", response_model=Module4Response)
async def verify_identity(
    document_face: UploadFile = File(..., description="Face photo cropped from the ID document"),
    live_frames: list[UploadFile] = File(..., description="Sequence of webcam frames captured during the liveness challenge (10-15 frames recommended)"),
    challenge: ChallengeTypeSchema = Form(..., description="Which challenge the frontend asked the user to perform"),
):
    """
    Main Module 4 endpoint.

    Frontend flow:
    1. Get document_face image (either cropped by Module 1's OCR/face-detect step,
       or send the full doc image — DeepFace will find the face itself).
    2. Randomly pick a challenge (blink or head_turn), tell the user what to do.
    3. Capture ~10-15 webcam frames over ~1.5-2 seconds while user performs it.
    4. POST everything here as multipart/form-data.

    Order of operations matters: we check liveness FIRST. If liveness fails,
    we don't even bother running face match — a spoofed liveness attempt is
    already grounds for rejection regardless of whether the photo looks similar.
    """
    # --- Load document face image ---
    try:
        doc_bytes = await document_face.read()
        doc_img = bytes_to_cv2_image(doc_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid document face image: {e}")

    # --- Load live frames ---
    if len(live_frames) < 5:
        raise HTTPException(status_code=400, detail="At least 5 live frames are required for liveness analysis.")

    frame_imgs = []
    for f in live_frames:
        try:
            frame_bytes = await f.read()
            frame_imgs.append(bytes_to_cv2_image(frame_bytes))
        except ValueError:
            continue  # skip unreadable frames, don't fail the whole request

    if len(frame_imgs) < 5:
        raise HTTPException(status_code=400, detail="Fewer than 5 live frames could be decoded successfully.")

    # --- Step 1: Liveness check ---
    liveness_result = analyze_liveness(frame_imgs, ChallengeType(challenge.value))
    liveness_response = LivenessResponse(
        passed=liveness_result.passed,
        challenge=liveness_result.challenge,
        confidence=liveness_result.confidence,
        reason=liveness_result.reason,
        frames_with_face=liveness_result.frames_with_face,
        frames_total=liveness_result.frames_total,
    )

    if not liveness_result.passed:
        return Module4Response(
            verdict=Verdict.LIVENESS_FAILED,
            risk_score=90.0,
            liveness=liveness_response,
            face_match=None,
            message="Liveness check failed — possible spoof attempt (photo/video replay).",
        )

    # --- Step 2: Face match (use the best frame — highest-confidence face detection) ---
    # Simple choice: middle frame of the sequence tends to be well-centered.
    # Good-enough for hackathon; a v2 could pick the sharpest / most frontal frame.
    live_face_img = frame_imgs[len(frame_imgs) // 2]

    match_result = verify_faces(doc_img, live_face_img)
    match_response = FaceMatchResponse(
        matched=match_result.matched,
        similarity=match_result.similarity,
        distance=match_result.distance,
        threshold=match_result.threshold,
        reason=match_result.reason,
    )

    if not match_result.matched:
        return Module4Response(
            verdict=Verdict.FACE_MISMATCH,
            risk_score=round(80.0 * (1 - match_result.similarity) + 20, 2),
            liveness=liveness_response,
            face_match=match_response,
            message="Liveness passed, but the live face does not match the document photo.",
        )

    # --- All checks passed ---
    risk_score = round(20.0 * (1 - match_result.similarity), 2)  # low risk, scaled by match confidence
    return Module4Response(
        verdict=Verdict.VERIFIED,
        risk_score=risk_score,
        liveness=liveness_response,
        face_match=match_response,
        message="Identity verified: liveness confirmed and face matches document.",
    )
