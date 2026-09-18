from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from app.services.validation.module2.pipeline import run_validation

router = APIRouter(prefix="/api/v1/validation", tags=["Module 2 - Document Validation"])


class ValidationRequest(BaseModel):
    """
    Matches the JSON shape Module 1 (OCR) is expected to produce.
    See app/services/validation/module2/README.md for the full field contract.
    """
    document_type: str
    passport_number: str | None = None
    name: str | None = None
    nationality: str | None = None
    date_of_birth: str | None = None
    expiry_date: str | None = None
    sex: str | None = None
    mrz: list[str] | None = None
    optional: dict[str, Any] | None = None
    # For VISA validation, a reference passport record can be supplied separately.
    passport_data: dict[str, Any] | None = None


@router.post("/check")
async def validate_document(payload: ValidationRequest):
    """
    Runs Module 2's rule-based validation (field checks, MRZ structure,
    MRZ check digits, cross-field consistency) on structured document data.

    Input: JSON fields as extracted by Module 1 (OCR) — NOT an image upload.
    Output: pass/fail/warning per rule, plus an overall_status
    (VALID / INVALID / REVIEW).
    """
    input_data = payload.model_dump(exclude={"passport_data"}, exclude_none=True)
    passport_data = payload.passport_data

    result = run_validation(input_data, passport_data)
    return result
