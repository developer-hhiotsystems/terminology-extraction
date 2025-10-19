"""
Input Validation Utilities

Provides validation functions for common input types:
- Email addresses
- URLs
- UUIDs
- Dates
- SQL query safety
- File paths

Usage:
    from security.validators import validate_email, is_safe_sql

    if not validate_email(email):
        raise ValueError("Invalid email")
"""

import re
import uuid
from datetime import datetime
from typing import Optional, List
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid email format
    """
    if not email or not isinstance(email, str):
        return False

    # RFC 5322 simplified pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False

    # Additional checks
    if len(email) > 254:  # RFC 5321
        return False

    local, domain = email.rsplit('@', 1)
    if len(local) > 64:  # RFC 5321
        return False

    return True


def validate_url(url: str, allowed_schemes: List[str] = None) -> bool:
    """
    Validate URL format and scheme

    Args:
        url: URL to validate
        allowed_schemes: List of allowed schemes (default: ['http', 'https'])

    Returns:
        bool: True if valid URL
    """
    if not url or not isinstance(url, str):
        return False

    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']

    try:
        result = urlparse(url)

        # Check scheme
        if result.scheme not in allowed_schemes:
            return False

        # Check netloc (domain)
        if not result.netloc:
            return False

        # Check for localhost/private IPs in production
        private_patterns = [
            r'localhost',
            r'127\.\d+\.\d+\.\d+',
            r'192\.168\.\d+\.\d+',
            r'10\.\d+\.\d+\.\d+',
            r'172\.(1[6-9]|2\d|3[01])\.\d+\.\d+'
        ]

        for pattern in private_patterns:
            if re.search(pattern, result.netloc, re.IGNORECASE):
                # Allow in development, reject in production
                # (caller should check environment)
                pass

        return True

    except Exception:
        return False


def validate_uuid(value: str) -> bool:
    """
    Validate UUID format

    Args:
        value: UUID string to validate

    Returns:
        bool: True if valid UUID
    """
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def validate_date(date_string: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format

    Args:
        date_string: Date string to validate
        format: Expected date format (default: YYYY-MM-DD)

    Returns:
        bool: True if valid date
    """
    try:
        datetime.strptime(date_string, format)
        return True
    except (ValueError, TypeError):
        return False


def is_safe_sql(value: str) -> bool:
    """
    Check if string is safe for SQL queries

    Note: This is a helper check. ALWAYS use parameterized queries!

    Args:
        value: String to check

    Returns:
        bool: True if appears safe
    """
    if not isinstance(value, str):
        return True  # Non-strings are safe

    # Dangerous SQL keywords
    dangerous_patterns = [
        r'\b(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|EXEC|EXECUTE)\b',
        r'(--|#|\/\*|\*\/)',
        r';',
        r'\bOR\b.*=.*\bOR\b',
        r'\bAND\b.*=.*\bAND\b',
        r"('|\")\s*(OR|AND)\s*\1\s*=\s*\1",
        r'\bUNION\b.*\bSELECT\b'
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return False

    return True


def validate_filename(filename: str) -> bool:
    """
    Validate filename for safety

    Args:
        filename: Filename to validate

    Returns:
        bool: True if safe filename
    """
    if not filename or not isinstance(filename, str):
        return False

    # Check for path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # Check for dangerous extensions
    dangerous_extensions = [
        '.exe', '.bat', '.cmd', '.sh', '.ps1', '.vbs',
        '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg'
    ]

    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    if f'.{ext}' in dangerous_extensions:
        return False

    # Check for hidden files (Unix)
    if filename.startswith('.'):
        return False

    # Check length
    if len(filename) > 255:
        return False

    return True


def validate_file_path(path: str, base_dir: str) -> bool:
    """
    Validate file path is within base directory

    Prevents path traversal attacks.

    Args:
        path: File path to validate
        base_dir: Base directory path

    Returns:
        bool: True if path is safe
    """
    from pathlib import Path

    try:
        # Resolve to absolute paths
        file_path = Path(path).resolve()
        base_path = Path(base_dir).resolve()

        # Check if file_path is within base_path
        return str(file_path).startswith(str(base_path))

    except Exception:
        return False


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML by escaping dangerous characters

    Args:
        text: Text to sanitize

    Returns:
        str: Sanitized text
    """
    if not text or not isinstance(text, str):
        return text

    # HTML entity replacements
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }

    for char, entity in replacements.items():
        text = text.replace(char, entity)

    return text


def validate_integer_range(
    value: int,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> bool:
    """
    Validate integer is within range

    Args:
        value: Integer to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        bool: True if within range
    """
    if not isinstance(value, int):
        return False

    if min_value is not None and value < min_value:
        return False

    if max_value is not None and value > max_value:
        return False

    return True


def validate_string_length(
    value: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> bool:
    """
    Validate string length

    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length

    Returns:
        bool: True if length is valid
    """
    if not isinstance(value, str):
        return False

    length = len(value)

    if min_length is not None and length < min_length:
        return False

    if max_length is not None and length > max_length:
        return False

    return True


def validate_alphanumeric(value: str, allow_spaces: bool = False) -> bool:
    """
    Validate string is alphanumeric

    Args:
        value: String to validate
        allow_spaces: Whether to allow spaces

    Returns:
        bool: True if alphanumeric
    """
    if not isinstance(value, str):
        return False

    if allow_spaces:
        pattern = r'^[a-zA-Z0-9\s]+$'
    else:
        pattern = r'^[a-zA-Z0-9]+$'

    return bool(re.match(pattern, value))
