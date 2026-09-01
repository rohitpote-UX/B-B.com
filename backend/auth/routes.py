"""
Brand Battle — Auth V2 Router
Exposes authentication, registration, password analysis, username availability, and session control endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate
from auth.schemas import UserCreateV2, UserLoginV2, TokenResponseV2, PasswordStrengthResult, UsernameCheckResponse, EmailValidationResponse
from auth.password import hash_password, verify_password, evaluate_password_strength
from auth.jwt import create_access_token, create_refresh_token
from auth.validators import check_username_availability, validate_email_address
from auth.dependencies import get_current_user
from auth.token_service import token_service
from auth.sessions import session_manager
from auth.audit import security_audit_logger

router = APIRouter(prefix="/api/auth", tags=["Authentication V2"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.id})
    security_audit_logger.log_event("signup_success", user_id=user.id)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login with email and password."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    if security_audit_logger.is_ip_locked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again in 15 minutes."
        )

    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        security_audit_logger.log_event("login_failed", ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="We couldn't verify your credentials. Please try again."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    access_token = create_access_token(data={"sub": user.id})
    session_manager.create_session(user_id=user.id, ip_address=client_ip)
    security_audit_logger.log_event("login_success", user_id=user.id, ip_address=client_ip)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url
    if update_data.preferences is not None:
        current_user.preferences = update_data.preferences

    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get("/check-username", response_model=UsernameCheckResponse)
async def check_username(username: str, db: Session = Depends(get_db)):
    """Live availability check for username."""
    is_avail, msg = check_username_availability(db, username)
    return UsernameCheckResponse(username=username, is_available=is_avail, message=msg)


@router.post("/evaluate-password", response_model=PasswordStrengthResult)
async def evaluate_password(data: dict):
    """Live strength & entropy evaluation for password."""
    password = data.get("password", "")
    return evaluate_password_strength(password)
