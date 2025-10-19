"""
Unit tests for TermValidator
Tests comprehensive term validation logic
"""
import pytest
from src.backend.services.term_validator import (
    TermValidator,
    ValidationConfig,
    create_strict_validator,
    create_lenient_validator,
    create_default_validator
)


class TestTermValidator:
    """Test suite for TermValidator class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = create_default_validator("en")
        self.strict_validator = create_strict_validator("en")
        self.lenient_validator = create_lenient_validator("en")

    # ===== Test Invalid Terms (Known Issues) =====

    def test_reject_pure_symbols(self):
        """Test rejection of pure symbol terms"""
        invalid_terms = ["[%]", "...", "!!!", "---", "***", "###"]

        for term in invalid_terms:
            assert not self.validator.is_valid_term(term), f"Should reject symbol: {term}"
            reason = self.validator.get_rejection_reason(term)
            assert "symbol" in reason.lower() or "punctuation" in reason.lower()

    def test_reject_pure_numbers(self):
        """Test rejection of pure number terms"""
        invalid_terms = ["4000", "123", "3.14159"]

        for term in invalid_terms:
            assert not self.validator.is_valid_term(term), f"Should reject number: {term}"
            reason = self.validator.get_rejection_reason(term)
            # May be rejected as number or as too short
            assert "number" in reason.lower() or "short" in reason.lower() or "symbol" in reason.lower()

    def test_reject_percentages(self):
        """Test rejection of percentage terms"""
        invalid_terms = ["70%", "50 %", "25.5%", "100 percent"]

        for term in invalid_terms:
            assert not self.validator.is_valid_term(term), f"Should reject percentage: {term}"
            reason = self.validator.get_rejection_reason(term)
            assert "percentage" in reason.lower()

    def test_reject_stop_words(self):
        """Test rejection of common stop words"""
        # Use only stop words that are at least 3 characters long
        invalid_terms = ["The", "and", "for", "with"]

        for term in invalid_terms:
            assert not self.validator.is_valid_term(term), f"Should reject stop word: {term}"
            reason = self.validator.get_rejection_reason(term)
            assert "stop word" in reason.lower()

    def test_reject_fragments(self):
        """Test rejection of word fragments"""
        invalid_terms = ["Mem-", "-ing", "three-", "-able"]

        for term in invalid_terms:
            assert not self.validator.is_valid_term(term), f"Should reject fragment: {term}"
            reason = self.validator.get_rejection_reason(term)
            assert "fragment" in reason.lower() or "hyphen" in reason.lower()

    def test_reject_too_short(self):
        """Test rejection of terms that are too short"""
        invalid_terms = ["ab", "x", "12"]

        for term in invalid_terms:
            assert not self.validator.is_valid_term(term), f"Should reject short term: {term}"
            reason = self.validator.get_rejection_reason(term)
            assert "short" in reason.lower() or "length" in reason.lower()

    # ===== Test Valid Terms =====

    def test_accept_valid_technical_terms(self):
        """Test acceptance of valid technical terms"""
        valid_terms = [
            "API",  # Acronym
            "HTTP",
            "Database",  # Single word
            "Machine Learning",  # Compound term
            "Natural Language Processing",  # Multi-word term
            "RESTful",
            "JavaScript",
            "PostgreSQL",
            "DevOps",
        ]

        for term in valid_terms:
            assert self.validator.is_valid_term(term), f"Should accept valid term: {term}"
            reason = self.validator.get_rejection_reason(term)
            assert reason == "", f"Valid term should have no rejection reason: {term}"

    def test_accept_hyphenated_terms(self):
        """Test acceptance of hyphenated compound terms"""
        valid_terms = [
            "Client-Server",
            "Multi-Threading",
            "Cross-Platform",
            "Real-Time",
        ]

        for term in valid_terms:
            assert self.validator.is_valid_term(term), f"Should accept hyphenated term: {term}"

    def test_accept_acronyms(self):
        """Test acceptance of acronyms"""
        valid_terms = ["API", "SQL", "HTTP", "REST", "CRUD", "JSON", "XML"]

        for term in valid_terms:
            assert self.validator.is_valid_term(term), f"Should accept acronym: {term}"

    # ===== Test Length Validation =====

    def test_length_validation(self):
        """Test minimum and maximum length validation"""
        # Default config: min=3, max=100
        assert not self.validator.is_valid_term("ab")  # Too short
        assert self.validator.is_valid_term("abc")  # Just right
        assert self.validator.is_valid_term("Sensor")  # Normal length
        # Test that extremely long terms are rejected (>100 chars)
        very_long_term = "X" * 150  # 150 characters
        assert not self.validator.is_valid_term(very_long_term)  # Too long

    # ===== Test Word Count Validation =====

    def test_word_count_validation(self):
        """Test word count limits for compound terms"""
        # Default config: max_word_count=4
        assert self.validator.is_valid_term("Database")  # 1 word
        assert self.validator.is_valid_term("Machine Learning")  # 2 words
        assert self.validator.is_valid_term("Natural Language Processing")  # 3 words
        assert self.validator.is_valid_term("Relational Database Management System")  # 4 words
        assert not self.validator.is_valid_term("This Is A Very Long Term Name")  # 6 words, too many

    # ===== Test Symbol Ratio Validation =====

    def test_symbol_ratio_validation(self):
        """Test symbol-to-character ratio limits"""
        # Valid: some symbols are OK
        assert self.validator.is_valid_term("Client-Server")  # Hyphen is valid

        # Invalid: too many symbols
        assert not self.validator.is_valid_term("A!!!B!!!C")  # Too many symbols
        assert not self.validator.is_valid_term("???what???")  # Too many symbols

    # ===== Test Capitalization Validation =====

    def test_capitalization_validation(self):
        """Test capitalization pattern validation"""
        # Valid patterns
        assert self.validator.is_valid_term("Database")  # Title case
        assert self.validator.is_valid_term("API")  # All uppercase (acronym)
        assert self.validator.is_valid_term("database")  # All lowercase
        assert self.validator.is_valid_term("Machine Learning")  # Title Case Words

        # Invalid patterns (random capitalization with 3+ case changes)
        assert not self.validator.is_valid_term("DaTaBaSe")  # Random caps (4 case changes)

    # ===== Test Batch Validation =====

    def test_batch_validate(self):
        """Test batch validation of multiple terms"""
        terms = [
            "API",  # Valid
            "Database",  # Valid
            "123",  # Invalid (number)
            "and",  # Invalid (stop word)
            "[%]",  # Invalid (symbols)
            "Machine Learning",  # Valid
            "70%",  # Invalid (percentage)
        ]

        result = self.validator.batch_validate(terms)

        assert result["total"] == 7
        assert result["valid_count"] == 3
        assert result["invalid_count"] == 4
        assert "API" in result["valid"]
        assert "Database" in result["valid"]
        assert "Machine Learning" in result["valid"]
        assert "123" in result["invalid"]
        assert "and" in result["invalid"]
        assert "[%]" in result["invalid"]
        assert "70%" in result["invalid"]

        # Check rejection reasons
        assert "123" in result["rejection_reasons"]
        assert "number" in result["rejection_reasons"]["123"].lower()

    # ===== Test Validation with Details =====

    def test_validate_with_details(self):
        """Test detailed validation results"""
        # Valid term
        result = self.validator.validate_with_details("Database")
        assert result["valid"] is True
        assert result["term"] == "Database"
        assert result["rejection_reason"] == ""
        assert all(result["details"].values())  # All checks should pass

        # Invalid term
        result = self.validator.validate_with_details("123")
        assert result["valid"] is False
        assert result["term"] == "123"
        assert result["rejection_reason"] != ""
        assert result["details"]["not_number"] is False  # This check should fail

    # ===== Test Configuration Variants =====

    def test_strict_validator(self):
        """Test strict validation configuration"""
        # Strict validator has higher minimum length (4)
        assert not self.strict_validator.is_valid_term("API")  # Too short for strict
        assert self.strict_validator.is_valid_term("REST")  # 4 chars, OK
        assert self.strict_validator.is_valid_term("Database")  # OK

    def test_lenient_validator(self):
        """Test lenient validation configuration"""
        # Lenient validator has lower minimum length (2)
        assert self.lenient_validator.is_valid_term("AI")  # OK for lenient
        assert self.lenient_validator.is_valid_term("IO")  # OK for lenient
        assert self.lenient_validator.is_valid_term("Database")  # OK

    # ===== Test Language-Specific Stop Words =====

    def test_english_stop_words(self):
        """Test English stop word filtering"""
        validator_en = create_default_validator("en")

        english_stop_words = ["the", "and", "of", "in", "to"]
        for word in english_stop_words:
            assert not validator_en.is_valid_term(word)

    def test_german_stop_words(self):
        """Test German stop word filtering"""
        validator_de = create_default_validator("de")

        german_stop_words = ["der", "die", "das", "und", "oder"]
        for word in german_stop_words:
            assert not validator_de.is_valid_term(word)

    # ===== Edge Cases =====

    def test_empty_term(self):
        """Test handling of empty terms"""
        assert not self.validator.is_valid_term("")
        assert not self.validator.is_valid_term("   ")
        assert not self.validator.is_valid_term("\t\n")

    def test_none_term(self):
        """Test handling of None input"""
        assert not self.validator.is_valid_term(None)

    def test_whitespace_handling(self):
        """Test proper whitespace handling"""
        # Leading/trailing whitespace should be handled
        assert self.validator.is_valid_term("  Database  ") is True
        assert self.validator.is_valid_term("\tAPI\n") is True

    def test_case_sensitivity(self):
        """Test case sensitivity in validation"""
        # Stop words should be case-insensitive
        assert not self.validator.is_valid_term("The")  # Capitalized stop word
        assert not self.validator.is_valid_term("THE")  # Uppercase stop word
        assert not self.validator.is_valid_term("the")  # Lowercase stop word

    # ===== Test Custom Configuration =====

    def test_custom_config(self):
        """Test validator with custom configuration"""
        config = ValidationConfig(
            min_term_length=5,
            max_term_length=20,
            reject_pure_numbers=False,  # Allow numbers
            language="en"
        )
        validator = TermValidator(config)

        # Should reject short terms
        assert not validator.is_valid_term("Test")  # 4 chars, too short

        # Should accept 5+ character terms
        assert validator.is_valid_term("Tests")  # 5 chars, OK

        # Should accept numbers (custom config)
        assert validator.is_valid_term("12345")  # Numbers allowed in this config

    # ===== Test Real-World Examples =====

    def test_real_world_technical_terms(self):
        """Test with real-world technical glossary terms"""
        valid_technical_terms = [
            "API Gateway",
            "Load Balancer",
            "Container Orchestration",
            "Microservices",
            "CI/CD Pipeline",
            "Version Control",
            "Authentication",
            "Authorization",
            "Encryption",
            "SSL Certificate",
            "Docker Container",
            "Kubernetes Cluster",
        ]

        for term in valid_technical_terms:
            result = self.validator.validate_with_details(term)
            assert result["valid"], f"Should accept technical term: {term}, Reason: {result['rejection_reason']}"

    def test_real_world_invalid_terms(self):
        """Test with real-world invalid terms that should be rejected"""
        invalid_terms = [
            "...",  # Ellipsis
            "---",  # Dashes
            "[sic]",  # Annotation
            "e.g.",  # Abbreviation with too many symbols
            "i.e.",  # Abbreviation with too many symbols
        ]

        for term in invalid_terms:
            result = self.validator.validate_with_details(term)
            assert not result["valid"], f"Should reject invalid term: {term}"


class TestValidationConfig:
    """Test suite for ValidationConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = ValidationConfig()

        assert config.min_term_length == 3
        assert config.max_term_length == 100
        assert config.min_word_count == 1
        assert config.max_word_count == 4
        assert config.max_symbol_ratio == 0.3
        assert config.reject_pure_numbers is True
        assert config.reject_percentages is True
        assert config.language == "en"

    def test_custom_config(self):
        """Test custom configuration values"""
        config = ValidationConfig(
            min_term_length=5,
            max_term_length=50,
            language="de"
        )

        assert config.min_term_length == 5
        assert config.max_term_length == 50
        assert config.language == "de"

    def test_stop_words_loaded(self):
        """Test that stop words are loaded for different languages"""
        config_en = ValidationConfig(language="en")
        config_de = ValidationConfig(language="de")

        assert len(config_en.stop_words) > 0
        assert len(config_de.stop_words) > 0
        assert "the" in config_en.stop_words
        assert "der" in config_de.stop_words


