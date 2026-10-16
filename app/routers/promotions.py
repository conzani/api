from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.schemas.promotions import (
    PromotionCreate, PromotionUpdate, PromotionResponse,
    PromotionWindowCreate, PromotionWindowUpdate, PromotionWindowResponse,
    PromotionTargetCreate, PromotionTargetUpdate, PromotionTargetResponse,
    PromotionStoreCreate, PromotionStoreResponse,
    CouponCreate, CouponUpdate, CouponResponse,
    OrderPromotionCreate, OrderPromotionUpdate, OrderPromotionResponse
)
from app.models.promotions import (
    Promotion, PromotionWindow, PromotionTarget, PromotionStore,
    Coupon, OrderPromotion
)
from app.core.security import generate_public_id

router = APIRouter(prefix="/promotions", tags=["Promotions"])


# Promotion endpoints
@router.post("/", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(promotion: PromotionCreate, db: Session = Depends(get_db)):
    """Create a new promotion."""
    new_promotion = Promotion(
        public_id=generate_public_id(),
        **promotion.model_dump()
    )
    db.add(new_promotion)
    db.commit()
    db.refresh(new_promotion)
    return PromotionResponse(
        id=new_promotion.public_id,
        name=new_promotion.name,
        description=new_promotion.description,
        type=new_promotion.type,
        value=new_promotion.value,
        buy_quantity=new_promotion.buy_quantity,
        get_quantity=new_promotion.get_quantity,
        applies_to=new_promotion.applies_to,
        min_order_amount=new_promotion.min_order_amount,
        max_discount_amount=new_promotion.max_discount_amount,
        requires_code=new_promotion.requires_code,
        is_stackable=new_promotion.is_stackable,
        priority=new_promotion.priority,
        usage_limit=new_promotion.usage_limit,
        usage_limit_per_customer=new_promotion.usage_limit_per_customer,
        starts_at=new_promotion.starts_at,
        ends_at=new_promotion.ends_at,
        status=new_promotion.status,
        business_id=new_promotion.business_id,
        created_by=new_promotion.created_by,
        used_count=new_promotion.used_count,
        created_at=new_promotion.created_at,
        updated_at=new_promotion.updated_at,
        deleted_at=new_promotion.deleted_at,
    )


@router.get("/", response_model=List[PromotionResponse])
def get_promotions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all promotions with pagination."""
    promotions = db.query(Promotion).offset(skip).limit(limit).all()
    return [
        PromotionResponse(
            id=promotion.public_id,
            name=promotion.name,
            description=promotion.description,
            type=promotion.type,
            value=promotion.value,
            buy_quantity=promotion.buy_quantity,
            get_quantity=promotion.get_quantity,
            applies_to=promotion.applies_to,
            min_order_amount=promotion.min_order_amount,
            max_discount_amount=promotion.max_discount_amount,
            requires_code=promotion.requires_code,
            is_stackable=promotion.is_stackable,
            priority=promotion.priority,
            usage_limit=promotion.usage_limit,
            usage_limit_per_customer=promotion.usage_limit_per_customer,
            starts_at=promotion.starts_at,
            ends_at=promotion.ends_at,
            status=promotion.status,
            business_id=promotion.business_id,
            created_by=promotion.created_by,
            used_count=promotion.used_count,
            created_at=promotion.created_at,
            updated_at=promotion.updated_at,
            deleted_at=promotion.deleted_at,
        )
        for promotion in promotions
    ]


@router.get("/{id}", response_model=PromotionResponse)
def get_promotion(id: str, db: Session = Depends(get_db)):
    """Get a promotion by public_id."""
    promotion = db.query(Promotion).filter(Promotion.public_id == id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )
    return PromotionResponse(
        id=promotion.public_id,
        name=promotion.name,
        description=promotion.description,
        type=promotion.type,
        value=promotion.value,
        buy_quantity=promotion.buy_quantity,
        get_quantity=promotion.get_quantity,
        applies_to=promotion.applies_to,
        min_order_amount=promotion.min_order_amount,
        max_discount_amount=promotion.max_discount_amount,
        requires_code=promotion.requires_code,
        is_stackable=promotion.is_stackable,
        priority=promotion.priority,
        usage_limit=promotion.usage_limit,
        usage_limit_per_customer=promotion.usage_limit_per_customer,
        starts_at=promotion.starts_at,
        ends_at=promotion.ends_at,
        status=promotion.status,
        business_id=promotion.business_id,
        created_by=promotion.created_by,
        used_count=promotion.used_count,
        created_at=promotion.created_at,
        updated_at=promotion.updated_at,
        deleted_at=promotion.deleted_at,
    )


@router.put("/{id}", response_model=PromotionResponse)
def update_promotion(id: str, promotion_update: PromotionUpdate, db: Session = Depends(get_db)):
    """Update a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    update_data = promotion_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(promotion, field, value)

    db.commit()
    db.refresh(promotion)
    return PromotionResponse(
        id=promotion.public_id,
        name=promotion.name,
        description=promotion.description,
        type=promotion.type,
        value=promotion.value,
        buy_quantity=promotion.buy_quantity,
        get_quantity=promotion.get_quantity,
        applies_to=promotion.applies_to,
        min_order_amount=promotion.min_order_amount,
        max_discount_amount=promotion.max_discount_amount,
        requires_code=promotion.requires_code,
        is_stackable=promotion.is_stackable,
        priority=promotion.priority,
        usage_limit=promotion.usage_limit,
        usage_limit_per_customer=promotion.usage_limit_per_customer,
        starts_at=promotion.starts_at,
        ends_at=promotion.ends_at,
        status=promotion.status,
        business_id=promotion.business_id,
        created_by=promotion.created_by,
        used_count=promotion.used_count,
        created_at=promotion.created_at,
        updated_at=promotion.updated_at,
        deleted_at=promotion.deleted_at,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion(id: str, db: Session = Depends(get_db)):
    """Soft delete a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    promotion.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None


# Promotion Window endpoints
@router.post("/{promotion_id}/windows/", response_model=PromotionWindowResponse, status_code=status.HTTP_201_CREATED)
def create_promotion_window(promotion_id: str, window: PromotionWindowCreate, db: Session = Depends(get_db)):
    """Create a time window for a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    new_window = PromotionWindow(
        promotion_id=promotion.id,
        **window.model_dump()
    )
    db.add(new_window)
    db.commit()
    db.refresh(new_window)
    return new_window


@router.get("/{promotion_id}/windows/", response_model=List[PromotionWindowResponse])
def get_promotion_windows(promotion_id: str, db: Session = Depends(get_db)):
    """Get all time windows for a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    windows = db.query(PromotionWindow).filter(PromotionWindow.promotion_id == promotion.id).all()
    return windows


@router.get("/{promotion_id}/windows/{id}", response_model=PromotionWindowResponse)
def get_promotion_window(promotion_id: str, id: int, db: Session = Depends(get_db)):
    """Get a time window by ID."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    window = db.query(PromotionWindow).filter(
        PromotionWindow.promotion_id == promotion.id,
        PromotionWindow.id == id
    ).first()
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Window not found"
        )
    return window


