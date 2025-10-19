"""
Unit tests for PDF Extractor Service
Tests the prevention-first OCR normalization added in Week 2
"""
import pytest
from src.backend.services.pdf_extractor import PDFExtractor


class TestPDFExtractor:
    """Test PDF extraction and OCR normalization"""

    # ===== Test OCR Normalization (Week 2 Addition) =====

    def test_normalize_three_plus_consecutive_duplicates(self):
        """Test fixing 3+ consecutive duplicate characters (current implementation)"""
        # Current implementation: keep (count + 1) // 2 characters
        assert PDFExtractor._normalize_ocr_artifacts("aaa") == "aa"  # 3 → 2
        assert PDFExtractor._normalize_ocr_artifacts("llll") == "ll"  # 4 → 2
        assert PDFExtractor._normalize_ocr_artifacts("Plotttting") == "Plotting"  # "tttt" → "tt"
        assert PDFExtractor._normalize_ocr_artifacts("Processsssss") == "Processss"  # 8 s's → 4 s's (but already had 2)

    def test_normalize_alternating_duplicates_limitation(self):
        """Document that alternating duplicates are PARTIALLY fixed"""
        # Only sequences of 3+ consecutive duplicates are fixed
        # "Pplloottttiinngg" has "tttt" (4 t's) which gets fixed to "tt"
        assert PDFExtractor._normalize_ocr_artifacts("Pplloottttiinngg") == "Pplloottiinngg"  # tttt → tt, rest unchanged
        assert PDFExtractor._normalize_ocr_artifacts("Tthhee") == "Tthhee"  # All pairs, no 3+ consecutive
        assert PDFExtractor._normalize_ocr_artifacts("Aanndd") == "Aanndd"  # All pairs, no 3+ consecutive
        # TODO: Enhancement to detect alternating patterns where EACH char is doubled

    def test_normalize_pdf_encoding_artifacts(self):
        """Test removing PDF font encoding artifacts (cid:XX)"""
        assert PDFExtractor._normalize_ocr_artifacts("cid:31 Temperature").strip() == "Temperature"
        assert PDFExtractor._normalize_ocr_artifacts("Sensor cid:128").strip() == "Sensor"
        assert PDFExtractor._normalize_ocr_artifacts("cid:31").strip() == ""
        assert PDFExtractor._normalize_ocr_artifacts("Process cid:45 Flow") == "Process Flow"  # Double space normalized

    def test_normalize_excessive_whitespace(self):
        """Test fixing excessive whitespace"""
        assert PDFExtractor._normalize_ocr_artifacts("Process  Flow") == "Process Flow"
        assert PDFExtractor._normalize_ocr_artifacts("Sensor   Data") == "Sensor Data"
        assert PDFExtractor._normalize_ocr_artifacts("Multiple    Spaces     Here") == "Multiple Spaces Here"

    def test_normalize_spaced_out_characters(self):
        """Test fixing spaced-out character patterns"""
        # The implementation DOES handle "T e m p" patterns with capital followed by lowercase
        assert PDFExtractor._normalize_ocr_artifacts("T e m p e r a t u r e") == "Temperature"
        assert PDFExtractor._normalize_ocr_artifacts("S e n s o r") == "Sensor"
        # This regex: r'\b([A-Z](?:\s+[a-z])+)\b' matches capital letter followed by spaced lowercase

    def test_normalize_mixed_corruption(self):
        """Test fixing multiple types of corruption in same text"""
        # Multiple issues in one string
        # Note: Alternating duplicates won't be fixed, only 3+ consecutive and cid artifacts
        assert PDFExtractor._normalize_ocr_artifacts("cid:31 Plotttting") == "Plotting"  # cid removed, ttt → tt
        assert PDFExtractor._normalize_ocr_artifacts("Tablle  cid:45") == "Tablle"  # cid removed, spaces normalized

    def test_normalize_empty_and_none(self):
        """Test edge cases: empty string and None"""
        assert PDFExtractor._normalize_ocr_artifacts("") == ""
        assert PDFExtractor._normalize_ocr_artifacts(None) == None

    def test_normalize_clean_text_unchanged(self):
        """Test that clean text is not modified"""
        clean_texts = [
            "Sensor",
            "Temperature Control",
            "pH Measurement",
            "Dissolved Oxygen Monitoring",
            "Real-Time Process Analytics"
        ]

        for text in clean_texts:
            assert PDFExtractor._normalize_ocr_artifacts(text) == text

    def test_normalize_preserves_valid_repeated_chars(self):
        """Test that valid repeated characters are preserved"""
        # Some terms naturally have repeated characters
        valid_terms = [
            "balloon",  # 'll' and 'oo' are valid
            "millennium",  # 'll' and 'nn' are valid
            "mississippi",  # 'ss', 'ss', 'pp' are valid (only 2 consecutive)
        ]

        for term in valid_terms:
            # These should be preserved since they only have 2 consecutive, not 3+
            assert PDFExtractor._normalize_ocr_artifacts(term) == term

    def test_normalize_fixes_excessive_repeats_only(self):
        """Test that only 3+ consecutive duplicates are fixed"""
        # 2 consecutive = OK (natural English)
        assert PDFExtractor._normalize_ocr_artifacts("Balloon") == "Balloon"  # 'll', 'oo' = 2 each
        # 3+ consecutive = OCR error, fix it
        assert PDFExtractor._normalize_ocr_artifacts("Balllooon") == "Balloon"  # 'lll' → 'll', 'ooo' → 'oo'

    def test_normalize_case_insensitive(self):
        """Test that normalization works regardless of case"""
        assert PDFExtractor._normalize_ocr_artifacts("PLOTTTTING") == "PLOTTING"  # TTT → TT
        assert PDFExtractor._normalize_ocr_artifacts("processss") == "process"  # ssss → ss

    # ===== Integration Tests =====

    def test_normalize_real_world_ocr_output(self):
        """Test normalization on realistic OCR corruption patterns"""
        # Simulate real OCR output with PDF artifacts and excessive whitespace
        corrupted = "The processsss  flow  involves cid:31 several  stages."

        normalized = PDFExtractor._normalize_ocr_artifacts(corrupted)

        # Should remove 'cid:31', fix 4+ duplicates, and normalize whitespace
        assert "cid:31" not in normalized
        assert "processsss" not in normalized  # ssss → ss
        assert "  " not in normalized  # Double spaces removed
        assert "process" in normalized.lower()
