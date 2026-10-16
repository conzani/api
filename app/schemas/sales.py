from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# Store schemas
class StoreBase(BaseModel):
    name: str
    code: str
    phone: Optional[str] = None
    is_default: bool = False
    status: str = "active"


class StoreCreate(StoreBase):
    address_id: Optional[int] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    phone: Optional[str] = None
    address_id: Optional[int] = None
    is_default: Optional[bool] = None
    status: Optional[str] = None


class StoreResponse(StoreBase):
    id: str  # public_id
    address_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Tax schemas
class TaxBase(BaseModel):
    name: str
    rate: Decimal
    is_inclusive: bool = False
    is_active: bool = True


class TaxCreate(TaxBase):
    pass


class TaxUpdate(BaseModel):
    name: Optional[str] = None
    rate: Optional[Decimal] = None
    is_inclusive: Optional[bool] = None
    is_active: Optional[bool] = None


class TaxResponse(TaxBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Method schemas
class PaymentMethodBase(BaseModel):
    name: str
    code: str
    type: str  # cash, card, mobile_money, etc.
    is_active: bool = True


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None


class PaymentMethodResponse(PaymentMethodBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Order Item schemas
class OrderItemBase(BaseModel):
    product_name: str
    sku: str
    quantity: int
    unit_price: Decimal
    cost_price: Optional[Decimal] = None
    discount_amount: Decimal = 0
    tax_amount: Decimal = 0
    line_total: Decimal


class OrderItemCreate(OrderItemBase):
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    tax_id: Optional[int] = None


class OrderItemResponse(OrderItemBase):
    id: int
    business_id: int
    order_id: int
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    tax_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Order schemas
class OrderBase(BaseModel):
    order_number: str
    channel: str  # POS or online
    status: str = "draft"  # draft, completed, cancelled, refunded
    payment_status: str = "unpaid"  # unpaid, partial, paid
    subtotal: Decimal
    discount_total: Decimal = 0
    tax_total: Decimal = 0
    grand_total: Decimal
    amount_paid: Decimal = 0
    currency: str
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    store_id: Optional[int] = None
    customer_id: Optional[int] = None
    served_by: Optional[int] = None
    ordered_at: Optional[datetime] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    subtotal: Optional[Decimal] = None
    discount_total: Optional[Decimal] = None
    tax_total: Optional[Decimal] = None
    grand_total: Optional[Decimal] = None
    amount_paid: Optional[Decimal] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class OrderResponse(OrderBase):
    id: str  # public_id
    business_id: int
    store_id: Optional[int] = None
    customer_id: Optional[int] = None
    served_by: Optional[int] = None
    ordered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Payment schemas
class PaymentBase(BaseModel):
    amount: Decimal
    reference: Optional[str] = None
    status: str = "completed"


class PaymentCreate(PaymentBase):
    payment_method_id: int
    received_by: Optional[int] = None
    paid_at: Optional[datetime] = None


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    reference: Optional[str] = None
    status: Optional[str] = None
    paid_at: Optional[datetime] = None


class PaymentResponse(PaymentBase):
    id: str  # public_id
    business_id: int
    order_id: int
    payment_method_id: int
    received_by: Optional[int] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Order Return Item schemas
class OrderReturnItemBase(BaseModel):
    quantity: int
    refund_amount: Decimal
    restock: bool = True


class OrderReturnItemCreate(OrderReturnItemBase):
    order_item_id: int


class OrderReturnItemResponse(OrderReturnItemBase):
    id: int
    order_return_id: int
    order_item_id: int

    class Config:
        from_attributes = True


# Order Return schemas
class OrderReturnBase(BaseModel):
    return_number: str
    reason: Optional[str] = None
    refund_total: Decimal
    status: str = "pending"


class OrderReturnCreate(OrderReturnBase):
    processed_by: Optional[int] = None


class OrderReturnUpdate(BaseModel):
    reason: Optional[str] = None
    refund_total: Optional[Decimal] = None
    status: Optional[str] = None


class OrderReturnResponse(OrderReturnBase):
    id: str  # public_id
    business_id: int
    order_id: int
    processed_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
