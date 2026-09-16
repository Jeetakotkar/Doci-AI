from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/pipeline", tags=["Full Pipeline"])


class FullScreeningResponse(BaseModel):
    overall_risk_score: float
    ocr_result: dict | None = None
    validation_result: dict | None = None
    tampering_result: dict | None = None
    face_verification_result: dict | None = None
    final_decision: str


@router.post("/screen-document", response_model=FullScreeningResponse)
async def screen_document(
    document_image: UploadFile = File(..., description="Full ID document image"),
    live_frames: list[UploadFile] = File(..., description="Webcam frames for liveness+face match"),
    challenge: str = Form(...),
):
   
    # TODO: call OCR service here
    ocr_result = {"status": "not_yet_implemented"}

    # TODO : call validation service here
    validation_result = {"status": "not_yet_implemented"}

    # TODO : call tampering detection service here
    tampering_result = {"status": "not_yet_implemented"}

    # Module 4 — already implemented, reuse the same logic as /face-verification/verify
    from app.services.face_verification.liveness import analyze_liveness, ChallengeType
    from app.services.face_verification.face_match import verify_faces
    from app.utils.image_utils import bytes_to_cv2_image

    doc_bytes = await document_image.read()
    doc_img = bytes_to_cv2_image(doc_bytes)

    frame_imgs = []
    for f in live_frames:
        frame_imgs.append(bytes_to_cv2_image(await f.read()))

    liveness_result = analyze_liveness(frame_imgs, ChallengeType(challenge))

    face_verification_result = {"liveness_passed": liveness_result.passed}
    face_risk = 90.0

    if liveness_result.passed:
        live_face_img = frame_imgs[len(frame_imgs) // 2]
        match_result = verify_faces(doc_img, live_face_img)
        face_verification_result["face_matched"] = match_result.matched
        face_verification_result["similarity"] = match_result.similarity
        face_risk = round(20.0 * (1 - match_result.similarity), 2) if match_result.matched else 75.0

    # TODO: once modules 1-3 are real, combine their risk contributions here
   
    overall_risk_score = face_risk

    final_decision = "REVIEW REQUIRED" if overall_risk_score > 50 else "LOW RISK"

    return FullScreeningResponse(
        overall_risk_score=overall_risk_score,
        ocr_result=ocr_result,
        validation_result=validation_result,
        tampering_result=tampering_result,
        face_verification_result=face_verification_result,
        final_decision=final_decision,
    )
