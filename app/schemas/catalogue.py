from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    status: str = "active"


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: str  # public_id
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Brand schemas
class BrandBase(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    status: str = "active"


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = None


class BrandResponse(BrandBase):
    id: str  # public_id
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Unit schemas
class UnitBase(BaseModel):
    name: str
    short_name: str
    allow_decimal: bool = False


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    allow_decimal: Optional[bool] = None


class UnitResponse(UnitBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Attribute schemas
class AttributeBase(BaseModel):
    name: str
    type: str  # colour, size, material, etc.
    sort_order: int = 0


class AttributeCreate(AttributeBase):
    pass


class AttributeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    sort_order: Optional[int] = None


class AttributeResponse(AttributeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Attribute Value schemas
class AttributeValueBase(BaseModel):
    attribute_id: int
    value: str
    hex_code: Optional[str] = None
    sort_order: int = 0


class AttributeValueCreate(AttributeValueBase):
    pass


class AttributeValueUpdate(BaseModel):
    value: Optional[str] = None
    hex_code: Optional[str] = None
    sort_order: Optional[int] = None


class AttributeValueResponse(AttributeValueBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Tag schemas
class TagBase(BaseModel):
    name: str
    slug: str


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class TagResponse(TagBase):
    id: str  # public_id
    created_at: datetime

    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    product_type: str = "simple"  # simple or variable
    status: str = "draft"  # draft, active, archived
    is_featured: bool = False


class ProductCreate(ProductBase):
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    product_type: Optional[str] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None


class ProductResponse(ProductBase):
    id: str  # public_id
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product Variant schemas
class ProductVariantBase(BaseModel):
    sku: str
    name: str
    price: Decimal
    cost_price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    is_default: bool = False
    status: str = "active"


class ProductVariantCreate(ProductVariantBase):
    barcode: Optional[str] = None


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    is_default: Optional[bool] = None
    status: Optional[str] = None


class ProductVariantResponse(ProductVariantBase):
    id: str  # public_id
    barcode: Optional[str] = None
    product_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Product Image schemas
class ProductImageBase(BaseModel):
    url: str
    alt_text: Optional[str] = None
    sort_order: int = 0
    is_primary: bool = False


class ProductImageCreate(ProductImageBase):
    variant_id: Optional[int] = None


class ProductImageUpdate(BaseModel):
    url: Optional[str] = None
    alt_text: Optional[str] = None
    sort_order: Optional[int] = None
    is_primary: Optional[bool] = None
    variant_id: Optional[int] = None


class ProductImageResponse(ProductImageBase):
    id: str  # public_id
    product_id: int
    variant_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
