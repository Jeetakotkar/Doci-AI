import numpy as np
import cv2


def bytes_to_cv2_image(image_bytes: bytes) -> np.ndarray:
    """Decode uploaded image bytes into a BGR numpy array (OpenCV format)."""
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image — file may be corrupted or not a valid image.")
    return img
