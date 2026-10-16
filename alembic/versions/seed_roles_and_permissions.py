"""seed_roles_and_permissions

Revision ID: seed001
Revises: bf036ad268ff
Create Date: 2026-10-12

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
revision = 'seed001'
down_revision = 'bf036ad268ff'
branch_labels = None
depends_on = None


def generate_public_id():
    """Generate a 16-character UUID-like public ID."""
    return secrets.token_hex(8)


# Platform Permissions (business_id = null, is_system = true)
PLATFORM_PERMISSIONS = [
    # Super Admin Permissions
    {"code": "platform:all", "name": "Platform All Access", "description": "Full access to all platform features"},
    {"code": "platform:shops:manage", "name": "Manage Shops", "description": "Create, update, delete shops"},
    {"code": "platform:shops:view", "name": "View Shops", "description": "View all shops and their data"},
    {"code": "platform:billing:manage", "name": "Manage Billing", "description": "Manage subscriptions, plans, and invoices"},
    {"code": "platform:billing:view", "name": "View Billing", "description": "View subscriptions and invoices"},
    {"code": "platform:users:manage", "name": "Manage Platform Users", "description": "Manage platform admin users"},
    {"code": "platform:reports:all", "name": "All Platform Reports", "description": "Access all platform reports"},
    {"code": "platform:settings:manage", "name": "Manage Platform Settings", "description": "Manage platform-wide settings"},

    # Platform Support Permissions
    {"code": "platform:support:all", "name": "Platform Support Actions", "description": "Perform support actions"},

    # Platform Finance Permissions
    {"code": "platform:finance:reports", "name": "Finance Reports", "description": "View financial reports"},
]

# Platform Roles
PLATFORM_ROLES = [
    {
        "name": "Super admin",
        "description": "Full platform access including billing and shop management",
        "is_system": True,
        "permissions": [
            "platform:all",
        ]
    },
    {
        "name": "Platform support",
        "description": "View shops and help users, but can't change billing or delete data",
        "is_system": True,
        "permissions": [
            "platform:shops:view",
            "platform:users:view",
            "platform:reports:view",
            "platform:support:all",
        ]
    },
    {
        "name": "Platform finance",
        "description": "View subscriptions and invoices only",
        "is_system": True,
        "permissions": [
            "platform:billing:view",
            "platform:finance:reports",
        ]
    },
]

# Shop Permissions (for business-specific roles)
SHOP_PERMISSIONS = [
    # General
    {"code": "shop:all", "name": "Shop All Access", "description": "Full access to shop features"},
    {"code": "shop:view", "name": "View Shop", "description": "View shop information"},

    # Products & Inventory
    {"code": "shop:products:view", "name": "View Products", "description": "View product catalog"},
    {"code": "shop:products:create", "name": "Create Products", "description": "Add new products"},
    {"code": "shop:products:update", "name": "Update Products", "description": "Edit product details"},
    {"code": "shop:products:delete", "name": "Delete Products", "description": "Remove products"},
    {"code": "shop:inventory:view", "name": "View Inventory", "description": "View stock levels"},
    {"code": "shop:inventory:update", "name": "Update Inventory", "description": "Adjust stock levels"},
    {"code": "shop:inventory:stocktake", "name": "Stock Take", "description": "Perform stock counts"},

    # Orders & Sales
    {"code": "shop:orders:view", "name": "View Orders", "description": "View orders and sales"},
    {"code": "shop:orders:create", "name": "Create Orders", "description": "Create new orders"},
    {"code": "shop:orders:update", "name": "Update Orders", "description": "Modify orders"},
    {"code": "shop:orders:delete", "name": "Delete Orders", "description": "Cancel/delete orders"},
    {"code": "shop:orders:refund", "name": "Process Refunds", "description": "Issue refunds"},
    {"code": "shop:orders:approve", "name": "Approve Orders", "description": "Approve orders requiring approval"},
    {"code": "shop:payments:view", "name": "View Payments", "description": "View payment transactions"},
    {"code": "shop:payments:process", "name": "Process Payments", "description": "Process payments"},

    # Customers
    {"code": "shop:customers:view", "name": "View Customers", "description": "View customer list"},
    {"code": "shop:customers:create", "name": "Create Customers", "description": "Add new customers"},
    {"code": "shop:customers:update", "name": "Update Customers", "description": "Edit customer details"},
    {"code": "shop:customers:delete", "name": "Delete Customers", "description": "Remove customers"},

    # Staff & Users
    {"code": "shop:staff:view", "name": "View Staff", "description": "View staff members"},
    {"code": "shop:staff:create", "name": "Create Staff", "description": "Add staff members"},
    {"code": "shop:staff:update", "name": "Update Staff", "description": "Edit staff details"},
    {"code": "shop:staff:delete", "name": "Delete Staff", "description": "Remove staff"},
    {"code": "shop:staff:assign", "name": "Assign Staff", "description": "Assign staff to roles/stores"},

    # Reports
    {"code": "shop:reports:sales", "name": "Sales Reports", "description": "View sales reports"},
    {"code": "shop:reports:inventory", "name": "Inventory Reports", "description": "View inventory reports"},
    {"code": "shop:reports:financial", "name": "Financial Reports", "description": "View financial reports"},
    {"code": "shop:reports:staff", "name": "Staff Reports", "description": "View staff performance reports"},
    {"code": "shop:reports:all", "name": "All Reports", "description": "Access all shop reports"},

    # Settings
    {"code": "shop:settings:view", "name": "View Settings", "description": "View shop settings"},
    {"code": "shop:settings:update", "name": "Update Settings", "description": "Modify shop settings"},

    # Billing (for business owners)
    {"code": "shop:billing:view", "name": "View Billing", "description": "View billing information"},
    {"code": "shop:billing:manage", "name": "Manage Billing", "description": "Manage subscriptions and payments"},

    # Roles & Permissions
    {"code": "shop:roles:view", "name": "View Roles", "description": "View shop roles"},
    {"code": "shop:roles:create", "name": "Create Roles", "description": "Create custom roles"},
    {"code": "shop:roles:update", "name": "Update Roles", "description": "Edit role permissions"},
    {"code": "shop:roles:delete", "name": "Delete Roles", "description": "Remove roles"},

    # Delivery
    {"code": "shop:delivery:view", "name": "View Deliveries", "description": "View delivery orders"},
    {"code": "shop:delivery:update", "name": "Update Deliveries", "description": "Update delivery status"},
    {"code": "shop:delivery:own", "name": "Own Deliveries", "description": "View and update only assigned deliveries"},
]

# Shop Roles (default roles for each business)
SHOP_ROLES = [
    {
        "name": "Owner",
        "description": "Full control of the shop, including billing, deleting the shop and managing roles",
        "is_system": True,
        "permissions": [
            "shop:all",
        ]
    },
    {
        "name": "Admin / General manager",
        "description": "Everything except billing and deleting the shop",
        "is_system": True,
        "permissions": [
            "shop:products:view",
            "shop:products:create",
            "shop:products:update",
            "shop:products:delete",
            "shop:inventory:view",
            "shop:inventory:update",
            "shop:inventory:stocktake",
            "shop:orders:view",
            "shop:orders:create",
            "shop:orders:update",
            "shop:orders:delete",
            "shop:orders:refund",
            "shop:payments:view",
            "shop:payments:process",
            "shop:customers:view",
            "shop:customers:create",
            "shop:customers:update",
            "shop:customers:delete",
            "shop:staff:view",
            "shop:staff:create",
            "shop:staff:update",
            "shop:staff:delete",
            "shop:staff:assign",
            "shop:reports:sales",
            "shop:reports:inventory",
            "shop:reports:financial",
            "shop:reports:staff",
            "shop:reports:all",
            "shop:settings:view",
            "shop:settings:update",
            "shop:delivery:view",
            "shop:delivery:update",
        ]
    },
    {
        "name": "Store manager",
        "description": "Products, stock, orders, staff, reports for their store",
        "is_system": True,
        "permissions": [
            "shop:products:view",
            "shop:products:create",
            "shop:products:update",
            "shop:inventory:view",
            "shop:inventory:update",
            "shop:inventory:stocktake",
            "shop:orders:view",
            "shop:orders:create",
            "shop:orders:update",
            "shop:payments:view",
            "shop:customers:view",
            "shop:customers:create",
            "shop:customers:update",
            "shop:staff:view",
            "shop:staff:assign",
            "shop:reports:sales",
            "shop:reports:inventory",
            "shop:reports:staff",
            "shop:delivery:view",
            "shop:delivery:update",
        ]
    },
    {
        "name": "Cashier / Sales",
        "description": "Create sales, take payments, look up customers. Can't change prices or issue refunds without approval",
        "is_system": True,
        "permissions": [
            "shop:products:view",
            "shop:orders:view",
            "shop:orders:create",
            "shop:payments:process",
            "shop:customers:view",
            "shop:delivery:view",
        ]
    },
    {
        "name": "Inventory clerk",
        "description": "Add and update products, receive stock, run stock counts. Can't see sales totals or profit",
        "is_system": True,
        "permissions": [
            "shop:products:view",
            "shop:products:create",
            "shop:products:update",
            "shop:inventory:view",
            "shop:inventory:update",
            "shop:inventory:stocktake",
            "shop:reports:inventory",
        ]
    },
    {
        "name": "Accountant",
        "description": "Reports, expenses, tax, payments. Read-only on products and orders",
        "is_system": True,
        "permissions": [
            "shop:products:view",
            "shop:orders:view",
            "shop:payments:view",
            "shop:customers:view",
            "shop:reports:sales",
            "shop:reports:financial",
            "shop:reports:all",
        ]
    },
    {
        "name": "Customer support",
        "description": "View orders and customers, process returns",
        "is_system": True,
        "permissions": [
            "shop:orders:view",
            "shop:orders:update",
            "shop:orders:refund",
            "shop:customers:view",
            "shop:customers:update",
            "shop:delivery:view",
        ]
    },
    {
        "name": "Delivery / Rider",
        "description": "See and update only their assigned deliveries",
        "is_system": True,
        "permissions": [
            "shop:delivery:own",
        ]
    },
    {
        "name": "Viewer",
        "description": "Read-only, for auditors or investors",
        "is_system": True,
        "permissions": [
            "shop:products:view",
            "shop:inventory:view",
            "shop:orders:view",
            "shop:payments:view",
            "shop:customers:view",
            "shop:staff:view",
            "shop:reports:sales",
            "shop:reports:inventory",
            "shop:reports:financial",
            "shop:reports:staff",
            "shop:delivery:view",
        ]
    },
]


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Seed Platform Permissions
        print("Seeding platform permissions...")
        platform_permission_map = {}
        for perm_data in PLATFORM_PERMISSIONS:
            # Check if permission already exists
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
                platform_permission_map[perm_data["code"]] = permission.id
                print(f"  Created permission: {perm_data['code']}")
            else:
                platform_permission_map[perm_data["code"]] = existing.id
                print(f"  Permission already exists: {perm_data['code']}")

        # Seed Platform Roles
        print("\nSeeding platform roles...")
        for role_data in PLATFORM_ROLES:
            # Check if role already exists
            existing = session.query(Role).filter(
                Role.name == role_data["name"],
                Role.business_id.is_(None),
                Role.is_system == True
            ).first()
            
            if not existing:
                role = Role(
                    public_id=generate_public_id(),
                    name=role_data["name"],
                    description=role_data["description"],
                    is_system=role_data["is_system"],
                    business_id=None,  # Platform roles have no business
                )
                session.add(role)
                session.flush()
                
                # Assign permissions to role
                for perm_code in role_data["permissions"]:
                    if perm_code in platform_permission_map:
                        permission_id = platform_permission_map[perm_code]
                        role_permission = RolePermissionGroup(
                            role_id=role.id,
                            permission_id=permission_id,
                        )
                        session.add(role_permission)
                
                print(f"  Created role: {role_data['name']} with {len(role_data['permissions'])} permissions")
            else:
                print(f"  Role already exists: {role_data['name']}")

        # Seed Shop Permissions (as system-wide templates)
        print("\nSeeding shop permissions...")
        shop_permission_map = {}
        for perm_data in SHOP_PERMISSIONS:
            # Check if permission already exists
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
                shop_permission_map[perm_data["code"]] = permission.id
                print(f"  Created permission: {perm_data['code']}")
            else:
                shop_permission_map[perm_data["code"]] = existing.id
                print(f"  Permission already exists: {perm_data['code']}")

        # Seed Shop Roles (as system-wide templates)
        print("\nSeeding shop role templates...")
        for role_data in SHOP_ROLES:
            # Check if role template already exists
            existing = session.query(Role).filter(
                Role.name == role_data["name"],
                Role.business_id.is_(None),
                Role.is_system == True
            ).first()
            
            if not existing:
                role = Role(
                    public_id=generate_public_id(),
                    name=role_data["name"],
                    description=role_data["description"],
                    is_system=role_data["is_system"],
                    business_id=None,  # Template roles have no business
                )
                session.add(role)
                session.flush()
                
                # Assign permissions to role
                for perm_code in role_data["permissions"]:
                    if perm_code in shop_permission_map:
                        permission_id = shop_permission_map[perm_code]
                        role_permission = RolePermissionGroup(
                            role_id=role.id,
                            permission_id=permission_id,
                        )
                        session.add(role_permission)
                
                print(f"  Created role template: {role_data['name']} with {len(role_data['permissions'])} permissions")
            else:
                print(f"  Role template already exists: {role_data['name']}")

        session.commit()
        print("\nSeed data completed successfully!")
        print("\nSeeded:")
        print("  - 3 Platform Roles: Super admin, Platform support, Platform finance")
        print("  - 9 Shop Role Templates: Owner, Admin / General manager, Store manager, Cashier / Sales, Inventory clerk, Accountant, Customer support, Delivery / Rider, Viewer")
        print("  - 40+ Permissions")

    except Exception as e:
        session.rollback()
        print(f"\nError seeding data: {e}")
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        print("Removing seeded data...")

        # Remove role-permission mappings for seeded roles
        print("Removing role-permission mappings...")
        session.query(RolePermissionGroup).filter(
            RolePermissionGroup.role_id.in_(
                session.query(Role.id).filter(
                    (Role.business_id.is_(None)) & (Role.is_system == True)
                )
            )
        ).delete(synchronize_session=False)

        # Remove system roles
        print("Removing system roles...")
        session.query(Role).filter(
            (Role.business_id.is_(None)) & (Role.is_system == True)
        ).delete(synchronize_session=False)

        # Remove seeded permissions
        print("Removing seeded permissions...")
        all_permission_codes = [p["code"] for p in PLATFORM_PERMISSIONS + SHOP_PERMISSIONS]
        session.query(Permission).filter(Permission.code.in_(all_permission_codes)).delete(
            synchronize_session=False
        )

        session.commit()
        print("\nSeed data removed successfully!")

    except Exception as e:
        session.rollback()
        print(f"\nError removing seed data: {e}")
        raise
    finally:
        session.close()
