"""
Brand Battle — Password Security & Strength Engine
Password hashing via bcrypt and real-time entropy / crack time evaluation.
"""

import math
import re
import bcrypt
from typing import Dict, Any
from auth.schemas import PasswordStrengthResult

COMMON_DICTIONARY_WORDS = {
    "password", "123456", "admin", "welcome", "brandbattle", "secret",
    "letmein", "qwerty", "dragon", "baseball", "football", "shadow"
}


def hash_password(password: str) -> str:
    """Hash a plaintext password using salted bcrypt."""
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def evaluate_password_strength(password: str) -> PasswordStrengthResult:
    """
    Evaluates entropy bits, crack time, dictionary usage, and character diversity.
    """
    if not password:
        return PasswordStrengthResult(
            score=0,
            tier="Weak",
            entropy_bits=0.0,
            estimated_crack_time="Instant",
            has_min_length=False,
            has_uppercase=False,
            has_number=False,
            has_symbol=False,
            is_dictionary_word=False
        )

    has_min_len = len(password) >= 8
    has_upper = bool(re.search(r'[A-Z]', password))
    has_num = bool(re.search(r'[0-9]', password))
    has_sym = bool(re.search(r'[^A-[#a-zA-Z0-9]', password))
    is_dict = password.lower() in COMMON_DICTIONARY_WORDS

    # Character set pool size calculation
    pool_size = 0
    if re.search(r'[a-z]', password):
        pool_size += 26
    if has_upper:
        pool_size += 26
    if has_num:
        pool_size += 10
    if has_sym:
        pool_size += 32

    pool_size = max(1, pool_size)
    entropy_bits = round(len(password) * math.log2(pool_size), 1)

    # Score out of 100
    score = min(100, int((entropy_bits / 80.0) * 100))
    if is_dict:
        score = min(20, score)

    # Tier determination
    if score >= 90:
        tier = "Ultra"
        crack_time = "Centuries"
    elif score >= 75:
        tier = "Strong"
        crack_time = "34 Years"
    elif score >= 50:
        tier = "Good"
        crack_time = "3 Months"
    elif score >= 30:
        tier = "Fair"
        crack_time = "3 Days"
    else:
        tier = "Weak"
        crack_time = "Seconds"

    return PasswordStrengthResult(
        score=score,
        tier=tier,
        entropy_bits=entropy_bits,
        estimated_crack_time=crack_time,
        has_min_length=has_min_len,
        has_uppercase=has_upper,
        has_number=has_num,
        has_symbol=has_sym,
        is_dictionary_word=is_dict
    )
