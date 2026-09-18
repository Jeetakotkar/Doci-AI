import base64
from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

# Template document images (.jpeg)
SAMPLES = {
    "PASSPORT": "passport.jpeg",
    "VISA": "visa.jpeg",
    "AADHAAR": "aadhaar.jpeg",
    "DRIVING_LICENSE": "driving_license.jpeg",
}


def _decode_image(image_bytes: bytes):
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(array, cv2.IMREAD_COLOR)


def detect_tampering(
    document_type: str,
    test_bytes: bytes,
    threshold: float = 15.0,
    min_area: int = 40,
) -> dict:
    """
    Compare the uploaded document with its corresponding template image.
    The frontend uploads only one document image.
    """

    try:
        doc_type = document_type.upper()

        if doc_type not in SAMPLES:
            return {
                "success": False,
                "error": f"Unsupported document type: {document_type}",
            }

        # Load template
        sample_path = Path(__file__).parent / "samples" / SAMPLES[doc_type]

        if not sample_path.exists():
            return {
                "success": False,
                "error": f"Template not found: {sample_path.name}",
            }

        reference = cv2.imread(str(sample_path))
        test = _decode_image(test_bytes)

        if reference is None:
            return {
                "success": False,
                "error": "Could not load template image.",
            }

        if test is None:
            return {
                "success": False,
                "error": "Could not decode uploaded image.",
            }

        # Resize uploaded image to template size
        h, w = reference.shape[:2]
        test = cv2.resize(test, (w, h))

        # Convert to grayscale
        ref_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
        test_gray = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)

        # SSIM comparison
        score, diff = ssim(ref_gray, test_gray, full=True)

        tamper_score = (1.0 - score) * 100.0
        is_tampered = tamper_score >= threshold

        diff = (diff * 255).astype("uint8")

        _, thresh = cv2.threshold(
            diff,
            0,
            255,
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU,
        )

        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        annotated = test.copy()
        tampered_zones = 0

        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(
                annotated,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2,
            )
            tampered_zones += 1

        success, encoded = cv2.imencode(".jpeg", annotated)

        if not success:
            return {
                "success": False,
                "error": "Failed to encode annotated image.",
            }

        return {
            "success": True,
            "document_type": doc_type,
            "tamper_score": round(float(tamper_score), 2),
            "is_tampered": bool(is_tampered),
            "threshold": float(threshold),
            "tampered_zones": int(tampered_zones),
            "annotated_image_base64": base64.b64encode(
                encoded.tobytes()
            ).decode("utf-8"),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}