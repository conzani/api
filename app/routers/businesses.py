from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.business import (
    BusinessCreate, BusinessUpdate, BusinessResponse,
    BusinessUserCreate, BusinessUserResponse,
    BusinessTypeCreate, BusinessTypeUpdate, BusinessTypeResponse
)
from app.schemas.customer import AddressCreate, AddressUpdate, AddressResponse
from app.models.businesses import Business, BusinessUser, BusinessType
from app.models.customers import Address
from app.core.security import generate_public_id

router = APIRouter(prefix="/businesses", tags=["Businesses"])


# Business endpoints
@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
def create_business(business: BusinessCreate, db: Session = Depends(get_db)):
    """Create a new business."""
    new_business = Business(
        public_id=generate_public_id(),
        **business.model_dump()
    )
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    
    # Get business type if exists
    business_type = None
    if new_business.business_type_id:
        bt = db.query(BusinessType).filter(BusinessType.id == new_business.business_type_id).first()
        if bt:
            business_type = BusinessTypeResponse(
                id=bt.public_id,
                code=bt.code,
                name=bt.name,
                description=bt.description,
                created_at=bt.created_at,
                updated_at=bt.updated_at,
                deleted_at=bt.deleted_at,
            )
    
    return BusinessResponse(
        id=new_business.public_id,
        name=new_business.name,
        description=new_business.description,
        slogan=new_business.slogan,
        registration_number=new_business.registration_number,
        t_pin_number=new_business.t_pin_number,
        slug=new_business.slug,
        timezone=new_business.timezone,
        currency=new_business.currency,
        status=new_business.status,
        business_type=business_type,
        created_at=new_business.created_at,
        updated_at=new_business.updated_at,
        deleted_at=new_business.deleted_at,
    )


