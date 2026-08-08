import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger("document_reader")
logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """Extracts text and tables from PDF using pdfplumber & PyMuPDF (fitz).
    If no text is found (scanned PDF), performs local OCR.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    full_text = []
    tables_found = []

    # 1. Primary Engine: pdfplumber for high-precision text & tables
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    full_text.append(f"--- Page {i+1} ---\n{page_text}")
                
                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    for tbl in page_tables:
                        clean_tbl = [[str(cell or '').strip() for cell in row] for row in tbl]
                        tables_found.append(clean_tbl)
    except Exception as e:
        logger.warning(f"pdfplumber extraction warning for {pdf_path}: {e}")

    # 2. Secondary Engine: PyMuPDF (fitz) fallback if pdfplumber extracted nothing
    if not "".join(full_text).strip():
        try:
            import fitz
            doc = fitz.open(pdf_path)
            for i, page in enumerate(doc):
                text = page.get_text() or ""
                if text.strip():
                    full_text.append(f"--- Page {i+1} ---\n{text}")
        except Exception as e:
            logger.warning(f"PyMuPDF extraction warning for {pdf_path}: {e}")

    # 3. Local OCR Engine: if still no text found (scanned PDF), use Tesseract OCR
    if not "".join(full_text).strip():
        logger.info(f"No native text found in {pdf_path}. Running local OCR engine...")
        try:
            import pytesseract
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path)
            for i, img in enumerate(images):
                ocr_text = pytesseract.image_to_string(img)
                if ocr_text.strip():
                    full_text.append(f"--- Page {i+1} (OCR) ---\n{ocr_text}")
        except Exception as e:
            logger.error(f"Local OCR fallback error for {pdf_path}: {e}")

    combined_text = "\n\n".join(full_text).strip()
    return {
        "file_path": pdf_path,
        "file_name": os.path.basename(pdf_path),
        "file_type": "pdf",
        "extracted_text": combined_text,
        "tables": tables_found,
        "page_count": len(full_text)
    }


def extract_text_from_image(image_path: str) -> Dict[str, Any]:
    """Extracts text from an image (JPG/PNG/BMP) using 100% local pytesseract OCR and OpenCV preprocessing."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    extracted_text = ""
    engine_used = "local_tesseract_ocr"

    try:
        from PIL import Image
        import pytesseract
        
        # Load image
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img).strip()

        # If sparse, try basic contrast preprocessing with OpenCV
        if not extracted_text:
            try:
                import cv2
                import numpy as np
                cv_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if cv_img is not None:
                    # Thresholding to enhance contrast
                    _, thresh = cv2.threshold(cv_img, 150, 255, cv2.THRESH_BINARY)
                    extracted_text = pytesseract.image_to_string(thresh).strip()
            except Exception as cv_err:
                logger.warning(f"OpenCV preprocessing error for {image_path}: {cv_err}")

    except Exception as e:
        logger.error(f"Local OCR error for {image_path}: {e}")

    return {
        "file_path": image_path,
        "file_name": os.path.basename(image_path),
        "file_type": "image",
        "extracted_text": extracted_text,
        "engine_used": engine_used
    }


def read_document(file_path: str) -> Dict[str, Any]:
    """Universal 100% local document reader for PDFs, Images, and Text files."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
        return extract_text_from_image(file_path)
    elif ext in [".txt", ".csv", ".tsv", ".json", ".log"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": "text",
            "extracted_text": text
        }
    else:
        raise ValueError(f"Unsupported document file extension: {ext}")
