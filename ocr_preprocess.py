"""
Image preprocessing utilities for OCR optimization.

Key strategies:
1. Resize all images to PaddleOCR-VL optimal resolution (long side 1920px)
2. Apply CLAHE contrast enhancement for low-contrast images
3. For PDFs with failed extractions, re-render at 300 DPI and crop regions
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter

# PaddleOCR-VL benefits from higher-res input for small text.
# The model internally downscales to ~1M pixels as needed.
OCR_TARGET_LONG_SIDE = 1920
PDF_HIGH_DPI = 300


def preprocess_for_ocr(img: Image.Image) -> Image.Image:
    """Preprocess image for optimal PaddleOCR-VL input.

    1. Resize so long side = 1920px (model handles internal downscaling)
    2. For low-contrast images (e.g., gold on red): denoise + CLAHE
    """
    arr = np.array(img.convert("RGB"))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]

    # Resize: long side → 1920px
    long_side = max(h, w)
    scale = OCR_TARGET_LONG_SIDE / long_side
    if abs(scale - 1.0) > 0.05:
        new_w, new_h = int(w * scale), int(h * scale)
        interp = cv2.INTER_LANCZOS4 if scale > 1 else cv2.INTER_AREA
        bgr = cv2.resize(bgr, (new_w, new_h), interpolation=interp)

    # Detect low-contrast and enhance if needed
    r, g = bgr[:, :, 2].astype(float), bgr[:, :, 1].astype(float)
    red_dominant = (r > 120) & (r > g * 1.5)
    if red_dominant.mean() >= 0.15:
        denoised = cv2.fastNlMeansDenoisingColored(bgr, h=8, hColor=8)
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l_ch)
        bgr = cv2.cvtColor(cv2.merge([l_enhanced, a_ch, b_ch]), cv2.COLOR_LAB2BGR)

    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def preprocess_for_qwen(img: Image.Image) -> Image.Image:
    """Optimal preprocessing for Qwen3-VL: resize to ~1280px + contrast 1.5x.
    Capped at 1280px long side to fit within Qwen3's 4096 token context."""
    arr = np.array(img.convert("RGB"))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]
    # Resize to 1280px long side (up or down)
    target = 1280
    scale = target / max(h, w)
    if abs(scale - 1.0) > 0.05:
        interp = cv2.INTER_LANCZOS4 if scale > 1 else cv2.INTER_AREA
        bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=interp)
    # Contrast 1.5x on L channel
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.convertScaleAbs(l, alpha=1.5, beta=0)
    bgr = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def crop_and_preprocess(img: Image.Image, x1: float, y1: float,
                        x2: float, y2: float) -> Image.Image:
    """Crop a region (fractional coordinates 0-1) and preprocess for OCR."""
    w, h = img.size
    crop = img.crop((int(w * x1), int(h * y1), int(w * x2), int(h * y2)))
    return preprocess_for_ocr(crop)
