# MJ API

FastAPI project with SQLAlchemy, Alembic, JWT authentication, and email verification.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **JWT Authentication** - Secure token-based authentication
- **Email Verification** - 6-digit code verification via SMTP
- **UUID Public IDs** - 16-character unique identifiers
- **Modular Structure** - Well-organized codebase with routers
- **Pydantic** - Data validation using Python type annotations

## Project Structure

```
mj-api/
├── app/
│   ├── core/           # Configuration, security, email service
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic schemas for validation
│   ├── routers/        # API endpoints
│   ├── crud/           # Database operations (to be implemented)
│   ├── database.py     # Database configuration
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── venv/               # Virtual environment
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Database Schema

The project includes 14 tables:

### Authentication & Authorization
- `auth` - User authentication data
- `users` - User profiles
- `user_role` - User-role assignments
- `roles` - Role definitions
- `permission` - Permission definitions
- `role_permission_group` - Role-permission mappings

### Customer & Business
- `customer` - Customer profiles
- `address` - Address information
- `business` - Business information
- `business_user` - Business-user memberships

### System
- `session` - User sessions
- `verification_token` - Email/phone verification codes (6-digit)
- `invitation` - Business invitations
- `audit_log` - Audit trail

## Setup

### 1. Prerequisites

- Python 3.11 or 3.12 (recommended)
- MySQL database

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and SMTP settings:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/dbname
SECRET_KEY=your-secret-key-here
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 5. Initialize Alembic

```bash
alembic init alembic
```

### 6. Create Initial Migration

```bash
alembic revision --autogenerate -m "Initial migration"
```

### 7. Run Migrations

```bash
alembic upgrade head
```

### 8. Seed Roles and Permissions

The system includes default platform and shop roles with permissions. The seeding is done via a single migration file that contains all role and permission data.

Run the seed migration:

```bash
alembic upgrade seed001
```

This will create:
- **3 Platform Roles** (Super admin, Platform support, Platform finance)
- **9 Shop Role Templates** (Owner, Admin / General manager, Store manager, Cashier / Sales, Inventory clerk, Accountant, Customer support, Delivery / Rider, Viewer)
- **40+ Permissions** covering all system operations

When a new business is created, the shop role templates are automatically copied to that business, and the owner is assigned the Owner role.

### 9. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with email and password
- `POST /auth/verify-email` - Verify email with 6-digit code
- `POST /auth/resend-verification` - Resend verification email
- `POST /auth/refresh` - Refresh access token

### Users (`/users`)
- `POST /users/` - Create a new user
- `GET /users/` - Get all users (paginated)
- `GET /users/{public_id}` - Get a user by public_id
- `PUT /users/{public_id}` - Update a user
- `DELETE /users/{public_id}` - Soft delete a user

### Roles (`/roles`)
- `POST /roles/` - Create a new role
- `GET /roles/` - Get all roles (paginated)
- `GET /roles/{public_id}` - Get a role by public_id
- `PUT /roles/{public_id}` - Update a role
- `DELETE /roles/{public_id}` - Soft delete a role
- `POST /roles/permissions/` - Create a permission
- `GET /roles/permissions/` - Get all permissions
- `POST /roles/{public_id}/permissions/` - Assign permission to role

### Customers (`/customers`)
- `POST /customers/addresses/` - Create an address
- `GET /customers/addresses/` - Get all addresses
- `GET /customers/addresses/{address_id}` - Get an address
- `PUT /customers/addresses/{address_id}` - Update an address
- `POST /customers/` - Create a customer
- `GET /customers/` - Get all customers (paginated)
- `GET /customers/{public_id}` - Get a customer by public_id
- `PUT /customers/{public_id}` - Update a customer
- `DELETE /customers/{public_id}` - Soft delete a customer

### Businesses (`/businesses`)
- `POST /businesses/` - Create a business
- `GET /businesses/` - Get all businesses (paginated)
- `GET /businesses/{public_id}` - Get a business by public_id
- `PUT /businesses/{public_id}` - Update a business
- `DELETE /businesses/{public_id}` - Soft delete a business
- `POST /businesses/{public_id}/users/` - Add user to business
- `GET /businesses/{public_id}/users/` - Get business users

### System (`/system`)
- `POST /system/sessions/` - Create a session
- `GET /system/sessions/` - Get all sessions
- `DELETE /system/sessions/{session_id}` - Revoke a session
- `POST /system/verification-tokens/` - Create verification token
- `GET /system/verification-tokens/` - Get verification tokens
- `POST /system/invitations/` - Create invitation
- `GET /system/invitations/` - Get invitations
- `POST /system/invitations/{id}/accept` - Accept invitation
- `POST /system/audit-logs/` - Create audit log
- `GET /system/audit-logs/` - Get audit logs
- `GET /system/audit-logs/{business_public_id}` - Get business audit logs

## Key Features

### UUID Public IDs
All entities use 16-character UUID-like public IDs for API exposure:
```python
public_id = secrets.token_hex(8)  # 16 hex characters
```

### 6-Digit Verification Codes
Email verification uses 6-digit codes:
```python
verification_code = generate_verification_code()  # e.g., "123456"
```

### Email Service
SMTP-based email service with support for:
- Email verification
- Password reset
- Business invitations

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Account lockout after 5 failed login attempts
- Email verification required before login
- Soft delete for data retention

## Next Steps

- Implement CRUD operations in `app/crud/`
- Add comprehensive error handling
- Implement refresh token validation
- Add rate limiting
- Write unit tests
- Set up CI/CD pipeline
- Add API documentation enhancements

## License

MIT
