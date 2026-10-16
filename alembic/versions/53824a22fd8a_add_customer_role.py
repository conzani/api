"""add_customer_role

Revision ID: 53824a22fd8a
Revises: seed001
Create Date: 2026-10-12 11:54:49.108241

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
import sys
from pathlib import Path
import secrets

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.models.roles import Role, Permission, RolePermissionGroup

# revision identifiers, used by Alembic.
revision = '53824a22fd8a'
down_revision = 'seed001'
branch_labels = None
depends_on = None


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Get the shop:all permission (if it exists)
        shop_all_permission = session.query(Permission).filter(Permission.code == "shop:all").first()
        
        # If shop:all doesn't exist, create basic customer permissions
        if not shop_all_permission:
            print("Creating basic customer permissions...")
            customer_permissions = [
                {
                    "code": "shop:customers:view",
                    "name": "View Customers",
                    "description": "View customer information"
                },
                {
                    "code": "shop:orders:view",
                    "name": "View Orders",
                    "description": "View order history"
                },
            ]
            
            perm_ids = []
            for perm_data in customer_permissions:
                existing = session.query(Permission).filter(Permission.code == perm_data["code"]).first()
                if not existing:
                    permission = Permission(
                        public_id=generate_public_id(),
                        code=perm_data["code"],
                        name=perm_data["name"],
                        description=perm_data["description"],
                    )
                    session.add(permission)
                    session.flush()
                    perm_ids.append(permission.id)
                    print(f"  Created permission: {perm_data['code']}")
                else:
                    perm_ids.append(existing.id)
        else:
            perm_ids = [shop_all_permission.id]

        # Create Customer role
        print("Creating Customer role...")
        existing_role = session.query(Role).filter(
            Role.name == "Customer",
            Role.business_id.is_(None),
            Role.is_system == True
        ).first()
        
        if not existing_role:
            customer_role = Role(
                public_id=generate_public_id(),
                name="Customer",
                description="Customer with basic access to view orders and profile",
                is_system=True,
                business_id=None,  # Template role
            )
            session.add(customer_role)
            session.flush()
            
            # Assign permissions to Customer role
            for perm_id in perm_ids:
                role_permission = RolePermissionGroup(
                    role_id=customer_role.id,
                    permission_id=perm_id,
                )
                session.add(role_permission)
            
            print(f"  Created role: Customer with {len(perm_ids)} permissions")
        else:
            print("  Customer role already exists")

        session.commit()
        print("\nCustomer role added successfully!")

    except Exception as e:
        session.rollback()
        print(f"\nError adding customer role: {e}")
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        print("Removing Customer role...")
        
        # Find the Customer role
        customer_role = session.query(Role).filter(
            Role.name == "Customer",
            Role.business_id.is_(None),
            Role.is_system == True
        ).first()
        
        if customer_role:
            # Remove role-permission mappings
            session.query(RolePermissionGroup).filter(
                RolePermissionGroup.role_id == customer_role.id
            ).delete(synchronize_session=False)
            
            # Remove the role
            session.delete(customer_role)
            
            print("Customer role removed successfully")
        else:
            print("Customer role not found")

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"\nError removing customer role: {e}")
        raise
    finally:
        session.close()
