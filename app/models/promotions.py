import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, Date, ForeignKey, Integer, Boolean, Numeric, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # percentage, fixed_amount, buy_x_get_y
    value = Column(Numeric(10, 2), nullable=True)  # discount percentage or amount
    buy_quantity = Column(Integer, nullable=True)  # for buy X get Y
    get_quantity = Column(Integer, nullable=True)  # for buy X get Y
    applies_to = Column(String(50), nullable=False)  # order, product, category, brand
    min_order_amount = Column(Numeric(10, 2), nullable=True)
    max_discount_amount = Column(Numeric(10, 2), nullable=True)
    requires_code = Column(Boolean, default=False)
    is_stackable = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    usage_limit = Column(Integer, nullable=True)
    usage_limit_per_customer = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="draft")  # draft, scheduled, active, paused, expired
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="promotions")
    creator = relationship("User", backref="created_promotions")
    windows = relationship("PromotionWindow", back_populates="promotion")
    targets = relationship("PromotionTarget", back_populates="promotion")
    stores = relationship("PromotionStore", back_populates="promotion")
    coupons = relationship("Coupon", back_populates="promotion")
    order_promotions = relationship("OrderPromotion", back_populates="promotion")


class PromotionWindow(Base):
    __tablename__ = "promotion_windows"

    id = Column(BigInteger, primary_key=True, index=True)
    promotion_id = Column(BigInteger, ForeignKey("promotions.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6 (Sunday-Saturday)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationships
    promotion = relationship("Promotion", back_populates="windows")


class PromotionTarget(Base):
    __tablename__ = "promotion_targets"

    id = Column(BigInteger, primary_key=True, index=True)
    promotion_id = Column(BigInteger, ForeignKey("promotions.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=True)
    variant_id = Column(BigInteger, ForeignKey("product_variants.id"), nullable=True)
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True)
    brand_id = Column(BigInteger, ForeignKey("brands.id"), nullable=True)

    # Relationships
    promotion = relationship("Promotion", back_populates="targets")
    product = relationship("Product", backref="promotion_targets")
    variant = relationship("ProductVariant", backref="promotion_targets")
    category = relationship("Category", backref="promotion_targets")
    brand = relationship("Brand", backref="promotion_targets")


class PromotionStore(Base):
    __tablename__ = "promotion_stores"

    id = Column(BigInteger, primary_key=True, index=True)
    promotion_id = Column(BigInteger, ForeignKey("promotions.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)

    # Relationships
    promotion = relationship("Promotion", back_populates="stores")
    store = relationship("Store", backref="promotion_stores")


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    promotion_id = Column(BigInteger, ForeignKey("promotions.id"), nullable=False)
    customer_id = Column(BigInteger, ForeignKey("customer.id"), nullable=True)
    code = Column(String(100), nullable=False)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="coupons")
    promotion = relationship("Promotion", back_populates="coupons")
    customer = relationship("Customer", backref="coupons")
    order_promotions = relationship("OrderPromotion", back_populates="coupon")


class OrderPromotion(Base):
    __tablename__ = "order_promotions"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    order_item_id = Column(BigInteger, ForeignKey("order_items.id"), nullable=True)
    promotion_id = Column(BigInteger, ForeignKey("promotions.id"), nullable=False)
    coupon_id = Column(BigInteger, ForeignKey("coupons.id"), nullable=True)
    discount_amount = Column(Numeric(10, 2), nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="order_promotions")
    order = relationship("Order", backref="order_promotions")
    order_item = relationship("OrderItem", backref="order_promotions")
    promotion = relationship("Promotion", back_populates="order_promotions")
    coupon = relationship("Coupon", back_populates="order_promotions")
