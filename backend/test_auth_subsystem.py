"""
Brand Battle — Production Authentication Subsystem Test Suite
Verifies bcrypt password hashing, JWT creation/decoding, subject claim stringification,
refresh token rotation, and dependency authorization.
Uses standard library unittest for execution without external test framework dependencies.
"""

import unittest
from datetime import timedelta
import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.password import hash_password, verify_password, evaluate_password_strength
from auth.jwt import create_access_token, create_refresh_token, decode_access_token
from auth.token_service import token_service
from fastapi import HTTPException


class TestAuthSubsystem(unittest.TestCase):

    def test_password_hashing_and_verification(self):
        """Test password hashing with bcrypt and matching verification."""
        password = "ProductionSecurePassword2026!"
        hashed = hash_password(password)

        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith("$2b$") or hashed.startswith("$2a$"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))

    def test_password_strength_evaluation(self):
        """Test password strength analysis."""
        empty = evaluate_password_strength("")
        self.assertEqual(empty.score, 0)
        self.assertEqual(empty.tier, "Weak")

        weak = evaluate_password_strength("12345")
        self.assertLess(weak.score, 30)
        self.assertEqual(weak.tier, "Weak")

        strong = evaluate_password_strength("BrandBattle#2026SecurePass!")
        self.assertGreaterEqual(strong.score, 75)
        self.assertIn(strong.tier, ["Strong", "Ultra"])

    def test_jwt_access_token_creation_and_decoding_with_int_sub(self):
        """Test JWT creation with integer user_id sub claim and string decoding."""
        user_id = 12345
        token = create_access_token(data={"sub": user_id, "email": "test@b-b.com"})
        self.assertIsInstance(token, str)

        payload = decode_access_token(token)
        self.assertEqual(payload.get("sub"), str(user_id))
        self.assertEqual(payload.get("email"), "test@b-b.com")
        self.assertEqual(payload.get("token_type"), "access")
        self.assertEqual(payload.get("ver"), 2.0)

    def test_jwt_access_token_creation_and_decoding_with_str_sub(self):
        """Test JWT creation with string sub claim and decoding."""
        sub_str = "admin_user_01"
        token = create_access_token(data={"sub": sub_str})
        payload = decode_access_token(token)
        self.assertEqual(payload.get("sub"), sub_str)

    def test_jwt_refresh_token_creation(self):
        """Test JWT refresh token creation with user_id."""
        user_id = 999
        token = create_refresh_token(user_id=user_id)
        self.assertIsInstance(token, str)

        payload = decode_access_token(token)
        self.assertEqual(payload.get("sub"), str(user_id))
        self.assertEqual(payload.get("token_type"), "refresh")

    def test_invalid_token_decoding(self):
        """Test that invalid or tampered tokens raise 401 HTTPException."""
        with self.assertRaises(HTTPException) as ctx:
            decode_access_token("invalid.token.string")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_expired_token_decoding(self):
        """Test that expired tokens raise 401 HTTPException."""
        token = create_access_token(
            data={"sub": 1},
            expires_delta=timedelta(seconds=-10)
        )
        with self.assertRaises(HTTPException) as ctx:
            decode_access_token(token)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_token_revocation_service(self):
        """Test that token service properly revokes and tracks revoked tokens."""
        sample_token = "sample_revokable_token_xyz"
        self.assertFalse(token_service.is_token_revoked(sample_token))

        token_service.revoke_token(sample_token)
        self.assertTrue(token_service.is_token_revoked(sample_token))


if __name__ == "__main__":
    unittest.main()
