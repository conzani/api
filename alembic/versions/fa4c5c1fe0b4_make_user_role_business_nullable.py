"""make_user_role_business_nullable

Revision ID: fa4c5c1fe0b4
Revises: 53824a22fd8a
Create Date: 2026-10-12 11:59:33.724003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa4c5c1fe0b4'
down_revision = '53824a22fd8a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make business_id nullable in user_role table
    op.alter_column(
        'user_role',
        'business_id',
        existing_type=sa.BigInteger(),
        nullable=True
    )


def downgrade() -> None:
    # Make business_id not nullable in user_role table
    op.alter_column(
        'user_role',
        'business_id',
        existing_type=sa.BigInteger(),
        nullable=False
    )
