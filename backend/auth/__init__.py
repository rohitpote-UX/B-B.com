"""
Brand Battle — Enterprise Auth Module V2.0
Exports security dependencies, password utilities, JWT creators, and route definitions.
"""

from auth.password import hash_password, verify_password, evaluate_password_strength
from auth.jwt import create_access_token, create_refresh_token, decode_access_token
from auth.dependencies import get_current_user, get_current_user_optional, get_admin_user
from auth.routes import router as auth_router

__all__ = [
    "hash_password",
    "verify_password",
    "evaluate_password_strength",
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "get_current_user",
    "get_current_user_optional",
    "get_admin_user",
    "auth_router",
]