@router.put("/{promotion_id}/windows/{id}", response_model=PromotionWindowResponse)
def update_promotion_window(promotion_id: str, id: int, window_update: PromotionWindowUpdate, db: Session = Depends(get_db)):
    """Update a time window."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    window = db.query(PromotionWindow).filter(
        PromotionWindow.promotion_id == promotion.id,
        PromotionWindow.id == id
    ).first()
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Window not found"
        )

    update_data = window_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(window, field, value)

    db.commit()
    db.refresh(window)
    return window


@router.delete("/{promotion_id}/windows/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion_window(promotion_id: str, id: int, db: Session = Depends(get_db)):
    """Delete a time window."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    window = db.query(PromotionWindow).filter(
        PromotionWindow.promotion_id == promotion.id,
        PromotionWindow.id == id
    ).first()
    if not window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Window not found"
        )

    db.delete(window)
    db.commit()

    return None


# Promotion Target endpoints
@router.post("/{promotion_id}/targets/", response_model=PromotionTargetResponse, status_code=status.HTTP_201_CREATED)
def create_promotion_target(promotion_id: str, target: PromotionTargetCreate, db: Session = Depends(get_db)):
    """Add a target to a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    new_target = PromotionTarget(
        promotion_id=promotion.id,
        **target.model_dump()
    )
    db.add(new_target)
    db.commit()
    db.refresh(new_target)
    return new_target


@router.get("/{promotion_id}/targets/", response_model=List[PromotionTargetResponse])
def get_promotion_targets(promotion_id: str, db: Session = Depends(get_db)):
    """Get all targets for a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    targets = db.query(PromotionTarget).filter(PromotionTarget.promotion_id == promotion.id).all()
    return targets


