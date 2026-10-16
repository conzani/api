import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, Date, ForeignKey, Integer, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)


class Store(Base):
    __tablename__ = "stores"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    address_id = Column(BigInteger, ForeignKey("address.id"), nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=True)
    is_default = Column(Boolean, default=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="stores")
    address = relationship("Address", backref="stores")
    orders = relationship("Order", back_populates="store")


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=True)
    customer_id = Column(BigInteger, ForeignKey("customer.id"), nullable=True)
    served_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    order_number = Column(String(100), nullable=False)
    channel = Column(String(50), nullable=False)  # POS or online
    status = Column(String(50), default="draft")  # draft, completed, cancelled, refunded
    payment_status = Column(String(50), default="unpaid")  # unpaid, partial, paid
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_total = Column(Numeric(10, 2), nullable=False, server_default='0')
    tax_total = Column(Numeric(10, 2), nullable=False, server_default='0')
    grand_total = Column(Numeric(10, 2), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False, server_default='0')
    currency = Column(String(10), nullable=False)
    notes = Column(Text, nullable=True)
    ordered_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="orders")
    store = relationship("Store", back_populates="orders")
    customer = relationship("Customer", backref="orders")
    server = relationship("User", backref="served_orders", foreign_keys=[served_by])
    order_items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")
    order_returns = relationship("OrderReturn", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=True)
    variant_id = Column(BigInteger, ForeignKey("product_variants.id"), nullable=True)
    tax_id = Column(BigInteger, ForeignKey("taxes.id"), nullable=True)
    product_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)
    discount_amount = Column(Numeric(10, 2), nullable=False, server_default='0')
    tax_amount = Column(Numeric(10, 2), nullable=False, server_default='0')
    line_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="order_items")
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", backref="order_items")
    variant = relationship("ProductVariant", backref="order_items")
    tax = relationship("Tax", backref="order_items")
    order_return_items = relationship("OrderReturnItem", back_populates="order_item")


class Tax(Base):
    __tablename__ = "taxes"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    name = Column(String(100), nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)  # e.g., 16.00 for 16%
    is_inclusive = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="taxes")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)  # cash, card, mobile_money, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="payment_methods")
    payments = relationship("Payment", back_populates="payment_method")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    payment_method_id = Column(BigInteger, ForeignKey("payment_methods.id"), nullable=False)
    received_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    reference = Column(String(255), nullable=True)
    status = Column(String(50), default="completed")
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="payments")
    order = relationship("Order", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
    receiver = relationship("User", backref="received_payments", foreign_keys=[received_by])


class OrderReturn(Base):
    __tablename__ = "order_returns"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    processed_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    return_number = Column(String(100), nullable=False)
    reason = Column(Text, nullable=True)
    refund_total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="order_returns")
    order = relationship("Order", back_populates="order_returns")
    processor = relationship("User", backref="processed_returns", foreign_keys=[processed_by])
    order_return_items = relationship("OrderReturnItem", back_populates="order_return")


class OrderReturnItem(Base):
    __tablename__ = "order_return_items"

    id = Column(BigInteger, primary_key=True, index=True)
    order_return_id = Column(BigInteger, ForeignKey("order_returns.id"), nullable=False)
    order_item_id = Column(BigInteger, ForeignKey("order_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    refund_amount = Column(Numeric(10, 2), nullable=False)
    restock = Column(Boolean, default=True)

    # Relationships
    order_return = relationship("OrderReturn", back_populates="order_return_items")
    order_item = relationship("OrderItem", back_populates="order_return_items")
