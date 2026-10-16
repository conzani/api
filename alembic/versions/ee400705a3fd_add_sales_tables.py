"""add_sales_tables

Revision ID: ee400705a3fd
Revises: a77c35828b5f
Create Date: 2026-10-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee400705a3fd'
down_revision = 'a77c35828b5f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create stores table
    op.create_table(
        'stores',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('address_id', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(50), nullable=True, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['address_id'], ['address.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stores_id'), 'stores', ['id'], unique=False)
    op.create_index(op.f('ix_stores_public_id'), 'stores', ['public_id'], unique=True)
    op.create_index(op.f('ix_stores_business_id'), 'stores', ['business_id'], unique=False)

    # Create taxes table
    op.create_table(
        'taxes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('rate', sa.Numeric(5, 2), nullable=False),
        sa.Column('is_inclusive', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_taxes_id'), 'taxes', ['id'], unique=False)
    op.create_index(op.f('ix_taxes_business_id'), 'taxes', ['business_id'], unique=False)

    # Create payment_methods table
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_methods_id'), 'payment_methods', ['id'], unique=False)
    op.create_index(op.f('ix_payment_methods_business_id'), 'payment_methods', ['business_id'], unique=False)

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('store_id', sa.BigInteger(), nullable=True),
        sa.Column('customer_id', sa.BigInteger(), nullable=True),
        sa.Column('served_by', sa.BigInteger(), nullable=True),
        sa.Column('order_number', sa.String(100), nullable=False),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='draft'),
        sa.Column('payment_status', sa.String(50), nullable=True, server_default='unpaid'),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_total', sa.Numeric(10, 2), nullable=True, server_default='0'),
        sa.Column('tax_total', sa.Numeric(10, 2), nullable=True, server_default='0'),
        sa.Column('grand_total', sa.Numeric(10, 2), nullable=False),
        sa.Column('amount_paid', sa.Numeric(10, 2), nullable=True, server_default='0'),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('ordered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
        sa.ForeignKeyConstraint(['served_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_public_id'), 'orders', ['public_id'], unique=True)
    op.create_index(op.f('ix_orders_business_id_order_number'), 'orders', ['business_id', 'order_number'], unique=True)
    op.create_index(op.f('ix_orders_business_id'), 'orders', ['business_id'], unique=False)
    op.create_index(op.f('ix_orders_store_id'), 'orders', ['store_id'], unique=False)
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=True),
        sa.Column('variant_id', sa.BigInteger(), nullable=True),
        sa.Column('tax_id', sa.BigInteger(), nullable=True),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('cost_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=True, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=True, server_default='0'),
        sa.Column('line_total', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], ),
        sa.ForeignKeyConstraint(['tax_id'], ['taxes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)
    op.create_index(op.f('ix_order_items_business_id'), 'order_items', ['business_id'], unique=False)
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)
    op.create_index(op.f('ix_order_items_variant_id'), 'order_items', ['variant_id'], unique=False)

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('payment_method_id', sa.BigInteger(), nullable=False),
        sa.Column('received_by', sa.BigInteger(), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('reference', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, server_default='completed'),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ),
        sa.ForeignKeyConstraint(['received_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_public_id'), 'payments', ['public_id'], unique=True)
    op.create_index(op.f('ix_payments_business_id'), 'payments', ['business_id'], unique=False)
    op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=False)
    op.create_index(op.f('ix_payments_payment_method_id'), 'payments', ['payment_method_id'], unique=False)

    # Create order_returns table
    op.create_table(
        'order_returns',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('business_id', sa.BigInteger(), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('processed_by', sa.BigInteger(), nullable=True),
        sa.Column('return_number', sa.String(100), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('refund_total', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_returns_id'), 'order_returns', ['id'], unique=False)
    op.create_index(op.f('ix_order_returns_public_id'), 'order_returns', ['public_id'], unique=True)
    op.create_index(op.f('ix_order_returns_business_id'), 'order_returns', ['business_id'], unique=False)
    op.create_index(op.f('ix_order_returns_order_id'), 'order_returns', ['order_id'], unique=False)

    # Create order_return_items join table
    op.create_table(
        'order_return_items',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('order_return_id', sa.BigInteger(), nullable=False),
        sa.Column('order_item_id', sa.BigInteger(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('refund_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('restock', sa.Boolean(), nullable=True, server_default='1'),
        sa.ForeignKeyConstraint(['order_return_id'], ['order_returns.id'], ),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_return_items_order_return_id'), 'order_return_items', ['order_return_id'], unique=False)
    op.create_index(op.f('ix_order_return_items_order_item_id'), 'order_return_items', ['order_item_id'], unique=False)


def downgrade() -> None:
    # Drop in reverse order of creation
    op.drop_table('order_return_items')
    op.drop_table('order_returns')
    op.drop_table('payments')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('payment_methods')
    op.drop_table('taxes')
    op.drop_table('stores')
