from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.customer import AddressCreate, AddressUpdate, AddressResponse, CustomerCreate, CustomerUpdate, CustomerResponse
from app.models.customers import Address, Customer
from app.core.security import generate_public_id

router = APIRouter(prefix="/customers", tags=["Customers"])


# Address endpoints
@router.post("/{customer_id}/address", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_customer_address(customer_id: str, address: AddressCreate, db: Session = Depends(get_db)):
    """Create an address for a specific customer and link it."""
    # Find customer by public_id
    customer = db.query(Customer).filter(Customer.public_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Create address
    new_address = Address(**address.model_dump())
    db.add(new_address)
    db.flush()

    # Update customer with new address_id
    customer.address_id = new_address.id
    db.commit()
    db.refresh(new_address)

    return new_address


@router.get("/{customer_id}/address", response_model=AddressResponse)
def get_customer_address(customer_id: str, db: Session = Depends(get_db)):
    """Get a customer's address."""
    customer = db.query(Customer).filter(Customer.public_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if not customer.address_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer has no address"
        )

    address = db.query(Address).filter(Address.id == customer.address_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    return address


@router.put("/{customer_id}/address", response_model=AddressResponse)
def update_customer_address(customer_id: str, address_update: AddressUpdate, db: Session = Depends(get_db)):
    """Update a customer's address."""
    customer = db.query(Customer).filter(Customer.public_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if not customer.address_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer has no address"
        )

    address = db.query(Address).filter(Address.id == customer.address_id).first()
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


@router.delete("/{customer_id}/address", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_address(customer_id: str, db: Session = Depends(get_db)):
    """Delete a customer's address and unlink it."""
    from datetime import datetime
    
    customer = db.query(Customer).filter(Customer.public_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    if not customer.address_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer has no address"
        )

    # Soft delete the address
    address = db.query(Address).filter(Address.id == customer.address_id).first()
    if address:
        address.deleted_at = datetime.utcnow()
    
    # Unlink from customer
    customer.address_id = None
    db.commit()

    return None


@router.post("/addresses/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    """Create a new address (not linked to customer)."""
    new_address = Address(**address.model_dump())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


@router.get("/addresses/", response_model=List[AddressResponse])
def get_addresses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all addresses with pagination."""
    addresses = db.query(Address).offset(skip).limit(limit).all()
    return addresses


@router.get("/addresses/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: Session = Depends(get_db)):
    """Get an address by ID."""
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    return address


@router.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, address_update: AddressUpdate, db: Session = Depends(get_db)):
    """Update an address."""
    address = db.query(Address).filter(Address.id == address_id).first()
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


# Customer endpoints
@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    new_customer = Customer(
        public_id=generate_public_id(),
        **customer.model_dump()
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return CustomerResponse(
        id=new_customer.public_id,
        customer_type=new_customer.customer_type,
        firstname=new_customer.firstname,
        lastname=new_customer.lastname,
        date_of_birth=new_customer.date_of_birth,
        gender=new_customer.gender,
        phone=new_customer.phone,
        email=new_customer.email,
        status=new_customer.status,
        created_at=new_customer.created_at,
        updated_at=new_customer.updated_at,
        deleted_at=new_customer.deleted_at,
    )


@router.get("/", response_model=List[CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all customers with pagination."""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    # Transform to use public_id as id
    return [
        CustomerResponse(
            id=customer.public_id,
            customer_type=customer.customer_type,
            firstname=customer.firstname,
            lastname=customer.lastname,
            date_of_birth=customer.date_of_birth,
            gender=customer.gender,
            phone=customer.phone,
            email=customer.email,
            status=customer.status,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            deleted_at=customer.deleted_at,
        )
        for customer in customers
    ]


@router.get("/{id}", response_model=CustomerResponse)
def get_customer(id: str, db: Session = Depends(get_db)):
    """Get a customer by public_id."""
    customer = db.query(Customer).filter(Customer.public_id == id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return CustomerResponse(
        id=customer.public_id,
        customer_type=customer.customer_type,
        firstname=customer.firstname,
        lastname=customer.lastname,
        date_of_birth=customer.date_of_birth,
        gender=customer.gender,
        phone=customer.phone,
        email=customer.email,
        status=customer.status,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        deleted_at=customer.deleted_at,
    )


@router.put("/{id}", response_model=CustomerResponse)
def update_customer(id: str, customer_update: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer."""
    customer = db.query(Customer).filter(Customer.public_id == id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return CustomerResponse(
        id=customer.public_id,
        customer_type=customer.customer_type,
        firstname=customer.firstname,
        lastname=customer.lastname,
        date_of_birth=customer.date_of_birth,
        gender=customer.gender,
        phone=customer.phone,
        email=customer.email,
        status=customer.status,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        deleted_at=customer.deleted_at,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: str, db: Session = Depends(get_db)):
    """Soft delete a customer."""
    from datetime import datetime
    customer = db.query(Customer).filter(Customer.public_id == id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    customer.deleted_at = datetime.utcnow()
    db.commit()
    return None
