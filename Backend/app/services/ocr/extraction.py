import os
import re

import requests

# API key must be set as an environment variable, never hardcoded.
# export OCR_SPACE_API_KEY=your_key_here
API_KEY = os.environ.get("OCR_SPACE_API_KEY")

OCR_SPACE_URL = "https://api.ocr.space/parse/image"

# MRZ character set: A-Z, 0-9, 
MRZ_CHAR_RE = re.compile(r"^[A-Z0-9<]+$")


def _extract_mrz_lines(raw_text: str) -> list:
    candidates = []
    for line in raw_text.splitlines():
        cleaned = line.strip().replace(" ", "").upper()
        if len(cleaned) < 30:
            continue
        stripped = re.sub(r"[^A-Z0-9<]", "", cleaned)
        if len(stripped) >= 30 and MRZ_CHAR_RE.match(stripped):
            candidates.append(stripped)

    mrz_lines = []
    for line in candidates[-2:]:
        if len(line) < 44:
            line = line + ("<" * (44 - len(line)))
        else:
            line = line[:44]
        mrz_lines.append(line)

    return mrz_lines


def _parse_mrz(mrz_lines: list) -> dict:
    fields = {}

    if len(mrz_lines) < 2:
        return fields

    line1, line2 = mrz_lines[0], mrz_lines[1]

    if len(line1) >= 5:
        fields["nationality"] = line1[2:5].replace("<", "")

    name_field = line1[5:] if len(line1) > 5 else ""
    if "<<" in name_field:
        surname, given = name_field.split("<<", 1)
    else:
        surname, given = name_field, ""
    surname = surname.replace("<", " ").strip()
    given = given.replace("<", " ").strip()
    if surname or given:
        fields["name"] = (surname + ("<<" + given if given else "")).strip()

    if len(line2) >= 44:
        passport_number = line2[0:9].replace("<", "")
        dob_raw = line2[13:19]
        sex_raw = line2[20:21]
        expiry_raw = line2[21:27]

        fields["passport_number"] = passport_number
        fields["sex"] = sex_raw if sex_raw in ("M", "F", "X") else sex_raw
        fields["date_of_birth"] = _mrz_date_to_iso(dob_raw, is_dob=True)
        fields["expiry_date"] = _mrz_date_to_iso(expiry_raw, is_dob=False)

    return fields


def _mrz_date_to_iso(yymmdd: str, is_dob: bool) -> str:
    if len(yymmdd) != 6 or not yymmdd.isdigit():
        return ""

    yy, mm, dd = yymmdd[0:2], yymmdd[2:4], yymmdd[4:6]
    year = int(yy)

    if is_dob:
        century = 1900 if year > 30 else 2000
    else:
        century = 2000

    return f"{century + year:04d}-{mm}-{dd}"


def _guess_document_type(raw_text: str) -> str:
    upper = raw_text.upper()
    if "PASSPORT" in upper:
        return "PASSPORT"
    if "VISA" in upper:
        return "VISA"
    return "PASSPORT"


def extract_text(image_bytes: bytes) -> dict:
    if not API_KEY:
        return {"success": False, "error": "OCR_SPACE_API_KEY environment variable is not set."}

    if not image_bytes:
        return {"success": False, "error": "No image bytes provided."}

    try:
        payload = {"apikey": API_KEY, "language": "eng"}
        response = requests.post(
            OCR_SPACE_URL,
            files={"filename": ("image.jpg", image_bytes)},
            data=payload,
        )
        data = response.json()

        if data.get("IsErroredOnProcessing"):
            error_message = data.get("ErrorMessage", ["Unknown Error"])
            if isinstance(error_message, list):
                error_message = error_message[0] if error_message else "Unknown Error"
            return {"success": False, "error": error_message}

        raw_text = data.get("ParsedResults", [{}])[0].get("ParsedText", "").strip()

        if not raw_text:
            return {"success": False, "error": "No text found in image."}

        mrz_lines = _extract_mrz_lines(raw_text)
        parsed_fields = _parse_mrz(mrz_lines)

        result = {
            "success": True,
            "document_type": _guess_document_type(raw_text),
            "passport_number": parsed_fields.get("passport_number", ""),
            "name": parsed_fields.get("name", ""),
            "nationality": parsed_fields.get("nationality", ""),
            "date_of_birth": parsed_fields.get("date_of_birth", ""),
            "expiry_date": parsed_fields.get("expiry_date", ""),
            "sex": parsed_fields.get("sex", ""),
            "mrz": mrz_lines,
            "raw_text": raw_text,
        }
        return result

    except Exception as e:
        return {"success": False, "error": str(e)}