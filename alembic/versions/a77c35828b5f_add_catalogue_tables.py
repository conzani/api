"""add_catalogue_tables

Revision ID: a77c35828b5f
Revises: 1fff9df9846f
Create Date: 2026-10-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a77c35828b5f'
down_revision = '1fff9df9846f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_public_id'), 'categories', ['public_id'], unique=True)
    op.create_index(op.f('ix_categories_business_id_slug'), 'categories', ['business_id', 'slug'], unique=True)
    op.create_index(op.f('ix_categories_business_id'), 'categories', ['business_id'], unique=False)

    # Create brands table
    op.create_table(
        'brands',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_brands_id'), 'brands', ['id'], unique=False)
    op.create_index(op.f('ix_brands_public_id'), 'brands', ['public_id'], unique=True)
    op.create_index(op.f('ix_brands_business_id_slug'), 'brands', ['business_id', 'slug'], unique=True)
    op.create_index(op.f('ix_brands_business_id'), 'brands', ['business_id'], unique=False)

    # Create units table
    op.create_table(
        'units',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('short_name', sa.String(20), nullable=False),
        sa.Column('allow_decimal', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_units_id'), 'units', ['id'], unique=False)
    op.create_index(op.f('ix_units_business_id'), 'units', ['business_id'], unique=False)

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('brand_id', sa.BigInteger(), nullable=True),
        sa.Column('unit_id', sa.BigInteger(), nullable=True),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('product_type', sa.String(50), nullable=True, server_default='simple'),
        sa.Column('status', sa.String(50), nullable=True, server_default='draft'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_public_id'), 'products', ['public_id'], unique=True)
    op.create_index(op.f('ix_products_business_id_slug'), 'products', ['business_id', 'slug'], unique=True)
    op.create_index(op.f('ix_products_business_id'), 'products', ['business_id'], unique=False)
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)
    op.create_index(op.f('ix_products_brand_id'), 'products', ['brand_id'], unique=False)

    # Create product_variants table
    op.create_table(
        'product_variants',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False),
        sa.Column('barcode', sa.String(100), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('cost_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('compare_at_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('weight', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_variants_id'), 'product_variants', ['id'], unique=False)
    op.create_index(op.f('ix_product_variants_public_id'), 'product_variants', ['public_id'], unique=True)
    op.create_index(op.f('ix_product_variants_business_id_sku'), 'product_variants', ['business_id', 'sku'], unique=True)
    op.create_index(op.f('ix_product_variants_business_id'), 'product_variants', ['business_id'], unique=False)
    op.create_index(op.f('ix_product_variants_product_id'), 'product_variants', ['product_id'], unique=False)

    # Create product_images table
    op.create_table(
        'product_images',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('variant_id', sa.BigInteger(), nullable=True),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('alt_text', sa.String(255), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_primary', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_images_id'), 'product_images', ['id'], unique=False)
    op.create_index(op.f('ix_product_images_public_id'), 'product_images', ['public_id'], unique=True)
    op.create_index(op.f('ix_product_images_business_id'), 'product_images', ['business_id'], unique=False)
    op.create_index(op.f('ix_product_images_product_id'), 'product_images', ['product_id'], unique=False)
    op.create_index(op.f('ix_product_images_variant_id'), 'product_images', ['variant_id'], unique=False)

    # Create attributes table
    op.create_table(
        'attributes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attributes_id'), 'attributes', ['id'], unique=False)
    op.create_index(op.f('ix_attributes_business_id'), 'attributes', ['business_id'], unique=False)

    # Create attribute_values table
    op.create_table(
        'attribute_values',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('attribute_id', sa.BigInteger(), nullable=False),
        sa.Column('value', sa.String(100), nullable=False),
        sa.Column('hex_code', sa.String(7), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['attribute_id'], ['attributes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attribute_values_id'), 'attribute_values', ['id'], unique=False)
    op.create_index(op.f('ix_attribute_values_business_id'), 'attribute_values', ['business_id'], unique=False)
    op.create_index(op.f('ix_attribute_values_attribute_id'), 'attribute_values', ['attribute_id'], unique=False)

    # Create variant_attribute_values join table
    op.create_table(
        'variant_attribute_values',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('variant_id', sa.BigInteger(), nullable=False),
        sa.Column('attribute_value_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ),
        sa.ForeignKeyConstraint(['attribute_value_id'], ['attribute_values.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_variant_attribute_values_variant_id'), 'variant_attribute_values', ['variant_id'], unique=False)
    op.create_index(op.f('ix_variant_attribute_values_attribute_value_id'), 'variant_attribute_values', ['attribute_value_id'], unique=False)

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.create_index(op.f('ix_tags_public_id'), 'tags', ['public_id'], unique=True)
    op.create_index(op.f('ix_tags_business_id_slug'), 'tags', ['business_id', 'slug'], unique=True)
    op.create_index(op.f('ix_tags_business_id'), 'tags', ['business_id'], unique=False)

    # Create product_tags join table
    op.create_table(
        'product_tags',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('tag_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_tags_product_id'), 'product_tags', ['product_id'], unique=False)
    op.create_index(op.f('ix_product_tags_tag_id'), 'product_tags', ['tag_id'], unique=False)


def downgrade() -> None:
    # Drop in reverse order of creation
    op.drop_table('product_tags')
    op.drop_table('tags')
    op.drop_table('variant_attribute_values')
    op.drop_table('attribute_values')
    op.drop_table('attributes')
    op.drop_table('product_images')
    op.drop_table('product_variants')
    op.drop_table('products')
    op.drop_table('units')
    op.drop_table('brands')
    op.drop_table('categories')
