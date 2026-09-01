"""
Brand Battle — Legacy Auth Re-export Facade
Re-exports all utilities from auth/ package for 100% backward compatibility.
"""

from auth.password import hash_password, verify_password
from auth.jwt import create_access_token, decode_access_token
from auth.dependencies import get_current_user, get_current_user_optional, get_admin_user, security

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_current_user_optional",
    "get_admin_user",
    "security",
]
