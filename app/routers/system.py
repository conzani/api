from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.system import SessionCreate, SessionResponse, VerificationTokenCreate, VerificationTokenResponse, InvitationCreate, InvitationResponse, AuditLogCreate, AuditLogResponse
from app.models.system import Session, VerificationToken, Invitation, AuditLog
from app.core.security import generate_public_id

router = APIRouter(prefix="/system", tags=["System"])


# Session endpoints
@router.post("/sessions/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new session."""
    new_session = Session(**session.model_dump())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/sessions/", response_model=List[SessionResponse])
def get_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all sessions with pagination."""
    sessions = db.query(Session).offset(skip).limit(limit).all()
    return sessions


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(session_id: int, db: Session = Depends(get_db)):
    """Revoke a session."""
    from datetime import datetime
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session.revoked_at = datetime.utcnow()
    db.commit()
    return None


# Verification Token endpoints
@router.post("/verification-tokens/", response_model=VerificationTokenResponse, status_code=status.HTTP_201_CREATED)
def create_verification_token(token: VerificationTokenCreate, db: Session = Depends(get_db)):
    """Create a new verification token."""
    new_token = VerificationToken(**token.model_dump())
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token


@router.get("/verification-tokens/", response_model=List[VerificationTokenResponse])
def get_verification_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all verification tokens with pagination."""
    tokens = db.query(VerificationToken).offset(skip).limit(limit).all()
    return tokens


# Invitation endpoints
@router.post("/invitations/", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_invitation(invitation: InvitationCreate, db: Session = Depends(get_db)):
    """Create a new invitation."""
    new_invitation = Invitation(
        token_hash=generate_public_id(),
        **invitation.model_dump(exclude={"token_hash"})
    )
    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)
    return new_invitation


@router.get("/invitations/", response_model=List[InvitationResponse])
def get_invitations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all invitations with pagination."""
    invitations = db.query(Invitation).offset(skip).limit(limit).all()
    return invitations


@router.post("/invitations/{invitation_id}/accept", status_code=status.HTTP_200_OK)
def accept_invitation(invitation_id: int, db: Session = Depends(get_db)):
    """Accept an invitation."""
    from datetime import datetime
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    if invitation.accepted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already accepted"
        )

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )

    invitation.accepted_at = datetime.utcnow()
    db.commit()

    return {"message": "Invitation accepted successfully"}


# Audit Log endpoints
@router.post("/audit-logs/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(audit_log: AuditLogCreate, db: Session = Depends(get_db)):
    """Create a new audit log entry."""
    new_log = AuditLog(**audit_log.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/audit-logs/", response_model=List[AuditLogResponse])
def get_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all audit logs with pagination."""
    logs = db.query(AuditLog).offset(skip).limit(limit).all()
    return logs


@router.get("/audit-logs/{id}", response_model=List[AuditLogResponse])
def get_business_audit_logs(id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get audit logs for a specific business."""
    from app.models.businesses import Business
    business = db.query(Business).filter(Business.public_id == id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    logs = db.query(AuditLog).filter(AuditLog.business_id == business.id).offset(skip).limit(limit).all()
    return logs
