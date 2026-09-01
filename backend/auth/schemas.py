"""
Brand Battle — Auth Schemas V2.0
Pydantic data validation schemas for authentication, token rotation, sessions, and password security.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserCreateV2(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    agree_terms: bool = True
    receive_alerts: Optional[bool] = False


class UserLoginV2(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False
    device_fingerprint: Optional[str] = None


class PasswordStrengthResult(BaseModel):
    score: int = Field(ge=0, le=100)
    tier: str  # Weak, Fair, Good, Strong, Ultra
    entropy_bits: float
    estimated_crack_time: str
    has_min_length: bool
    has_uppercase: bool
    has_number: bool
    has_symbol: bool
    is_dictionary_word: bool


class UsernameCheckResponse(BaseModel):
    username: str
    is_available: bool
    message: str


class EmailValidationResponse(BaseModel):
    email: str
    is_valid: bool
    is_disposable: bool
    message: str


class TokenResponseV2(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 Hours
    user: Dict[str, Any]


class DeviceSession(BaseModel):
    session_id: str
    user_agent: str
    device_type: str
    ip_address: str
    country: str
    last_active: datetime
    is_current: bool


class SecurityAuditRecord(BaseModel):
    event_id: str
    user_id: Optional[int]
    event_type: str  # login_success, login_failed, password_changed, token_refreshed
    ip_address: str
    device_info: str
    timestamp: datetime
