"""
PDF text extraction service using pdfplumber
Extracts text content from PDF documents for term extraction
"""
import pdfplumber
import re
from typing import Dict, List, Optional
from pathlib import Path
import logging

from src.backend.constants import (
    PATTERN_DUPLICATE_CHARS,
    PATTERN_PDF_ENCODING,
    PATTERN_SPACED_CHARS
)

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Service for extracting text from PDF documents"""

    @staticmethod
    def _normalize_ocr_artifacts(text: str) -> str:
        """
        Normalize common OCR artifacts from PDF extraction

        This method fixes common OCR errors that occur during PDF text extraction,
        preventing garbage data from being extracted as terms.

        Fixes:
        - Doubled characters: "Pplloottttiinngg" → "Plotting"
        - Spaced characters: "S e n s o r" → "Sensor"
        - PDF encoding artifacts: "cid:31" → (removed)
        - Excessive whitespace and formatting issues

        Args:
            text: Raw extracted text from PDF

        Returns:
            Normalized text with OCR artifacts fixed

        Examples:
            >>> PDFExtractor._normalize_ocr_artifacts("Pplloottttiinngg")
            "Plotting"
            >>> PDFExtractor._normalize_ocr_artifacts("cid:31 Temperature")
            "Temperature"
        """
        if not text:
            return text

        # Fix pattern: 3+ consecutive duplicate characters (OCR doubling error)
        # Example: "Pplloottttiinngg" → "Plotting"
        # Match sequences like "pp", "ll", "oo", "tt", etc.
        def fix_doubled_chars(match):
            char = match.group(1)
            count = len(match.group(0)) // len(char)
            # If we have 4 duplicates "llll", keep 2 "ll"
            # If we have 3 duplicates "lll", keep 2 "ll" (round up)
            keep_count = (count + 1) // 2
            return char * keep_count

        # Only fix lowercase letter duplicates (preserves intentional caps like "IEEE")
        text = re.sub(PATTERN_DUPLICATE_CHARS, fix_doubled_chars, text, flags=re.IGNORECASE)

        # Remove PDF encoding artifacts (cid:XX)
        # These are font encoding references that shouldn't be in extracted text
        text = re.sub(PATTERN_PDF_ENCODING, '', text)

        # Fix excessive whitespace (common OCR issue)
        # Multiple spaces → single space
        text = re.sub(r' {2,}', ' ', text)

        # Fix broken words with spaces between each letter (rare OCR error)
        # "T e m p e r a t u r e" → "Temperature"
        # Only apply if ALL letters in the word are separated
        text = re.sub(PATTERN_SPACED_CHARS,
                     lambda m: m.group(0).replace(' ', ''), text)

        return text.strip()

    @staticmethod
    def extract_text(pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with:
                - text: Extracted text content
                - pages: Number of pages
                - metadata: PDF metadata
                - success: Boolean indicating success
                - error: Error message if failed
        """
        result = {
            "text": "",
            "pages": 0,
            "metadata": {},
            "success": False,
            "error": None
        }

        try:
            path = Path(pdf_path)
            if not path.exists():
                result["error"] = f"File not found: {pdf_path}"
                return result

            if not path.suffix.lower() == '.pdf':
                result["error"] = f"Not a PDF file: {pdf_path}"
                return result

            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                result["metadata"] = pdf.metadata or {}
                result["pages"] = len(pdf.pages)

                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # ✅ NORMALIZE OCR ARTIFACTS BEFORE APPENDING
                            page_text = PDFExtractor._normalize_ocr_artifacts(page_text)
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {e}")
                        continue

                result["text"] = "\n\n".join(text_parts)
                result["success"] = True

                logger.info(f"Successfully extracted {len(result['text'])} characters from {result['pages']} pages")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"PDF extraction failed: {e}")

        return result

    @staticmethod
    def extract_text_by_page(pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF file with page-by-page breakdown

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with:
                - pages: List of dicts with page_num and text
                - total_pages: Total number of pages
                - metadata: PDF metadata
                - success: Boolean indicating success
                - error: Error message if failed
        """
        result = {
            "pages": [],
            "total_pages": 0,
            "metadata": {},
            "success": False,
            "error": None
        }

        try:
            path = Path(pdf_path)
            if not path.exists():
                result["error"] = f"File not found: {pdf_path}"
                return result

            with pdfplumber.open(pdf_path) as pdf:
                result["metadata"] = pdf.metadata or {}
                result["total_pages"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        # ✅ NORMALIZE OCR ARTIFACTS
                        if page_text:
                            page_text = PDFExtractor._normalize_ocr_artifacts(page_text)
                        result["pages"].append({
                            "page_num": page_num,
                            "text": page_text or ""
                        })
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {e}")
                        result["pages"].append({
                            "page_num": page_num,
                            "text": "",
                            "error": str(e)
                        })

                result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"PDF extraction failed: {e}")

        return result

    @staticmethod
    def validate_pdf(pdf_path: str) -> Dict[str, any]:
        """
        Validate PDF file without extracting text

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with validation results
        """
        result = {
            "valid": False,
            "pages": 0,
            "file_size": 0,
            "error": None
        }

        try:
            path = Path(pdf_path)

            if not path.exists():
                result["error"] = "File not found"
                return result

            if not path.suffix.lower() == '.pdf':
                result["error"] = "Not a PDF file"
                return result

            result["file_size"] = path.stat().st_size

            with pdfplumber.open(pdf_path) as pdf:
                result["pages"] = len(pdf.pages)
                result["valid"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"PDF validation failed: {e}")

        return result
