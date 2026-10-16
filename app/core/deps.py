from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.security import decode_token
from app.core.token_blacklist import token_blacklist
from app.models.users import User
from app.models.businesses import Business

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if token_blacklist.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user's tokens are all blacklisted
    if token_blacklist.is_user_token_blacklisted(int(user_id)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="All tokens for this user have been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user (check if user is active)."""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    if current_user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deleted"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get the current user with verified email."""
    if not current_user.auth.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    
    return current_user


async def get_business_by_public_id(
    business_public_id: str,
    db: Session = Depends(get_db)
) -> Business:
    """Get a business by public_id."""
    business = db.query(Business).filter(Business.public_id == business_public_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    return business


async def get_current_user_business(
    business_public_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> tuple[Business, bool]:
    """
    Get a business and check if the current user is a member.
    Returns (business, is_member).
    """
    from app.models.businesses import BusinessUser
    
    business = await get_business_by_public_id(business_public_id, db)
    
    # Check if user is a member of the business
    business_user = db.query(BusinessUser).filter(
        BusinessUser.business_id == business.id,
        BusinessUser.user_id == current_user.id,
        BusinessUser.status == "active"
    ).first()
    
    is_member = business_user is not None
    
    # Also check if user is the owner
    is_owner = business.owner_id == current_user.id
    
    return business, is_member or is_owner


async def require_business_member(
    business_public_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Business:
    """
    Require the current user to be a member of the business.
    Returns the business if user is a member, raises exception otherwise.
    """
    business, is_member = await get_current_user_business(business_public_id, current_user, db)
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this business"
        )
    
    return business


async def require_business_owner(
    business_public_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Business:
    """
    Require the current user to be the owner of the business.
    Returns the business if user is the owner, raises exception otherwise.
    """
    business = await get_business_by_public_id(business_public_id, db)
    
    if business.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this business"
        )
    
    return business


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authentication is provided, otherwise return None.
    Useful for endpoints that work both authenticated and unauthenticated.
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user
