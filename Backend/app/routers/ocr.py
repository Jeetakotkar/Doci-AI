from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.ocr.extraction import extract_text

router = APIRouter(prefix="/api/v1/ocr", tags=["Module 1 - OCR Extraction"])


@router.post("/extract")
async def extract_document_fields(
    document_image: UploadFile = File(..., description="Identity document image (passport, visa, ID, etc.)")
):
    """
    Extracts text from a document image via OCR.space, then parses the MRZ
    lines into the structured fields Module 2 expects: document_type,
    passport_number, name, nationality, date_of_birth, expiry_date, sex, mrz.
    """
    image_bytes = await document_image.read()

    result = extract_text(image_bytes)

    if not result.get("success"):
        raise HTTPException(status_code=422, detail=result.get("error", "OCR extraction failed."))

    return result