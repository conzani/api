import secrets
from sqlalchemy import Column, BigInteger, String, DateTime, Date, ForeignKey, Integer, Boolean, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)


class Category(Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="categories")
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    logo_url = Column(String(500), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="brands")
    products = relationship("Product", back_populates="brand")


class Unit(Base):
    __tablename__ = "units"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    name = Column(String(100), nullable=False)
    short_name = Column(String(20), nullable=False)
    allow_decimal = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="units")
    products = relationship("Product", back_populates="unit")


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id"), nullable=True)
    brand_id = Column(BigInteger, ForeignKey("brands.id"), nullable=True)
    unit_id = Column(BigInteger, ForeignKey("units.id"), nullable=True)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    product_type = Column(String(50), default="simple")  # simple or variable
    status = Column(String(50), default="draft")  # draft, active, archived
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="products")
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    creator = relationship("User", backref="created_products")
    variants = relationship("ProductVariant", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    tags = relationship("Tag", secondary="product_tags", back_populates="products")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    sku = Column(String(100), nullable=False)
    barcode = Column(String(100), nullable=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=True)
    compare_at_price = Column(Numeric(10, 2), nullable=True)
    weight = Column(Numeric(10, 2), nullable=True)
    is_default = Column(Boolean, default=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    business = relationship("Business", backref="product_variants")
    product = relationship("Product", back_populates="variants")
    images = relationship("ProductImage", back_populates="variant")
    attribute_values = relationship("AttributeValue", secondary="variant_attribute_values", back_populates="variants")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    variant_id = Column(BigInteger, ForeignKey("product_variants.id"), nullable=True)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="product_images")
    product = relationship("Product", back_populates="images")
    variant = relationship("ProductVariant", back_populates="images")


class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # colour, size, material, etc.
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", backref="attributes")
    values = relationship("AttributeValue", back_populates="attribute")


class AttributeValue(Base):
    __tablename__ = "attribute_values"

    id = Column(BigInteger, primary_key=True, index=True)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    attribute_id = Column(BigInteger, ForeignKey("attributes.id"), nullable=False)
    value = Column(String(100), nullable=False)
    hex_code = Column(String(7), nullable=True)  # for colour swatches
    sort_order = Column(Integer, default=0)

    # Relationships
    business = relationship("Business", backref="attribute_values")
    attribute = relationship("Attribute", back_populates="values")
    variants = relationship("ProductVariant", secondary="variant_attribute_values", back_populates="attribute_values")


class VariantAttributeValue(Base):
    __tablename__ = "variant_attribute_values"

    id = Column(BigInteger, primary_key=True, index=True)
    variant_id = Column(BigInteger, ForeignKey("product_variants.id"), nullable=False)
    attribute_value_id = Column(BigInteger, ForeignKey("attribute_values.id"), nullable=False)

    # Relationships
    variant = relationship("ProductVariant", backref="variant_attribute_values")
    attribute_value = relationship("AttributeValue", backref="variant_attribute_values")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True, index=True)
    public_id = Column(String(16), unique=True, index=True, default=generate_public_id)
    business_id = Column(BigInteger, ForeignKey("business.id"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False)

    # Relationships
    business = relationship("Business", backref="tags")
    products = relationship("Product", secondary="product_tags", back_populates="tags")


class ProductTag(Base):
    __tablename__ = "product_tags"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    tag_id = Column(BigInteger, ForeignKey("tags.id"), nullable=False)

    # Relationships
    product = relationship("Product", backref="product_tags")
    tag = relationship("Tag", backref="product_tags")
