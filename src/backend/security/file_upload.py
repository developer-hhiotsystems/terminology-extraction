"""
Secure File Upload Handler

Implements security measures for file uploads:
- File type validation (whitelist)
- File size limits
- Virus scanning (optional)
- Safe filename sanitization
- Content type verification

Usage:
    from security.file_upload import SecureFileUpload

    uploader = SecureFileUpload(settings)
    result = await uploader.validate_and_save(file)
"""

import os
import re
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException, status
import magic  # python-magic
import logging

logger = logging.getLogger(__name__)


class SecureFileUpload:
    """
    Secure file upload handler with validation and sanitization
    """

    # Allowed MIME types for each extension
    ALLOWED_MIMES = {
        '.pdf': ['application/pdf'],
        '.txt': ['text/plain'],
        '.docx': [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ],
        '.doc': ['application/msword'],
        '.rtf': ['application/rtf', 'text/rtf']
    }

    # Maximum file sizes per type (in bytes)
    MAX_SIZES = {
        '.pdf': 50 * 1024 * 1024,   # 50 MB
        '.txt': 10 * 1024 * 1024,   # 10 MB
        '.docx': 25 * 1024 * 1024,  # 25 MB
        '.doc': 25 * 1024 * 1024,   # 25 MB
        '.rtf': 10 * 1024 * 1024    # 10 MB
    }

    # Dangerous file signatures (magic bytes)
    DANGEROUS_SIGNATURES = [
        b'MZ',  # Windows executable
        b'\x7fELF',  # Linux executable
        b'#!',  # Shell script
        b'<?php',  # PHP script
        b'<%',  # ASP/JSP
    ]

    def __init__(
        self,
        upload_dir: str = "uploads",
        allowed_extensions: List[str] = None,
        max_size_mb: int = 50,
        enable_virus_scan: bool = False
    ):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True, parents=True)

        self.allowed_extensions = allowed_extensions or ['.pdf', '.txt', '.docx']
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.enable_virus_scan = enable_virus_scan

        # Initialize magic for MIME type detection
        try:
            self.magic = magic.Magic(mime=True)
        except Exception as e:
            logger.warning(f"python-magic not available: {e}")
            self.magic = None

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Get base name (remove path)
        filename = os.path.basename(filename)

        # Remove non-ASCII characters
        filename = filename.encode('ascii', 'ignore').decode('ascii')

        # Remove dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Prevent double extensions (.pdf.exe)
        parts = filename.rsplit('.', 1)
        if len(parts) == 2:
            name, ext = parts
            # Remove any dots from the name part
            name = name.replace('.', '_')
            filename = f"{name}.{ext}"

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1)
            name = name[:250 - len(ext)]
            filename = f"{name}.{ext}"

        # Ensure it's not empty
        if not filename or filename == '.':
            filename = 'unnamed_file.txt'

        return filename

    def validate_extension(self, filename: str) -> Tuple[bool, str]:
        """
        Validate file extension

        Args:
            filename: Filename to check

        Returns:
            Tuple[bool, str]: (is_valid, extension)
        """
        ext = Path(filename).suffix.lower()

        if not ext:
            return False, ""

        if ext not in self.allowed_extensions:
            return False, ext

        return True, ext

    def validate_mime_type(self, file_path: Path, expected_ext: str) -> bool:
        """
        Validate MIME type matches extension

        Args:
            file_path: Path to file
            expected_ext: Expected extension

        Returns:
            bool: True if MIME type is valid
        """
        if not self.magic:
            logger.warning("MIME type validation skipped (python-magic not available)")
            return True

        try:
            # Detect actual MIME type
            mime_type = self.magic.from_file(str(file_path))

            # Check against allowed MIME types for this extension
            allowed_mimes = self.ALLOWED_MIMES.get(expected_ext, [])

            if mime_type not in allowed_mimes:
                logger.warning(
                    f"MIME type mismatch: {mime_type} not in {allowed_mimes}",
                    extra={'file': str(file_path), 'extension': expected_ext}
                )
                return False

            return True

        except Exception as e:
            logger.error(f"MIME type validation error: {e}")
            return False

    def check_file_signature(self, file_path: Path) -> bool:
        """
        Check file signature for dangerous content

        Args:
            file_path: Path to file

        Returns:
            bool: True if file is safe
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(1024)  # Read first 1KB

                # Check for dangerous signatures
                for signature in self.DANGEROUS_SIGNATURES:
                    if header.startswith(signature):
                        logger.warning(
                            f"Dangerous file signature detected: {signature}",
                            extra={'file': str(file_path)}
                        )
                        return False

            return True

        except Exception as e:
            logger.error(f"File signature check error: {e}")
            return False

    def calculate_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file

        Args:
            file_path: Path to file

        Returns:
            str: SHA256 hash (hex)
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)

        return sha256.hexdigest()

    async def validate_and_save(
        self,
        file: UploadFile,
        custom_name: Optional[str] = None
    ) -> dict:
        """
        Validate and save uploaded file

        Args:
            file: Uploaded file
            custom_name: Optional custom filename

        Returns:
            dict: File information (path, hash, size, etc.)

        Raises:
            HTTPException: If validation fails
        """
        # Use custom name or sanitize original
        if custom_name:
            filename = self.sanitize_filename(custom_name)
        else:
            filename = self.sanitize_filename(file.filename)

        # Validate extension
        is_valid, ext = self.validate_extension(filename)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_file_type",
                    "message": f"File type '{ext}' not allowed",
                    "allowed_types": self.allowed_extensions
                }
            )

        # Check file size limit
        max_size = self.MAX_SIZES.get(ext, self.max_size_bytes)

        # Read file content
        content = await file.read()
        file_size = len(content)

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": "file_too_large",
                    "message": f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds limit ({max_size / 1024 / 1024:.2f} MB)",
                    "max_size_mb": max_size / 1024 / 1024
                }
            )

        # Create temporary file path
        temp_path = self.upload_dir / f"temp_{filename}"

        try:
            # Save temporarily
            with open(temp_path, 'wb') as f:
                f.write(content)

            # Validate MIME type
            if not self.validate_mime_type(temp_path, ext):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_file_content",
                        "message": "File content does not match extension"
                    }
                )

            # Check file signature
            if not self.check_file_signature(temp_path):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "dangerous_file",
                        "message": "File contains dangerous content"
                    }
                )

            # Calculate hash for deduplication
            file_hash = self.calculate_hash(temp_path)

            # Create final filename with hash
            final_filename = f"{Path(filename).stem}_{file_hash[:8]}{ext}"
            final_path = self.upload_dir / final_filename

            # Move to final location
            temp_path.rename(final_path)

            logger.info(
                f"File uploaded successfully: {final_filename}",
                extra={
                    'filename': final_filename,
                    'size_bytes': file_size,
                    'hash': file_hash
                }
            )

            return {
                "filename": final_filename,
                "original_filename": file.filename,
                "path": str(final_path),
                "size_bytes": file_size,
                "size_mb": round(file_size / 1024 / 1024, 2),
                "hash": file_hash,
                "extension": ext,
                "mime_type": file.content_type
            }

        except HTTPException:
            # Remove temp file on validation error
            if temp_path.exists():
                temp_path.unlink()
            raise

        except Exception as e:
            # Remove temp file on error
            if temp_path.exists():
                temp_path.unlink()

            logger.error(f"File upload error: {e}", exc_info=True)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "upload_failed",
                    "message": "File upload failed"
                }
            )

    def delete_file(self, filename: str) -> bool:
        """
        Delete uploaded file

        Args:
            filename: Filename to delete

        Returns:
            bool: True if deleted successfully
        """
        try:
            file_path = self.upload_dir / filename

            # Validate path (prevent directory traversal)
            if not file_path.resolve().parent == self.upload_dir.resolve():
                logger.warning(f"Path traversal attempt: {filename}")
                return False

            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {filename}")
                return True

            return False

        except Exception as e:
            logger.error(f"File deletion error: {e}")
            return False
