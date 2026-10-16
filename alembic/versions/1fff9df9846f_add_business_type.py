"""add_business_type

Revision ID: 1fff9df9846f
Revises: fa4c5c1fe0b4
Create Date: 2026-10-13 13:48:46.912962

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
import sys
from pathlib import Path
import secrets

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.models.businesses import BusinessType

# revision identifiers, used by Alembic.
revision = '1fff9df9846f'
down_revision = 'fa4c5c1fe0b4'
branch_labels = None
depends_on = None


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)


def upgrade() -> None:
    # Create business_type table
    op.create_table(
        'business_type',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('public_id', sa.String(16), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_type_id'), 'business_type', ['id'], unique=False)
    op.create_index(op.f('ix_business_type_public_id'), 'business_type', ['public_id'], unique=True)
    op.create_index(op.f('ix_business_type_code'), 'business_type', ['code'], unique=True)

    # Add business_type_id column to business table (after address_id, before name)
    op.add_column('business', sa.Column('business_type_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_business_business_type_id', 'business', 'business_type', ['business_type_id'], ['id'])

    # Seed business types
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        business_types = [
            {
                "code": "retail",
                "name": "Retail",
                "description": "Retail business selling goods directly to consumers"
            },
            {
                "code": "wholesale",
                "name": "Wholesale",
                "description": "Wholesale business selling goods in bulk to retailers"
            },
            {
                "code": "service",
                "name": "Service",
                "description": "Service-based business offering services to customers"
            },
            {
                "code": "manufacturing",
                "name": "Manufacturing",
                "description": "Manufacturing business producing goods"
            },
            {
                "code": "restaurant",
                "name": "Restaurant",
                "description": "Restaurant or food service business"
            },
            {
                "code": "ecommerce",
                "name": "E-commerce",
                "description": "Online retail business"
            },
            {
                "code": "professional",
                "name": "Professional Services",
                "description": "Professional services like legal, accounting, consulting"
            },
            {
                "code": "other",
                "name": "Other",
                "description": "Other types of business"
            },
        ]

        for bt_data in business_types:
            existing = session.query(BusinessType).filter(BusinessType.code == bt_data["code"]).first()
            if not existing:
                business_type = BusinessType(
                    public_id=generate_public_id(),
                    code=bt_data["code"],
                    name=bt_data["name"],
                    description=bt_data["description"],
                )
                session.add(business_type)
                print(f"Created business type: {bt_data['code']} - {bt_data['name']}")

        session.commit()
        print("\nBusiness types seeded successfully!")

    except Exception as e:
        session.rollback()
        print(f"\nError seeding business types: {e}")
        raise
    finally:
        session.close()


def downgrade() -> None:
    # Remove foreign key and column
    op.drop_constraint('fk_business_business_type_id', 'business', type_='foreignkey')
    op.drop_column('business', 'business_type_id')

    # Drop business_type table
    op.drop_index(op.f('ix_business_type_code'), table_name='business_type')
    op.drop_index(op.f('ix_business_type_public_id'), table_name='business_type')
    op.drop_index(op.f('ix_business_type_id'), table_name='business_type')
    op.drop_table('business_type')
