from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.schemas.catalogue import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse,
    ProductImageCreate, ProductImageUpdate, ProductImageResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    BrandCreate, BrandUpdate, BrandResponse,
    UnitCreate, UnitUpdate, UnitResponse,
    AttributeCreate, AttributeUpdate, AttributeResponse,
    AttributeValueCreate, AttributeValueUpdate, AttributeValueResponse,
    TagCreate, TagUpdate, TagResponse
)
from app.models.catalogue import (
    Product, ProductVariant, ProductImage,
    Category, Brand, Unit,
    Attribute, AttributeValue,
    Tag, ProductTag
)
from app.core.security import generate_public_id
from app.core.cache_manager import cache_manager
from app.core.rate_limiter import check_rate_limit
from app.core.config import settings

router = APIRouter(prefix="/catalogue", tags=["Catalogue"])


def catalogue_rate_limit(request: Request):
    """Rate limit for catalogue endpoints."""
    return check_rate_limit(request, limit=settings.GLOBAL_RATE_LIMIT, window=settings.GLOBAL_RATE_WINDOW)


# Category endpoints
@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    new_category = Category(
        public_id=generate_public_id(),
        **category.model_dump()
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    # Invalidate cache for this business
    cache_manager.invalidate_category_cache(new_category.business_id)
    cache_manager.delete_pattern("categories_all:*")
    
    return CategoryResponse(
        id=new_category.public_id,
        name=new_category.name,
        slug=new_category.slug,
        description=new_category.description,
        image_url=new_category.image_url,
        sort_order=new_category.sort_order,
        status=new_category.status,
        parent_id=new_category.parent_id,
        created_at=new_category.created_at,
        updated_at=new_category.updated_at,
        deleted_at=new_category.deleted_at,
    )


@router.get("/categories/", response_model=List[CategoryResponse], dependencies=[Depends(catalogue_rate_limit)])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all categories with pagination."""
    # Try to get from cache first
    from app.core.cache_manager import cache_manager
    cache_key = f"categories_all:{skip}:{limit}"
    cached = cache_manager.get(cache_key)
    if cached:
        return cached
    
    categories = db.query(Category).offset(skip).limit(limit).all()
    result = [
        CategoryResponse(
            id=cat.public_id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            image_url=cat.image_url,
            sort_order=cat.sort_order,
            status=cat.status,
            parent_id=cat.parent_id,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
            deleted_at=cat.deleted_at,
        )
        for cat in categories
    ]
    
    # Cache for 5 minutes
    cache_manager.set(cache_key, result, ttl=300)
    return result


@router.get("/categories/{id}", response_model=CategoryResponse, dependencies=[Depends(catalogue_rate_limit)])
def get_category(id: str, db: Session = Depends(get_db)):
    """Get a category by public_id."""
    # Try to get from cache
    cached_category = cache_manager.get_category(id)
    if cached_category:
        return CategoryResponse(**cached_category)
    
    category = db.query(Category).filter(Category.public_id == id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category_response = CategoryResponse(
        id=category.public_id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        image_url=category.image_url,
        sort_order=category.sort_order,
        status=category.status,
        parent_id=category.parent_id,
        created_at=category.created_at,
        updated_at=category.updated_at,
        deleted_at=category.deleted_at,
    )
    
    # Cache the result
    cache_manager.set_category(id, category_response.model_dump(), category.business_id)
    
    return category_response


@router.put("/categories/{id}", response_model=CategoryResponse)
def update_category(id: str, category_update: CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category."""
    category = db.query(Category).filter(Category.public_id == id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    
    # Invalidate cache for this business
    from app.core.cache_manager import cache_manager
    cache_manager.invalidate_category_cache(category.business_id)
    cache_manager.delete_pattern("categories_all:*")
    
    return CategoryResponse(
        id=category.public_id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        image_url=category.image_url,
        sort_order=category.sort_order,
        status=category.status,
        parent_id=category.parent_id,
        created_at=category.created_at,
        updated_at=category.updated_at,
        deleted_at=category.deleted_at,
    )


@router.delete("/categories/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(id: str, db: Session = Depends(get_db)):
    """Soft delete a category."""
    from datetime import datetime
    category = db.query(Category).filter(Category.public_id == id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    category.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None


# Brand endpoints
@router.post("/brands/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    """Create a new brand."""
    new_brand = Brand(
        public_id=generate_public_id(),
        **brand.model_dump()
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    # Invalidate cache for this business
    cache_manager.invalidate_brand_cache(new_brand.business_id)
    
    return BrandResponse(
        id=new_brand.public_id,
        name=new_brand.name,
        slug=new_brand.slug,
        logo_url=new_brand.logo_url,
        status=new_brand.status,
        created_at=new_brand.created_at,
        updated_at=new_brand.updated_at,
        deleted_at=new_brand.deleted_at,
    )


@router.get("/brands/", response_model=List[BrandResponse], dependencies=[Depends(catalogue_rate_limit)])
def get_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all brands with pagination."""
    # Try to get from cache (note: for simplicity, we'll skip list caching for now)
    brands = db.query(Brand).offset(skip).limit(limit).all()
    return [
        BrandResponse(
            id=brand.public_id,
            name=brand.name,
            slug=brand.slug,
            logo_url=brand.logo_url,
            status=brand.status,
            created_at=brand.created_at,
            updated_at=brand.updated_at,
            deleted_at=brand.deleted_at,
        )
        for brand in brands
    ]


@router.get("/brands/{id}", response_model=BrandResponse, dependencies=[Depends(catalogue_rate_limit)])
def get_brand(id: str, db: Session = Depends(get_db)):
    """Get a brand by public_id."""
    # Try to get from cache
    cached_brand = cache_manager.get_brand(id)
    if cached_brand:
        return BrandResponse(**cached_brand)
    
    brand = db.query(Brand).filter(Brand.public_id == id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    brand_response = BrandResponse(
        id=brand.public_id,
        name=brand.name,
        slug=brand.slug,
        logo_url=brand.logo_url,
        status=brand.status,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        deleted_at=brand.deleted_at,
    )
    
    # Cache the result
    cache_manager.set_brand(id, brand_response.model_dump(), brand.business_id)
    
    return brand_response


@router.put("/brands/{id}", response_model=BrandResponse)
def update_brand(id: str, brand_update: BrandUpdate, db: Session = Depends(get_db)):
    """Update a brand."""
    brand = db.query(Brand).filter(Brand.public_id == id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    update_data = brand_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)

    db.commit()
    db.refresh(brand)
    
    # Invalidate cache for this business
    cache_manager.invalidate_brand_cache(brand.business_id)
    
    return BrandResponse(
        id=brand.public_id,
        name=brand.name,
        slug=brand.slug,
        logo_url=brand.logo_url,
        status=brand.status,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        deleted_at=brand.deleted_at,
    )


@router.delete("/brands/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(id: str, db: Session = Depends(get_db)):
    """Soft delete a brand."""
    from datetime import datetime
    brand = db.query(Brand).filter(Brand.public_id == id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )

    brand.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    # Invalidate cache for this business
    cache_manager.invalidate_brand_cache(brand.business_id)

    return None


# Unit endpoints
@router.post("/units/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(unit: UnitCreate, db: Session = Depends(get_db)):
    """Create a new unit."""
    new_unit = Unit(**unit.model_dump())
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


@router.get("/units/", response_model=List[UnitResponse])
def get_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all units with pagination."""
    units = db.query(Unit).offset(skip).limit(limit).all()
    return units


@router.get("/units/{id}", response_model=UnitResponse)
def get_unit(id: int, db: Session = Depends(get_db)):
    """Get a unit by ID."""
    unit = db.query(Unit).filter(Unit.id == id).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    return unit


@router.put("/units/{id}", response_model=UnitResponse)
def update_unit(id: int, unit_update: UnitUpdate, db: Session = Depends(get_db)):
    """Update a unit."""
    unit = db.query(Unit).filter(Unit.id == id).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )

    update_data = unit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(unit, field, value)

    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/units/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(id: int, db: Session = Depends(get_db)):
    """Delete a unit."""
    unit = db.query(Unit).filter(Unit.id == id).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )

    db.delete(unit)
    db.commit()

    return None


# Attribute endpoints
@router.post("/attributes/", response_model=AttributeResponse, status_code=status.HTTP_201_CREATED)
def create_attribute(attribute: AttributeCreate, db: Session = Depends(get_db)):
    """Create a new attribute."""
    new_attribute = Attribute(**attribute.model_dump())
    db.add(new_attribute)
    db.commit()
    db.refresh(new_attribute)
    return new_attribute


@router.get("/attributes/", response_model=List[AttributeResponse])
def get_attributes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all attributes with pagination."""
    attributes = db.query(Attribute).offset(skip).limit(limit).all()
    return attributes


@router.get("/attributes/{id}", response_model=AttributeResponse)
def get_attribute(id: int, db: Session = Depends(get_db)):
    """Get an attribute by ID."""
    attribute = db.query(Attribute).filter(Attribute.id == id).first()
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute not found"
        )
    return attribute


@router.put("/attributes/{id}", response_model=AttributeResponse)
def update_attribute(id: int, attribute_update: AttributeUpdate, db: Session = Depends(get_db)):
    """Update an attribute."""
    attribute = db.query(Attribute).filter(Attribute.id == id).first()
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute not found"
        )

    update_data = attribute_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attribute, field, value)

    db.commit()
    db.refresh(attribute)
    return attribute


@router.delete("/attributes/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attribute(id: int, db: Session = Depends(get_db)):
    """Delete an attribute."""
    attribute = db.query(Attribute).filter(Attribute.id == id).first()
    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute not found"
        )

    db.delete(attribute)
    db.commit()

    return None


# Attribute Value endpoints
@router.post("/attributes/{attribute_id}/values/", response_model=AttributeValueResponse, status_code=status.HTTP_201_CREATED)
def create_attribute_value(attribute_id: int, attribute_value: AttributeValueCreate, db: Session = Depends(get_db)):
    """Create a new attribute value."""
    new_value = AttributeValue(
        attribute_id=attribute_id,
        **attribute_value.model_dump()
    )
    db.add(new_value)
    db.commit()
    db.refresh(new_value)
    return new_value


@router.get("/attributes/{attribute_id}/values/", response_model=List[AttributeValueResponse])
def get_attribute_values(attribute_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all values for an attribute."""
    values = db.query(AttributeValue).filter(AttributeValue.attribute_id == attribute_id).offset(skip).limit(limit).all()
    return values


@router.get("/attributes/{attribute_id}/values/{id}", response_model=AttributeValueResponse)
def get_attribute_value(attribute_id: int, id: int, db: Session = Depends(get_db)):
    """Get an attribute value by ID."""
    value = db.query(AttributeValue).filter(
        AttributeValue.attribute_id == attribute_id,
        AttributeValue.id == id
    ).first()
    if not value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute value not found"
        )
    return value


@router.put("/attributes/{attribute_id}/values/{id}", response_model=AttributeValueResponse)
def update_attribute_value(attribute_id: int, id: int, attribute_value_update: AttributeValueUpdate, db: Session = Depends(get_db)):
    """Update an attribute value."""
    value = db.query(AttributeValue).filter(
        AttributeValue.attribute_id == attribute_id,
        AttributeValue.id == id
    ).first()
    if not value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute value not found"
        )

    update_data = attribute_value_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(value, field, value)

    db.commit()
    db.refresh(value)
    return value


@router.delete("/attributes/{attribute_id}/values/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attribute_value(attribute_id: int, id: int, db: Session = Depends(get_db)):
    """Delete an attribute value."""
    value = db.query(AttributeValue).filter(
        AttributeValue.attribute_id == attribute_id,
        AttributeValue.id == id
    ).first()
    if not value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attribute value not found"
        )

    db.delete(value)
    db.commit()

    return None


# Tag endpoints
@router.post("/tags/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    new_tag = Tag(
        public_id=generate_public_id(),
        **tag.model_dump()
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return TagResponse(
        id=new_tag.public_id,
        name=new_tag.name,
        slug=new_tag.slug,
        created_at=new_tag.created_at,
    )


@router.get("/tags/", response_model=List[TagResponse])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tags with pagination."""
    tags = db.query(Tag).offset(skip).limit(limit).all()
    return [
        TagResponse(
            id=tag.public_id,
            name=tag.name,
            slug=tag.slug,
            created_at=tag.created_at,
        )
        for tag in tags
    ]


@router.get("/tags/{id}", response_model=TagResponse)
def get_tag(id: str, db: Session = Depends(get_db)):
    """Get a tag by public_id."""
    tag = db.query(Tag).filter(Tag.public_id == id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return TagResponse(
        id=tag.public_id,
        name=tag.name,
        slug=tag.slug,
        created_at=tag.created_at,
    )


@router.put("/tags/{id}", response_model=TagResponse)
def update_tag(id: str, tag_update: TagUpdate, db: Session = Depends(get_db)):
    """Update a tag."""
    tag = db.query(Tag).filter(Tag.public_id == id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    update_data = tag_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    db.commit()
    db.refresh(tag)
    return TagResponse(
        id=tag.public_id,
        name=tag.name,
        slug=tag.slug,
        created_at=tag.created_at,
    )


@router.delete("/tags/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(id: str, db: Session = Depends(get_db)):
    """Delete a tag."""
    tag = db.query(Tag).filter(Tag.public_id == id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    db.delete(tag)
    db.commit()

    return None


# Product endpoints
@router.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    new_product = Product(
        public_id=generate_public_id(),
        **product.model_dump()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Invalidate cache for this business
    cache_manager.invalidate_product_cache(new_product.business_id)
    
    return ProductResponse(
        id=new_product.public_id,
        name=new_product.name,
        slug=new_product.slug,
        description=new_product.description,
        product_type=new_product.product_type,
        status=new_product.status,
        is_featured=new_product.is_featured,
        category_id=new_product.category_id,
        brand_id=new_product.brand_id,
        unit_id=new_product.unit_id,
        created_by=new_product.created_by,
        created_at=new_product.created_at,
        updated_at=new_product.updated_at,
        deleted_at=new_product.deleted_at,
    )


@router.get("/products/", response_model=List[ProductResponse], dependencies=[Depends(catalogue_rate_limit)])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all products with pagination."""
    products = db.query(Product).offset(skip).limit(limit).all()
    return [
        ProductResponse(
            id=product.public_id,
            name=product.name,
            slug=product.slug,
            description=product.description,
            product_type=product.product_type,
            status=product.status,
            is_featured=product.is_featured,
            category_id=product.category_id,
            brand_id=product.brand_id,
            unit_id=product.unit_id,
            created_by=product.created_by,
            created_at=product.created_at,
            updated_at=product.updated_at,
            deleted_at=product.deleted_at,
        )
        for product in products
    ]


@router.get("/products/{id}", response_model=ProductResponse, dependencies=[Depends(catalogue_rate_limit)])
def get_product(id: str, db: Session = Depends(get_db)):
    """Get a product by public_id."""
    # Try to get from cache
    cached_product = cache_manager.get_product(id)
    if cached_product:
        return ProductResponse(**cached_product)
    
    product = db.query(Product).filter(Product.public_id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product_response = ProductResponse(
        id=product.public_id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        product_type=product.product_type,
        status=product.status,
        is_featured=product.is_featured,
        category_id=product.category_id,
        brand_id=product.brand_id,
        unit_id=product.unit_id,
        created_by=product.created_by,
        created_at=product.created_at,
        updated_at=product.updated_at,
        deleted_at=product.deleted_at,
    )
    
    # Cache the result
    cache_manager.set_product(id, product_response.model_dump(), product.business_id)
    
    return product_response


@router.put("/products/{id}", response_model=ProductResponse)
def update_product(id: str, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product."""
    product = db.query(Product).filter(Product.public_id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    
    # Invalidate cache for this business
    cache_manager.invalidate_product_cache(product.business_id)
    
    return ProductResponse(
        id=product.public_id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        product_type=product.product_type,
        status=product.status,
        is_featured=product.is_featured,
        category_id=product.category_id,
        brand_id=product.brand_id,
        unit_id=product.unit_id,
        created_by=product.created_by,
        created_at=product.created_at,
        updated_at=product.updated_at,
        deleted_at=product.deleted_at,
    )


@router.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: str, db: Session = Depends(get_db)):
    """Soft delete a product."""
    from datetime import datetime
    product = db.query(Product).filter(Product.public_id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.deleted_at = datetime.now(timezone.utc)
    db.commit()
    
    # Invalidate cache for this business
    cache_manager.invalidate_product_cache(product.business_id)

    return None


# Product Variant endpoints
@router.post("/products/{product_id}/variants/", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
def create_product_variant(product_id: str, variant: ProductVariantCreate, db: Session = Depends(get_db)):
    """Create a new product variant."""
    # Find product by public_id
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    new_variant = ProductVariant(
        public_id=generate_public_id(),
        product_id=product.id,
        **variant.model_dump()
    )
    db.add(new_variant)
    db.commit()
    db.refresh(new_variant)
    return ProductVariantResponse(
        id=new_variant.public_id,
        sku=new_variant.sku,
        barcode=new_variant.barcode,
        name=new_variant.name,
        price=new_variant.price,
        cost_price=new_variant.cost_price,
        compare_at_price=new_variant.compare_at_price,
        weight=new_variant.weight,
        is_default=new_variant.is_default,
        status=new_variant.status,
        product_id=new_variant.product_id,
        created_at=new_variant.created_at,
        updated_at=new_variant.updated_at,
        deleted_at=new_variant.deleted_at,
    )


@router.get("/products/{product_id}/variants/", response_model=List[ProductVariantResponse])
def get_product_variants(product_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all variants for a product."""
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
    )

    variants = db.query(ProductVariant).filter(ProductVariant.product_id == product.id).offset(skip).limit(limit).all()
    return [
        ProductVariantResponse(
            id=variant.public_id,
            sku=variant.sku,
            barcode=variant.barcode,
            name=variant.name,
            price=variant.price,
            cost_price=variant.cost_price,
            compare_at_price=variant.compare_at_price,
            weight=variant.weight,
            is_default=variant.is_default,
            status=variant.status,
            product_id=variant.product_id,
            created_at=variant.created_at,
            updated_at=variant.updated_at,
            deleted_at=variant.deleted_at,
        )
        for variant in variants
    ]


@router.get("/products/{product_id}/variants/{id}", response_model=ProductVariantResponse)
def get_product_variant(product_id: str, id: str, db: Session = Depends(get_db)):
    """Get a product variant by public_id."""
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
    )

    variant = db.query(ProductVariant).filter(
        ProductVariant.product_id == product.id,
        ProductVariant.public_id == id
    ).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )
    return ProductVariantResponse(
        id=variant.public_id,
        sku=variant.sku,
        barcode=variant.barcode,
        name=variant.name,
        price=variant.price,
        cost_price=variant.cost_price,
        compare_at_price=variant.compare_at_price,
        weight=variant.weight,
        is_default=variant.is_default,
        status=variant.status,
        product_id=variant.product_id,
        created_at=variant.created_at,
        updated_at=variant.updated_at,
        deleted_at=variant.deleted_at,
    )


@router.put("/products/{product_id}/variants/{id}", response_model=ProductVariantResponse)
def update_product_variant(product_id: str, id: str, variant_update: ProductVariantUpdate, db: Session = Depends(get_db)):
    """Update a product variant."""
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    variant = db.query(ProductVariant).filter(
        ProductVariant.product_id == product.id,
        ProductVariant.public_id == id
    ).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )

    update_data = variant_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(variant, field, value)

    db.commit()
    db.refresh(variant)
    return ProductVariantResponse(
        id=variant.public_id,
        sku=variant.sku,
        barcode=variant.barcode,
        name=variant.name,
        price=variant.price,
        cost_price=variant.cost_price,
        compare_at_price=variant.compare_at_price,
        weight=variant.weight,
        is_default=variant.is_default,
        status=variant.status,
        product_id=variant.product_id,
        created_at=variant.created_at,
        updated_at=variant.updated_at,
        deleted_at=variant.deleted_at,
    )


@router.delete("/products/{product_id}/variants/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_variant(product_id: str, id: str, db: Session = Depends(get_db)):
    """Soft delete a product variant."""
    from datetime import datetime
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    variant = db.query(ProductVariant).filter(
        ProductVariant.product_id == product.id,
        ProductVariant.public_id == id
    ).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )

    variant.deleted_at = datetime.now(timezone.utc)
    db.commit()

    return None


# Product Image endpoints
@router.post("/products/{product_id}/images/", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
def create_product_image(product_id: str, image: ProductImageCreate, db: Session = Depends(get_db)):
    """Create a new product image."""
    # Find product by public_id
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    new_image = ProductImage(
        public_id=generate_public_id(),
        product_id=product.id,
        **image.model_dump()
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return ProductImageResponse(
        id=new_image.public_id,
        url=new_image.url,
        alt_text=new_image.alt_text,
        sort_order=new_image.sort_order,
        is_primary=new_image.is_primary,
        product_id=new_image.product_id,
        variant_id=new_image.variant_id,
        created_at=new_image.created_at,
    )


@router.get("/products/{product_id}/images/", response_model=List[ProductImageResponse])
def get_product_images(product_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all images for a product."""
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    images = db.query(ProductImage).filter(ProductImage.product_id == product.id).offset(skip).limit(limit).all()
    return [
        ProductImageResponse(
            id=image.public_id,
            url=image.url,
            alt_text=image.alt_text,
            sort_order=image.sort_order,
            is_primary=image.is_primary,
            product_id=image.product_id,
            variant_id=image.variant_id,
            created_at=image.created_at,
        )
        for image in images
    ]


@router.get("/products/{product_id}/images/{id}", response_model=ProductImageResponse)
def get_product_image(product_id: str, id: str, db: Session = Depends(get_db)):
    """Get a product image by public_id."""
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    image = db.query(ProductImage).filter(
        ProductImage.product_id == product.id,
        ProductImage.public_id == id
    ).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    return ProductImageResponse(
        id=image.public_id,
        url=image.url,
        alt_text=image.alt_text,
        sort_order=image.sort_order,
        is_primary=image.is_primary,
        product_id=image.product_id,
        variant_id=image.variant_id,
        created_at=image.created_at,
    )


@router.put("/products/{product_id}/images/{id}", response_model=ProductImageResponse)
def update_product_image(product_id: str, id: str, image_update: ProductImageUpdate, db: Session = Depends(get_db)):
    """Update a product image."""
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    image = db.query(ProductImage).filter(
        ProductImage.product_id == product.id,
        ProductImage.public_id == id
    ).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    update_data = image_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(image, field, value)

    db.commit()
    db.refresh(image)
    return ProductImageResponse(
        id=image.public_id,
        url=image.url,
        alt_text=image.alt_text,
        sort_order=image.sort_order,
        is_primary=image.is_primary,
        product_id=image.product_id,
        variant_id=image.variant_id,
        created_at=image.created_at,
    )


@router.delete("/products/{product_id}/images/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(product_id: str, id: str, db: Session = Depends(get_db)):
    """Delete a product image."""
    product = db.query(Product).filter(Product.public_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    image = db.query(ProductImage).filter(
        ProductImage.product_id == product.id,
        ProductImage.public_id == id
    ).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    db.delete(image)
    db.commit()

    return None
