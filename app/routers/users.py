from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.users import User, UserRole
from app.core.security import get_password_hash, generate_public_id, decode_token
from app.models.auth import Auth

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (public endpoint)."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create auth record
    auth = Auth(password_hash=get_password_hash(user.password))
    db.add(auth)
    db.flush()

    # Create user record
    new_user = User(
        public_id=generate_public_id(),
        auth_id=auth.id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        gender=user.gender,
        phone=user.phone,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.public_id,
        email=new_user.email,
        firstname=new_user.firstname,
        lastname=new_user.lastname,
        gender=new_user.gender,
        phone=new_user.phone,
        status=new_user.status,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        deleted_at=new_user.deleted_at,
    )


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get all users with pagination (requires authentication)."""
    # Verify token
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    # Transform to use public_id as id
    return [
        UserResponse(
            id=user.public_id,
            email=user.email,
            firstname=user.firstname,
            lastname=user.lastname,
            gender=user.gender,
            phone=user.phone,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )
        for user in users
    ]


@router.get("/{id}", response_model=UserResponse)
def get_user(
    id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get a user by public_id (requires authentication)."""
    # Verify token
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.public_id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse(
        id=user.public_id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        gender=user.gender,
        phone=user.phone,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
    )


@router.put("/{id}", response_model=UserResponse)
def update_user(
    id: str,
    user_update: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update a user (requires authentication)."""
    # Verify token
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.public_id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.public_id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname,
        gender=user.gender,
        phone=user.phone,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Soft delete a user (requires authentication)."""
    # Verify token
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.public_id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.deleted_at = datetime.utcnow()
    user.status = "deleted"
    db.commit()

    return None
