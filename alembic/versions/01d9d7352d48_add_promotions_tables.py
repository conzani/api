"""add_promotions_tables

Revision ID: 01d9d7352d48
Revises: ee400705a3fd
Create Date: 2026-10-13 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01d9d7352d48'
down_revision = 'ee400705a3fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create promotions table
    op.create_table(
        'promotions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('value', sa.Numeric(10, 2), nullable=True),
        sa.Column('buy_quantity', sa.Integer(), nullable=True),
        sa.Column('get_quantity', sa.Integer(), nullable=True),
        sa.Column('applies_to', sa.String(50), nullable=False),
        sa.Column('min_order_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('max_discount_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('requires_code', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('is_stackable', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('usage_limit_per_customer', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promotions_id'), 'promotions', ['id'], unique=False)
    op.create_index(op.f('ix_promotions_public_id'), 'promotions', ['public_id'], unique=True)
    op.create_index(op.f('ix_promotions_business_id'), 'promotions', ['business_id'], unique=False)

    # Create promotion_windows table
    op.create_table(
        'promotion_windows',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('promotion_id', sa.BigInteger(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promotion_windows_id'), 'promotion_windows', ['id'], unique=False)
    op.create_index(op.f('ix_promotion_windows_promotion_id'), 'promotion_windows', ['promotion_id'], unique=False)

    # Create promotion_targets table
    op.create_table(
        'promotion_targets',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('promotion_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=True),
        sa.Column('variant_id', sa.BigInteger(), nullable=True),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('brand_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promotion_targets_id'), 'promotion_targets', ['id'], unique=False)
    op.create_index(op.f('ix_promotion_targets_promotion_id'), 'promotion_targets', ['promotion_id'], unique=False)
    op.create_index(op.f('ix_promotion_targets_product_id'), 'promotion_targets', ['product_id'], unique=False)
    op.create_index(op.f('ix_promotion_targets_variant_id'), 'promotion_targets', ['variant_id'], unique=False)
    op.create_index(op.f('ix_promotion_targets_category_id'), 'promotion_targets', ['category_id'], unique=False)
    op.create_index(op.f('ix_promotion_targets_brand_id'), 'promotion_targets', ['brand_id'], unique=False)

    # Create promotion_stores table
    op.create_table(
        'promotion_stores',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('promotion_id', sa.BigInteger(), nullable=False),
        sa.Column('store_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], ),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_promotion_stores_id'), 'promotion_stores', ['id'], unique=False)
    op.create_index(op.f('ix_promotion_stores_promotion_id'), 'promotion_stores', ['promotion_id'], unique=False)
    op.create_index(op.f('ix_promotion_stores_store_id'), 'promotion_stores', ['store_id'], unique=False)

    # Create coupons table
    op.create_table(
        'coupons',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('promotion_id', sa.BigInteger(), nullable=False),
        sa.Column('customer_id', sa.BigInteger(), nullable=True),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupons_id'), 'coupons', ['id'], unique=False)
    op.create_index(op.f('ix_coupons_public_id'), 'coupons', ['public_id'], unique=True)
    op.create_index(op.f('ix_coupons_business_id'), 'coupons', ['business_id'], unique=False)
    op.create_index(op.f('ix_coupons_code'), 'coupons', ['code'], unique=False)

    # Create order_promotions table
    op.create_table(
        'order_promotions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('order_item_id', sa.BigInteger(), nullable=True),
        sa.Column('promotion_id', sa.BigInteger(), nullable=False),
        sa.Column('coupon_id', sa.BigInteger(), nullable=True),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id'], ),
        sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], ),
        sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_promotions_id'), 'order_promotions', ['id'], unique=False)
    op.create_index(op.f('ix_order_promotions_business_id'), 'order_promotions', ['business_id'], unique=False)
    op.create_index(op.f('ix_order_promotions_order_id'), 'order_promotions', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_promotions_order_item_id'), 'order_promotions', ['order_item_id'], unique=False)
    op.create_index(op.f('ix_order_promotions_promotion_id'), 'order_promotions', ['promotion_id'], unique=False)
    op.create_index(op.f('ix_order_promotions_coupon_id'), 'order_promotions', ['coupon_id'], unique=False)


def downgrade() -> None:
    # Drop in reverse order of creation
    op.drop_table('order_promotions')
    op.drop_table('coupons')
    op.drop_table('promotion_stores')
    op.drop_table('promotion_targets')
    op.drop_table('promotion_windows')
    op.drop_table('promotions')
