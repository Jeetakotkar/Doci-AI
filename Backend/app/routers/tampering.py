from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.tampering.detection import detect_tampering

router = APIRouter(
    prefix="/api/v1/tampering",
    tags=["Module 3 - Tampering Detection"],
)


@router.post("/detect")
async def check_tampering(
    # New API (optional)
    document_type: str | None = Form(None),
    document_image: UploadFile | None = File(None),

    # Old frontend fields (keep for compatibility)
    reference_image: UploadFile | None = File(None),
    test_image: UploadFile | None = File(None),

    threshold: float = Form(15.0),
    min_area: int = Form(40),
):
    # Use old frontend upload if new field isn't present
    uploaded = document_image if document_image else test_image

    if uploaded is None:
        raise HTTPException(status_code=400, detail="No document image provided.")

    image_bytes = await uploaded.read()

    # If frontend doesn't send document_type, assume Aadhaar for demo
    doc_type = (document_type or "AADHAAR").upper().strip()

    result = detect_tampering(
        document_type=doc_type,
        test_bytes=image_bytes,
        threshold=threshold,
        min_area=min_area,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Tampering detection failed."),
        )

    return result