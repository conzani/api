from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional, List
from decimal import Decimal


# Promotion Window schemas
class PromotionWindowBase(BaseModel):
    day_of_week: int  # 0-6 (Sunday-Saturday)
    start_time: time
    end_time: time


class PromotionWindowCreate(PromotionWindowBase):
    pass


class PromotionWindowUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class PromotionWindowResponse(PromotionWindowBase):
    id: int
    promotion_id: int

    class Config:
        from_attributes = True


# Promotion Target schemas
class PromotionTargetBase(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None


class PromotionTargetCreate(PromotionTargetBase):
    pass


class PromotionTargetUpdate(BaseModel):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None


class PromotionTargetResponse(PromotionTargetBase):
    id: int
    promotion_id: int

    class Config:
        from_attributes = True


# Promotion Store schemas
class PromotionStoreBase(BaseModel):
    store_id: int


class PromotionStoreCreate(PromotionStoreBase):
    pass


class PromotionStoreResponse(PromotionStoreBase):
    id: int
    promotion_id: int

    class Config:
        from_attributes = True


# Promotion schemas
class PromotionBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str  # percentage, fixed_amount, buy_x_get_y
    value: Optional[Decimal] = None
    buy_quantity: Optional[int] = None
    get_quantity: Optional[int] = None
    applies_to: str  # order, product, category, brand
    min_order_amount: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    requires_code: bool = False
    is_stackable: bool = False
    priority: int = 0
    usage_limit: Optional[int] = None
    usage_limit_per_customer: Optional[int] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, active, paused, expired


class PromotionCreate(PromotionBase):
    created_by: Optional[int] = None


class PromotionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    value: Optional[Decimal] = None
    buy_quantity: Optional[int] = None
    get_quantity: Optional[int] = None
    applies_to: Optional[str] = None
    min_order_amount: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    requires_code: Optional[bool] = None
    is_stackable: Optional[bool] = None
    priority: Optional[int] = None
    usage_limit: Optional[int] = None
    usage_limit_per_customer: Optional[int] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    status: Optional[str] = None


class PromotionResponse(PromotionBase):
    id: str  # public_id
    business_id: int
    created_by: Optional[int] = None
    used_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Coupon schemas
class CouponBase(BaseModel):
    code: str
    usage_limit: Optional[int] = None
    expires_at: Optional[datetime] = None
    status: str = "active"


class CouponCreate(CouponBase):
    promotion_id: int
    customer_id: Optional[int] = None


class CouponUpdate(BaseModel):
    code: Optional[str] = None
    usage_limit: Optional[int] = None
    expires_at: Optional[datetime] = None
    status: Optional[str] = None


class CouponResponse(CouponBase):
    id: str  # public_id
    business_id: int
    promotion_id: int
    customer_id: Optional[int] = None
    used_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# Order Promotion schemas
class OrderPromotionBase(BaseModel):
    discount_amount: Decimal


class OrderPromotionCreate(OrderPromotionBase):
    order_id: int
    order_item_id: Optional[int] = None
    promotion_id: int
    coupon_id: Optional[int] = None


class OrderPromotionUpdate(BaseModel):
    discount_amount: Optional[Decimal] = None


class OrderPromotionResponse(OrderPromotionBase):
    id: int
    business_id: int
    order_id: int
    order_item_id: Optional[int] = None
    promotion_id: int
    coupon_id: Optional[int] = None
    applied_at: datetime

    class Config:
        from_attributes = True