@router.delete("/{promotion_id}/targets/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion_target(promotion_id: str, id: int, db: Session = Depends(get_db)):
    """Delete a target from a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    target = db.query(PromotionTarget).filter(
        PromotionTarget.promotion_id == promotion.id,
        PromotionTarget.id == id
    ).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )

    db.delete(target)
    db.commit()

    return None


# Promotion Store endpoints
@router.post("/{promotion_id}/stores/", response_model=PromotionStoreResponse, status_code=status.HTTP_201_CREATED)
def add_promotion_store(promotion_id: str, store: PromotionStoreCreate, db: Session = Depends(get_db)):
    """Add a store to a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    new_store = PromotionStore(
        promotion_id=promotion.id,
        **store.model_dump()
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


@router.get("/{promotion_id}/stores/", response_model=List[PromotionStoreResponse])
def get_promotion_stores(promotion_id: str, db: Session = Depends(get_db)):
    """Get all stores for a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    stores = db.query(PromotionStore).filter(PromotionStore.promotion_id == promotion.id).all()
    return stores


@router.delete("/{promotion_id}/stores/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_promotion_store(promotion_id: str, id: int, db: Session = Depends(get_db)):
    """Remove a store from a promotion."""
    promotion = db.query(Promotion).filter(Promotion.public_id == promotion_id).first()
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotion not found"
        )

    store = db.query(PromotionStore).filter(
        PromotionStore.promotion_id == promotion.id,
        PromotionStore.id == id
    ).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    db.delete(store)
    db.commit()

    return None


# Coupon endpoints
@router.post("/coupons/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(coupon: CouponCreate, db: Session = Depends(get_db)):
    """Create a new coupon."""
    new_coupon = Coupon(
        public_id=generate_public_id(),
        **coupon.model_dump()
    )
    db.add(new_coupon)
    db.commit()
    db.refresh(new_coupon)
    return CouponResponse(
        id=new_coupon.public_id,
        code=new_coupon.code,
        usage_limit=new_coupon.usage_limit,
        expires_at=new_coupon.expires_at,
        status=new_coupon.status,
        business_id=new_coupon.business_id,
        promotion_id=new_coupon.promotion_id,
        customer_id=new_coupon.customer_id,
        used_count=new_coupon.used_count,
        created_at=new_coupon.created_at,
    )


@router.get("/coupons/", response_model=List[CouponResponse])
def get_coupons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all coupons with pagination."""
    coupons = db.query(Coupon).offset(skip).limit(limit).all()
    return [
        CouponResponse(
            id=coupon.public_id,
            code=coupon.code,
            usage_limit=coupon.usage_limit,
            expires_at=coupon.expires_at,
            status=coupon.status,
            business_id=coupon.business_id,
            promotion_id=coupon.promotion_id,
            customer_id=coupon.customer_id,
            used_count=coupon.used_count,
            created_at=coupon.created_at,
        )
        for coupon in coupons
    ]


@router.get("/coupons/{id}", response_model=CouponResponse)
def get_coupon(id: str, db: Session = Depends(get_db)):
    """Get a coupon by public_id."""
    coupon = db.query(Coupon).filter(Coupon.public_id == id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    return CouponResponse(
        id=coupon.public_id,
        code=coupon.code,
        usage_limit=coupon.usage_limit,
        expires_at=coupon.expires_at,
        status=coupon.status,
        business_id=coupon.business_id,
        promotion_id=coupon.promotion_id,
        customer_id=coupon.customer_id,
        used_count=coupon.used_count,
        created_at=coupon.created_at,
    )


@router.put("/coupons/{id}", response_model=CouponResponse)
def update_coupon(id: str, coupon_update: CouponUpdate, db: Session = Depends(get_db)):
    """Update a coupon."""
    coupon = db.query(Coupon).filter(Coupon.public_id == id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    update_data = coupon_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(coupon, field, value)

    db.commit()
    db.refresh(coupon)
    return CouponResponse(
        id=coupon.public_id,
        code=coupon.code,
        usage_limit=coupon.usage_limit,
        expires_at=coupon.expires_at,
        status=coupon.status,
        business_id=coupon.business_id,
        promotion_id=coupon.promotion_id,
        customer_id=coupon.customer_id,
        used_count=coupon.used_count,
        created_at=coupon.created_at,
    )


@router.delete("/coupons/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(id: str, db: Session = Depends(get_db)):
    """Delete a coupon."""
    coupon = db.query(Coupon).filter(Coupon.public_id == id).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    db.delete(coupon)
    db.commit()

    return None


# Order Promotion endpoints
@router.post("/order-promotions/", response_model=OrderPromotionResponse, status_code=status.HTTP_201_CREATED)
def create_order_promotion(order_promotion: OrderPromotionCreate, db: Session = Depends(get_db)):
    """Create an order promotion record (discount applied)."""
    new_order_promotion = OrderPromotion(**order_promotion.model_dump())
    db.add(new_order_promotion)
    db.commit()
    db.refresh(new_order_promotion)
    return new_order_promotion


@router.get("/order-promotions/", response_model=List[OrderPromotionResponse])
def get_order_promotions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all order promotions with pagination."""
    order_promotions = db.query(OrderPromotion).offset(skip).limit(limit).all()
    return order_promotions


@router.get("/order-promotions/{id}", response_model=OrderPromotionResponse)
def get_order_promotion(id: int, db: Session = Depends(get_db)):
    """Get an order promotion by ID."""
    order_promotion = db.query(OrderPromotion).filter(OrderPromotion.id == id).first()
    if not order_promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order promotion not found"
        )
    return order_promotion


@router.put("/order-promotions/{id}", response_model=OrderPromotionResponse)
def update_order_promotion(id: int, order_promotion_update: OrderPromotionUpdate, db: Session = Depends(get_db)):
    """Update an order promotion."""
    order_promotion = db.query(OrderPromotion).filter(OrderPromotion.id == id).first()
    if not order_promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order promotion not found"
        )

    update_data = order_promotion_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order_promotion, field, value)

    db.commit()
    db.refresh(order_promotion)
    return order_promotion


@router.delete("/order-promotions/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_promotion(id: int, db: Session = Depends(get_db)):
    """Delete an order promotion."""
    order_promotion = db.query(OrderPromotion).filter(OrderPromotion.id == id).first()
    if not order_promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order promotion not found"
        )

    db.delete(order_promotion)
    db.commit()

    return None
