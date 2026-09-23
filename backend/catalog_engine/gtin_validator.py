"""
Brand Battle — GTIN / EAN / UPC Validation Engine
Implements GS1 standard Modulo-10 check digit algorithms, length verification,
and bogus/dummy identifier filtering. Never fabricates identifiers.
"""

import re
from typing import Tuple, Optional


class GtinValidator:
    """
    Validates Global Trade Item Numbers (GTIN-8, UPC-12, EAN-13, GTIN-14).
    Adheres strictly to GS1 specifications.
    """

    VALID_LENGTHS = {8, 12, 13, 14}

    # Common dummy or placeholder patterns to reject
    DUMMY_PATTERNS = {
        "00000000", "000000000000", "0000000000000", "00000000000000",
        "11111111", "111111111111", "1111111111111", "11111111111111",
        "12345678", "123456789012", "1234567890128", "12345678901231"
    }

    @classmethod
    def clean_gtin(cls, raw: Optional[str]) -> Optional[str]:
        """Cleans and extracts only digits from input string."""
        if not raw or not isinstance(raw, str):
            return None
        digits_only = re.sub(r"\D", "", raw.strip())
        return digits_only if digits_only else None

    @classmethod
    def calculate_check_digit(cls, digits_without_check: str) -> int:
        """
        Calculates GS1 standard Modulo-10 check digit.
        Digits are processed from right to left with alternating weights of 3 and 1.
        """
        total = 0
        reverse_digits = digits_without_check[::-1]
        for idx, char in enumerate(reverse_digits):
            weight = 3 if idx % 2 == 0 else 1
            total += int(char) * weight
        
        remainder = total % 10
        return 0 if remainder == 0 else 10 - remainder

    @classmethod
    def validate(cls, raw_identifier: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates an identifier.
        Returns: (is_valid: bool, cleaned_gtin: Optional[str], error_reason: Optional[str])
        """
        cleaned = cls.clean_gtin(raw_identifier)
        if not cleaned:
            return False, None, "Empty or non-numeric identifier"

        length = len(cleaned)
        if length not in cls.VALID_LENGTHS:
            return False, cleaned, f"Invalid GTIN length {length}. Expected 8, 12, 13, or 14 digits."

        if cleaned in cls.DUMMY_PATTERNS or len(set(cleaned)) == 1:
            return False, cleaned, "Rejected repeating or dummy test identifier."

        # Modulo-10 check digit verification
        digits_body = cleaned[:-1]
        expected_check = cls.calculate_check_digit(digits_body)
        actual_check = int(cleaned[-1])

        if expected_check != actual_check:
            return (
                False,
                cleaned,
                f"Checksum mismatch: expected check digit {expected_check}, found {actual_check}."
            )

        return True, cleaned, None

    @classmethod
    def classify_type(cls, valid_gtin: str) -> str:
        """Returns standard type name for a validated GTIN."""
        length = len(valid_gtin)
        if length == 8:
            return "GTIN-8"
        elif length == 12:
            return "UPC-A"
        elif length == 13:
            return "EAN-13"
        elif length == 14:
            return "GTIN-14"
        return "UNKNOWN"
