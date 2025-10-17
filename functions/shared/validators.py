"""
Validators
Validation functions for inputs and data
"""

import re
from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension

    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (e.g., ['.docx', '.doc'])

    Returns:
        True if valid

    Raises:
        ValidationError: If extension not allowed
    """
    ext = filename.lower().split('.')[-1]

    if not any(filename.lower().endswith(allowed_ext) for allowed_ext in allowed_extensions):
        raise ValidationError(
            f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    return True


def validate_guid(guid: str) -> bool:
    """
    Validate GUID format

    Args:
        guid: GUID string to validate

    Returns:
        True if valid GUID

    Raises:
        ValidationError: If invalid GUID format
    """
    guid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )

    if not guid_pattern.match(guid):
        raise ValidationError("Invalid GUID format")

    return True


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that required fields are present in data

    Args:
        data: Data dictionary to validate
        required_fields: List of required field names

    Returns:
        True if all required fields present

    Raises:
        ValidationError: If required field missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )

    return True


def validate_file_size(file_size: int, max_size_mb: int = 25) -> bool:
    """
    Validate file size

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        True if size is valid

    Raises:
        ValidationError: If file too large
    """
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise ValidationError(
            f"File size ({file_size / 1024 / 1024:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
        )

    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove dangerous characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators and other dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    return filename
