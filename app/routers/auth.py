from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    Token,
    AuthResponse,
)
from app.models.auth import Auth
from app.models.users import User, UserRole
from app.models.roles import Role
from app.models.customers import Customer
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_verification_code,
    generate_public_id,
)
from app.core.email import email_service
from app.core.config import settings
from app.core.deps import get_current_active_user
from app.core.rate_limiter import check_rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])


def register_rate_limit(request: Request):
    """Rate limit for registration."""
    return check_rate_limit(request, limit=settings.REGISTER_RATE_LIMIT, window=settings.REGISTER_RATE_WINDOW)


def login_rate_limit(request: Request):
    """Rate limit for login."""
    return check_rate_limit(request, limit=settings.LOGIN_RATE_LIMIT, window=settings.LOGIN_RATE_WINDOW)


def verification_rate_limit(request: Request):
    """Rate limit for verification."""
    return check_rate_limit(request, limit=settings.VERIFICATION_RATE_LIMIT, window=settings.VERIFICATION_RATE_WINDOW)


def password_reset_rate_limit(request: Request):
    """Rate limit for password reset."""
    return check_rate_limit(request, limit=settings.PASSWORD_RESET_RATE_LIMIT, window=settings.PASSWORD_RESET_RATE_WINDOW)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(register_rate_limit)])
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with Customer role."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create auth record
    auth = Auth(
        password_hash=get_password_hash(user_data.password),
        failed_attempts=0,
    )
    db.add(auth)
    db.flush()  # Get auth.id without committing

    # Create user record
    user = User(
        public_id=generate_public_id(),
        auth_id=auth.id,
        email=user_data.email,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        phone=user_data.phone,
        status="pending",  # Pending email verification
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(auth)

    # Assign Customer role to the new user
    customer_role = db.query(Role).filter(
        Role.name == "Customer",
        Role.business_id.is_(None),
        Role.is_system == True
    ).first()
    
    if customer_role:
        user_role = UserRole(
            user_id=user.id,
            role_id=customer_role.id,
            business_id=None,  # Platform-level role
            assigned_by=user.id,  # Self-assigned
        )
        db.add(user_role)
        db.commit()

    # Create customer record
    customer = Customer(
        auth_id=auth.id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        gender=user.gender,
        phone=user.phone,
        customer_type="individual",
        status="pending",  # Pending email verification
    )
    db.add(customer)
    db.commit()

    # Generate and store verification code in Redis (instead of database)
    from app.core.verification_manager import verification_code_manager
    verification_code = generate_verification_code()
    verification_code_manager.store_code(
        email=user.email,
        code=verification_code,
        purpose="email",
        ttl=settings.VERIFICATION_CODE_EXPIRE_MINUTES * 60
    )

    # Send verification email
    email_service.send_verification_email(
        to_email=user.email,
        verification_code=verification_code,
        user_name=f"{user.firstname} {user.lastname}".strip() or None,
    )

    return AuthResponse(
        id=customer.public_id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        gender=user.gender,
        phone=user.phone,
        customer_type=customer.customer_type,
        status=customer.status,
        email_verified_at=auth.email_verified_at,
        phone_verified_at=auth.phone_verified_at,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.post("/login", response_model=Token, dependencies=[Depends(login_rate_limit)])
def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Login with email and password."""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is locked
    auth = db.query(Auth).filter(Auth.id == user.auth_id).first()
    if auth.locked_until and auth.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked. Please try again later."
        )

    # Verify password
    if not verify_password(credentials.password, auth.password_hash):
        # Increment failed attempts
        auth.failed_attempts += 1
        # Lock account after 5 failed attempts
        if auth.failed_attempts >= 5:
            auth.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Reset failed attempts on successful login
    auth.failed_attempts = 0
    auth.last_login = datetime.now(timezone.utc)
    db.commit()

    # Check if email is verified
    if not auth.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "public_id": user.public_id})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "public_id": user.public_id})

    # Hash refresh token for storage
    from app.core.security import get_password_hash
    refresh_token_hash = get_password_hash(refresh_token)

    # Get client info
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Create session in Redis instead of database
    from app.core.session_manager import session_manager
    session_manager.create_session(
        user_id=user.id,
        refresh_token_hash=refresh_token_hash,
        device=user_agent[:100],  # Limit to 100 chars
        ip_address=client_host[:50],  # Limit to 50 chars
        expires_in_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/verify-email", dependencies=[Depends(verification_rate_limit)])
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify email with 6-digit code."""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify code using Redis
    from app.core.verification_manager import verification_code_manager
    if not verification_code_manager.verify_code(request.email, request.code, "email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    # Delete the code from Redis after successful verification
    verification_code_manager.delete_code(request.email, "email")

    # Update auth record
    auth = db.query(Auth).filter(Auth.id == user.auth_id).first()
    auth.email_verified_at = datetime.now(timezone.utc)

    # Update user status
    user.status = "active"

    # Update customer status
    customer = db.query(Customer).filter(Customer.auth_id == auth.id).first()
    if customer:
        customer.status = "active"

    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """Logout and revoke the current JWT token."""
    from app.core.session_manager import session_manager
    from app.core.token_blacklist import token_blacklist
    from app.core.config import settings
    
    # Revoke the user's session
    session_manager.revoke_all_user_sessions(current_user.id)
    
    # Revoke all tokens for this user
    token_blacklist.revoke_all_user_tokens(current_user.id, ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    
    return {"message": "Logged out successfully"}


@router.post("/logout-all")
def logout_all(current_user: User = Depends(get_current_active_user)):
    """Logout and revoke all tokens for the current user."""
    from app.core.session_manager import session_manager
    from app.core.token_blacklist import token_blacklist
    from app.core.config import settings
    
    # Revoke the user's session
    session_manager.revoke_all_user_sessions(current_user.id)
    
    # Revoke all tokens for this user
    token_blacklist.revoke_all_user_tokens(current_user.id, ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    
    return {"message": "Logged out from all devices successfully"}


@router.post("/resend-verification", dependencies=[Depends(verification_rate_limit)])
def resend_verification(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend verification email."""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if already verified
    auth = db.query(Auth).filter(Auth.id == user.auth_id).first()
    if auth.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Generate new verification code and store in Redis
    from app.core.verification_manager import verification_code_manager
    verification_code = generate_verification_code()
    verification_code_manager.store_code(
        email=user.email,
        code=verification_code,
        purpose="email",
        ttl=settings.VERIFICATION_CODE_EXPIRE_MINUTES * 60
    )

    # Send verification email
    email_service.send_verification_email(
        to_email=user.email,
        verification_code=verification_code,
        user_name=f"{user.firstname} {user.lastname}".strip() or None,
    )

    return {"message": "Verification email sent"}


@router.post("/password-reset", dependencies=[Depends(password_reset_rate_limit)])
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request a password reset (sends verification code)."""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "A reset code has been sent to your email"}

    # Generate reset code and store in Redis
    from app.core.verification_manager import verification_code_manager
    reset_code = generate_verification_code()
    verification_code_manager.store_code(
        email=user.email,
        code=reset_code,
        purpose="password_reset",
        ttl=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS * 3600
    )

    # Send password reset email
    email_service.send_password_reset_email(
        to_email=user.email,
        reset_code=reset_code,
        user_name=f"{user.firstname} {user.lastname}".strip() or None,
    )

    return {"message": "A reset code has been sent to your email"}


@router.post("/password-reset/confirm", dependencies=[Depends(password_reset_rate_limit)])
def confirm_password_reset(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Confirm password reset with code and new password."""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify code using Redis
    from app.core.verification_manager import verification_code_manager
    if not verification_code_manager.verify_code(request.email, request.code, "password_reset"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code"
        )

    # Delete the code from Redis after successful verification
    verification_code_manager.delete_code(request.email, "password_reset")

    # Update password
    auth = db.query(Auth).filter(Auth.id == user.auth_id).first()
    auth.password_hash = get_password_hash(request.new_password)
    auth.password_changed_at = datetime.now(timezone.utc)
    auth.failed_attempts = 0  # Reset failed attempts
    auth.locked_until = None  # Unlock account if locked

    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    from app.core.session_manager import session_manager
    from app.core.token_blacklist import token_blacklist
    from app.core.security import decode_token, get_password_hash
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if user's tokens are all blacklisted
    if token_blacklist.is_user_token_blacklisted(user.id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="All tokens for this user have been revoked"
        )
    
    # Hash the refresh token
    refresh_token_hash = get_password_hash(refresh_token)
    
    # Check if refresh token is blacklisted
    if token_blacklist.is_refresh_token_blacklisted(refresh_token_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )
    
    # Validate session in Redis
    session = session_manager.get_session_by_user_id(user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired"
        )
    
    # Verify refresh token hash matches stored hash
    if session.get("refresh_token_hash") != refresh_token_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Revoke old refresh token
    token_blacklist.revoke_refresh_token_hash(
        refresh_token_hash,
        ttl=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": str(user.id), "public_id": user.public_id})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id), "public_id": user.public_id})
    
    # Hash new refresh token
    new_refresh_token_hash = get_password_hash(new_refresh_token)
    
    # Update session with new refresh token hash
    session_manager.update_session(
        user_id=user_id,
        refresh_token_hash=new_refresh_token_hash,
        expires_in_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
