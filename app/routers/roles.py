from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, PermissionCreate, PermissionUpdate, PermissionResponse, RolePermissionGroupCreate
from app.models.roles import Role, Permission, RolePermissionGroup
from app.core.security import generate_public_id

router = APIRouter(prefix="/roles", tags=["Roles"])


# Role endpoints
@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role."""
    new_role = Role(
        public_id=generate_public_id(),
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        business_id=role.business_id,
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return RoleResponse(
        id=new_role.public_id,
        name=new_role.name,
        description=new_role.description,
        is_system=new_role.is_system,
        created_at=new_role.created_at,
        updated_at=new_role.updated_at,
        deleted_at=new_role.deleted_at,
    )


@router.get("/", response_model=List[RoleResponse])
def get_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all roles with pagination."""
    roles = db.query(Role).offset(skip).limit(limit).all()
    # Transform to use public_id as id
    return [
        RoleResponse(
            id=role.public_id,
            name=role.name,
            description=role.description,
            is_system=role.is_system,
            created_at=role.created_at,
            updated_at=role.updated_at,
            deleted_at=role.deleted_at,
        )
        for role in roles
    ]


@router.get("/{id}", response_model=RoleResponse)
def get_role(id: str, db: Session = Depends(get_db)):
    """Get a role by public_id."""
    role = db.query(Role).filter(Role.public_id == id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return RoleResponse(
        id=role.public_id,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        updated_at=role.updated_at,
        deleted_at=role.deleted_at,
    )


@router.put("/{id}", response_model=RoleResponse)
def update_role(id: str, role_update: RoleUpdate, db: Session = Depends(get_db)):
    """Update a role."""
    role = db.query(Role).filter(Role.public_id == id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    update_data = role_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)

    db.commit()
    db.refresh(role)
    return RoleResponse(
        id=role.public_id,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        updated_at=role.updated_at,
        deleted_at=role.deleted_at,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(id: str, db: Session = Depends(get_db)):
    """Soft delete a role."""
    from datetime import datetime
    role = db.query(Role).filter(Role.public_id == id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    role.deleted_at = datetime.utcnow()
    db.commit()
    return None


# Permission endpoints
@router.post("/permissions/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    """Create a new permission."""
    new_permission = Permission(
        public_id=generate_public_id(),
        code=permission.code,
        name=permission.name,
        description=permission.description,
    )
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return PermissionResponse(
        id=new_permission.public_id,
        code=new_permission.code,
        name=new_permission.name,
        description=new_permission.description,
        created_at=new_permission.created_at,
        updated_at=new_permission.updated_at,
        deleted_at=new_permission.deleted_at,
    )


@router.get("/permissions/", response_model=List[PermissionResponse])
def get_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all permissions with pagination."""
    permissions = db.query(Permission).offset(skip).limit(limit).all()
    # Transform to use public_id as id
    return [
        PermissionResponse(
            id=perm.public_id,
            code=perm.code,
            name=perm.name,
            description=perm.description,
            created_at=perm.created_at,
            updated_at=perm.updated_at,
            deleted_at=perm.deleted_at,
        )
        for perm in permissions
    ]


@router.post("/{id}/permissions/", status_code=status.HTTP_201_CREATED)
def assign_permission_to_role(id: str, assignment: RolePermissionGroupCreate, db: Session = Depends(get_db)):
    """Assign a permission to a role."""
    role = db.query(Role).filter(Role.public_id == id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Check if assignment already exists
    existing = db.query(RolePermissionGroup).filter(
        RolePermissionGroup.role_id == role.id,
        RolePermissionGroup.permission_id == assignment.permission_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already assigned to role"
        )

    new_assignment = RolePermissionGroup(
        role_id=role.id,
        permission_id=assignment.permission_id,
    )
    db.add(new_assignment)
    db.commit()

    return {"message": "Permission assigned to role successfully"}
