from __future__ import annotations

import io
import os
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def configure_tesseract(
    tesseract_bin: Path | None = None,
    tessdata_dir: Path | None = None,
) -> None:
    bin_path = Path(tesseract_bin or ROOT / "bin" / "tesseract")
    data_path = Path(tessdata_dir or ROOT / "tessdata")
    if bin_path.exists():
        pytesseract.pytesseract.tesseract_cmd = str(bin_path)
    if data_path.exists():
        os.environ["TESSDATA_PREFIX"] = str(data_path)


def ocr_page(page: fitz.Page, dpi_scale: float = 2.0) -> str:
    configure_tesseract()
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi_scale, dpi_scale))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang="eng")


def extract_pages_text(
    pdf_path: str | Path,
    page_numbers: list[int] | None = None,
    dpi_scale: float = 2.0,
    min_native_chars: int = 80,
) -> str:
    """Extract text from 1-indexed page numbers; OCR when native text is thin."""
    path = Path(pdf_path)
    doc = fitz.open(path)
    pages = page_numbers or list(range(1, doc.page_count + 1))
    chunks: list[str] = []
    for num in pages:
        if num < 1 or num > doc.page_count:
            continue
        page = doc.load_page(num - 1)
        native = (page.get_text("text") or "").strip()
        if len(native) >= min_native_chars:
            text = native
            method = "native"
        else:
            text = ocr_page(page, dpi_scale=dpi_scale)
            method = "ocr"
        chunks.append(f"\n===== PAGE {num} ({method}) =====\n{text}")
    doc.close()
    return "\n".join(chunks)