@router.get("/", response_model=List[BusinessResponse])
def get_businesses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all businesses with pagination."""
    businesses = db.query(Business).offset(skip).limit(limit).all()
    # Transform to use public_id as id and include business_type
    result = []
    for business in businesses:
        business_type = None
        if business.business_type_id:
            bt = db.query(BusinessType).filter(BusinessType.id == business.business_type_id).first()
            if bt:
                business_type = BusinessTypeResponse(
                    id=bt.public_id,
                    code=bt.code,
                    name=bt.name,
                    description=bt.description,
                    created_at=bt.created_at,
                    updated_at=bt.updated_at,
                    deleted_at=bt.deleted_at,
                )
        
        result.append(BusinessResponse(
            id=business.public_id,
            name=business.name,
            description=business.description,
            slogan=business.slogan,
            registration_number=business.registration_number,
            t_pin_number=business.t_pin_number,
            slug=business.slug,
            timezone=business.timezone,
            currency=business.currency,
            status=business.status,
            business_type=business_type,
            created_at=business.created_at,
            updated_at=business.updated_at,
            deleted_at=business.deleted_at,
        ))
    
    return result


@router.get("/{id}", response_model=BusinessResponse)
def get_business(id: str, db: Session = Depends(get_db)):
    """Get a business by public_id."""
    business = db.query(Business).filter(Business.public_id == id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Get business type if exists
    business_type = None
    if business.business_type_id:
        bt = db.query(BusinessType).filter(BusinessType.id == business.business_type_id).first()
        if bt:
            business_type = BusinessTypeResponse(
                id=bt.public_id,
                code=bt.code,
                name=bt.name,
                description=bt.description,
                created_at=bt.created_at,
                updated_at=bt.updated_at,
                deleted_at=bt.deleted_at,
            )
    
    return BusinessResponse(
        id=business.public_id,
        name=business.name,
        description=business.description,
        slogan=business.slogan,
        registration_number=business.registration_number,
        t_pin_number=business.t_pin_number,
        slug=business.slug,
        timezone=business.timezone,
        currency=business.currency,
        status=business.status,
        business_type=business_type,
        created_at=business.created_at,
        updated_at=business.updated_at,
        deleted_at=business.deleted_at,
    )


@router.put("/{id}", response_model=BusinessResponse)
def update_business(id: str, business_update: BusinessUpdate, db: Session = Depends(get_db)):
    """Update a business."""
    business = db.query(Business).filter(Business.public_id == id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    update_data = business_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business, field, value)

    db.commit()
    db.refresh(business)
    
    # Get business type if exists
    business_type = None
    if business.business_type_id:
        bt = db.query(BusinessType).filter(BusinessType.id == business.business_type_id).first()
        if bt:
            business_type = BusinessTypeResponse(
                id=bt.public_id,
                code=bt.code,
                name=bt.name,
                description=bt.description,
                created_at=bt.created_at,
                updated_at=bt.updated_at,
                deleted_at=bt.deleted_at,
            )
    
    return BusinessResponse(
        id=business.public_id,
        name=business.name,
        description=business.description,
        slogan=business.slogan,
        registration_number=business.registration_number,
        t_pin_number=business.t_pin_number,
        slug=business.slug,
        timezone=business.timezone,
        currency=business.currency,
        status=business.status,
        business_type=business_type,
        created_at=business.created_at,
        updated_at=business.updated_at,
        deleted_at=business.deleted_at,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(id: str, db: Session = Depends(get_db)):
    """Soft delete a business."""
    from datetime import datetime
    business = db.query(Business).filter(Business.public_id == id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    business.deleted_at = datetime.utcnow()
    db.commit()
    return None


# Business User endpoints
@router.post("/{id}/users/", response_model=BusinessUserResponse, status_code=status.HTTP_201_CREATED)
def add_user_to_business(id: str, business_user: BusinessUserCreate, db: Session = Depends(get_db)):
    """Add a user to a business."""
    business = db.query(Business).filter(Business.public_id == id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    # Check if user is already in business
    existing = db.query(BusinessUser).filter(
        BusinessUser.business_id == business.id,
        BusinessUser.user_id == business_user.user_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already in business"
        )

    new_business_user = BusinessUser(
        business_id=business.id,
        user_id=business_user.user_id,
        status=business_user.status,
    )
    db.add(new_business_user)
    db.commit()
    db.refresh(new_business_user)
    return new_business_user


@router.get("/{id}/users/", response_model=List[BusinessUserResponse])
def get_business_users(id: str, db: Session = Depends(get_db)):
    """Get all users in a business."""
    business = db.query(Business).filter(Business.public_id == id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    business_users = db.query(BusinessUser).filter(BusinessUser.business_id == business.id).all()
    return business_users


# Business Address endpoints
@router.post("/{business_id}/address", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_business_address(business_id: str, address: AddressCreate, db: Session = Depends(get_db)):
    """Create an address for a specific business and link it."""
    # Find business by public_id
    business = db.query(Business).filter(Business.public_id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    # Create address
    new_address = Address(**address.model_dump())
    db.add(new_address)
    db.flush()

    # Update business with new address_id
    business.address_id = new_address.id
    db.commit()
    db.refresh(new_address)

    return new_address


@router.get("/{business_id}/address", response_model=AddressResponse)
def get_business_address(business_id: str, db: Session = Depends(get_db)):
    """Get a business's address."""
    business = db.query(Business).filter(Business.public_id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    if not business.address_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business has no address"
        )

    address = db.query(Address).filter(Address.id == business.address_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    return address


@router.put("/{business_id}/address", response_model=AddressResponse)
def update_business_address(business_id: str, address_update: AddressUpdate, db: Session = Depends(get_db)):
    """Update a business's address."""
    business = db.query(Business).filter(Business.public_id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    if not business.address_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business has no address"
        )

    address = db.query(Address).filter(Address.id == business.address_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    update_data = address_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    return address


@router.delete("/{business_id}/address", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_address(business_id: str, db: Session = Depends(get_db)):
    """Delete a business's address and unlink it."""
    from datetime import datetime
    
    business = db.query(Business).filter(Business.public_id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )

    if not business.address_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business has no address"
        )

    # Soft delete the address
    address = db.query(Address).filter(Address.id == business.address_id).first()
    if address:
        address.deleted_at = datetime.utcnow()
    
    # Unlink from business
    business.address_id = None
    db.commit()

    return None


# Business Type endpoints
@router.post("/types/", response_model=BusinessTypeResponse, status_code=status.HTTP_201_CREATED)
def create_business_type(business_type: BusinessTypeCreate, db: Session = Depends(get_db)):
    """Create a new business type."""
    # Check if code already exists
    existing = db.query(BusinessType).filter(BusinessType.code == business_type.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business type code already exists"
        )

    new_business_type = BusinessType(
        public_id=generate_public_id(),
        **business_type.model_dump()
    )
    db.add(new_business_type)
    db.commit()
    db.refresh(new_business_type)
    return BusinessTypeResponse(
        id=new_business_type.public_id,
        code=new_business_type.code,
        name=new_business_type.name,
        description=new_business_type.description,
        created_at=new_business_type.created_at,
        updated_at=new_business_type.updated_at,
        deleted_at=new_business_type.deleted_at,
    )


@router.get("/types/", response_model=List[BusinessTypeResponse])
def get_business_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all business types with pagination."""
    business_types = db.query(BusinessType).offset(skip).limit(limit).all()
    return [
        BusinessTypeResponse(
            id=bt.public_id,
            code=bt.code,
            name=bt.name,
            description=bt.description,
            created_at=bt.created_at,
            updated_at=bt.updated_at,
            deleted_at=bt.deleted_at,
        )
        for bt in business_types
    ]


@router.get("/types/{id}", response_model=BusinessTypeResponse)
def get_business_type(id: str, db: Session = Depends(get_db)):
    """Get a business type by public_id."""
    business_type = db.query(BusinessType).filter(BusinessType.public_id == id).first()
    if not business_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business type not found"
        )
    return BusinessTypeResponse(
        id=business_type.public_id,
        code=business_type.code,
        name=business_type.name,
        description=business_type.description,
        created_at=business_type.created_at,
        updated_at=business_type.updated_at,
        deleted_at=business_type.deleted_at,
    )


@router.put("/types/{id}", response_model=BusinessTypeResponse)
def update_business_type(id: str, business_type_update: BusinessTypeUpdate, db: Session = Depends(get_db)):
    """Update a business type."""
    business_type = db.query(BusinessType).filter(BusinessType.public_id == id).first()
    if not business_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business type not found"
        )

    update_data = business_type_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business_type, field, value)

    db.commit()
    db.refresh(business_type)
    return BusinessTypeResponse(
        id=business_type.public_id,
        code=business_type.code,
        name=business_type.name,
        description=business_type.description,
        created_at=business_type.created_at,
        updated_at=business_type.updated_at,
        deleted_at=business_type.deleted_at,
    )


@router.delete("/types/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_type(id: str, db: Session = Depends(get_db)):
    """Soft delete a business type."""
    from datetime import datetime
    business_type = db.query(BusinessType).filter(BusinessType.public_id == id).first()
    if not business_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business type not found"
        )

    business_type.deleted_at = datetime.utcnow()
    db.commit()

    return None