class TestWeek2ValidationAdditions:
    """Test Week 2 prevention-first validation additions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = create_default_validator("en")

    # ===== Test PDF Artifact Rejection =====

    def test_reject_pdf_encoding_artifacts(self):
        """Test rejection of PDF font encoding artifacts (cid:XX)"""
        assert not self.validator.is_valid_term("cid:31")
        assert not self.validator.is_valid_term("cid:128")
        assert not self.validator.is_valid_term("Sensor cid:45")
        assert self.validator.get_rejection_reason("cid:31") == "PDF encoding artifact (cid:XX)"

    def test_reject_pdf_internal_references(self):
        """Test rejection of PDF internal object references"""
        assert not self.validator.is_valid_term("obj")
        assert not self.validator.is_valid_term("endobj")
        assert not self.validator.is_valid_term("stream")
        assert not self.validator.is_valid_term("endstream")
        assert self.validator.get_rejection_reason("obj") == "PDF internal reference"

    # ===== Test Citation Rejection =====

    def test_reject_et_al_citations(self):
        """Test rejection of 'et al' citations"""
        assert not self.validator.is_valid_term("et al")
        assert not self.validator.is_valid_term("et al.")
        assert not self.validator.is_valid_term("Et Al")
        assert not self.validator.is_valid_term("L\u00f6ffelholz Et Al.")
        assert self.validator.get_rejection_reason("et al") == "Bibliographic citation (et al/ibid/page ref)"

    def test_reject_ibid_citations(self):
        """Test rejection of 'ibid' citations"""
        assert not self.validator.is_valid_term("ibid")
        assert not self.validator.is_valid_term("ibid.")
        assert not self.validator.is_valid_term("Ibid")
        assert self.validator.get_rejection_reason("ibid") == "Bibliographic citation (et al/ibid/page ref)"

    def test_reject_page_references(self):
        """Test rejection of page number references"""
        # These patterns are common in extracted PDF text
        assert not self.validator.is_valid_term("p. 5")
        assert not self.validator.is_valid_term("pp. 10-15")
        # Note: "page 42" might be accepted as it has valid word + number pattern
        # The key patterns caught are "p." and "pp." abbreviations

    def test_reject_year_only(self):
        """Test rejection of standalone years"""
        assert not self.validator.is_valid_term("2023")
        assert not self.validator.is_valid_term("2020")
        # But accept years as part of terms
        assert self.validator.is_valid_term("COVID-19")  # Year in context is OK

    # ===== Test Broken Hyphen Rejection =====

    def test_reject_leading_hyphen_fragments(self):
        """Test rejection of word fragments starting with hyphen"""
        assert not self.validator.is_valid_term("-tion")
        assert not self.validator.is_valid_term("-ing")
        assert not self.validator.is_valid_term("-ment")
        assert self.validator.get_rejection_reason("-tion") == "Term starts with hyphen (likely a fragment)"

    def test_reject_trailing_hyphen_fragments(self):
        """Test rejection of word fragments ending with hyphen"""
        assert not self.validator.is_valid_term("comple-")
        assert not self.validator.is_valid_term("temper-")
        assert not self.validator.is_valid_term("proces-")
        assert self.validator.get_rejection_reason("comple-") == "Term ends with hyphen (likely a fragment)"

    def test_accept_valid_hyphenated_terms(self):
        """Test that valid hyphenated terms are accepted"""
        # Valid compound terms with hyphens (not starting or ending with hyphen)
        assert self.validator.is_valid_term("Client-Server")
        assert self.validator.is_valid_term("Multi-Threading")
        assert self.validator.is_valid_term("Real-Time")
        # Note: Some validators may have additional rules for hyphenated terms

    # ===== Test OCR Corruption Rejection =====

    def test_reject_excessive_duplicate_characters(self):
        """Test rejection of terms with 4+ consecutive duplicate characters"""
        assert not self.validator.is_valid_term("Ppppllll")
        assert not self.validator.is_valid_term("aaaa")
        assert not self.validator.is_valid_term("XXXX")
        assert self.validator.get_rejection_reason("Ppppllll") == "OCR corruption (excessive duplicate characters)"

    def test_reject_alternating_duplicates(self):
        """Test rejection of alternating duplicate patterns from OCR"""
        assert not self.validator.is_valid_term("Pplloottttiinngg Tthhee")
        assert not self.validator.is_valid_term("Bbiioorreeaaccttoorr")
        assert not self.validator.is_valid_term("Ffiigguurree")
        assert self.validator.get_rejection_reason("Tthhee") == "OCR corruption (alternating duplicates)"

    def test_accept_natural_duplicates(self):
        """Test that natural English duplicate letters are accepted"""
        # These are valid English words with duplicate letters
        assert self.validator.is_valid_term("balloon")  # 'll', 'oo'
        assert self.validator.is_valid_term("mill")  # 'll'
        assert self.validator.is_valid_term("success")  # 'cc', 'ss'
        # Only 2 consecutive duplicates are normal, not 4+

    # ===== Integration Tests for Week 2 Fixes =====

    def test_real_world_bad_terms_from_week2_analysis(self):
        """Test rejection of actual bad terms found in database before Week 2 fixes"""
        # These are real examples from the cleanup script analysis
        bad_terms = [
            "Et Al",  # Citation
            "Tthhee",  # OCR corruption
            "Cid:31",  # PDF artifact
            "Cid:30",  # PDF artifact
            "L\u00f6ffelholz Et Al.",  # Citation
            "Ffiigguurree",  # OCR corruption
            "Aanndd",  # OCR corruption
            "Liepe Et Al",  # Citation
            "Vvaalluuee",  # OCR corruption
            "Uussee",  # OCR corruption
            "Ttaabbllee",  # OCR corruption
            "Tthhee Rree",  # OCR corruption
            "Bbiioorreeaaccttoorr",  # OCR corruption
            "Kkaa Vvaalluuee",  # OCR corruption
            "Tthhee Kkaa",  # OCR corruption
            "Pplloottttiinngg Tthhee",  # OCR corruption
            "Ddeetteerrmmiinniinngg Tthhee",  # OCR corruption
            "Bbaasseedd Oonn",  # OCR corruption
            "J. Et Al",  # Citation
        ]

        for term in bad_terms:
            assert not self.validator.is_valid_term(term), \
                f"Week 2 validation should reject: {term}"
            reason = self.validator.get_rejection_reason(term)
            assert reason != "", f"Should have rejection reason for: {term}"

    def test_week2_impact_metrics(self):
        """Document Week 2 validation impact on data quality"""
        # Week 2 cleanup removed 102 bad entries (3.1%)
        # Breakdown:
        # - 63 OCR corruption (alternating duplicates)
        # - 20 Bibliographic citations
        # - 11 OCR corruption (excessive duplicates)
        # - 4 Acronyms too long
        # - 2 PDF encoding artifacts
        # - 2 PDF internal references

        # Test samples from each category
        ocr_samples = ["Tthhee", "Ffiigguurree", "Bbiioorreeaaccttoorr"]
        for term in ocr_samples:
            assert not self.validator.is_valid_term(term)

        citation_samples = ["et al", "ibid", "Et Al"]
        for term in citation_samples:
            assert not self.validator.is_valid_term(term)

        pdf_artifact_samples = ["cid:31", "obj", "endobj"]
        for term in pdf_artifact_samples:
            assert not self.validator.is_valid_term(term)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
