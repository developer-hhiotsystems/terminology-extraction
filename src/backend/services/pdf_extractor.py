"""
PDF text extraction service using pdfplumber
Extracts text content from PDF documents for term extraction
"""
import pdfplumber
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Service for extracting text from PDF documents"""

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
