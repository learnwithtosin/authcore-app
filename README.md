AuthCore

AuthCore is a minimalist but production-ready authentication and organization management API built with FastAPI. It provides secure user authentication using JWT access tokens and database-backed refresh tokens with rotation and revocation, along with organization and membership management.

The project is designed as a modular authentication backend that can be reused across multiple applications.

Features
Authentication

JWT access token authentication

Secure refresh tokens stored in database

Refresh token hashing for security

Refresh token rotation

Token revocation support

Login, refresh, and logout endpoints

User Management

Register users

Retrieve authenticated user profile

Update user profile

Change password

Deactivate account

Automatic refresh token revocation on password change

Organization Management

Create organizations

List organizations a user belongs to

View organization details

Membership Management

Invite members to organizations

List organization members

Promote members to admin

Demote admins to members

Suspend / unsuspend members

Remove members from organization

Security

JWT authentication middleware (JWTBearer)

Password hashing

Refresh token hashing

Role-based access control

Admin-only endpoints

Active membership checks

Tech Stack

Python

FastAPI

SQLAlchemy

PostgreSQL / SQLite

JWT (JSON Web Tokens)

Pydantic

Alembic (optional for migrations)

Project Structure
authcore/
│
├── app/
│   ├── api/                # API routes
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── organizations.py
│   │
│   ├── core/               # Core configuration and security
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── models/             # Database models
│   │   ├── user.py
│   │   ├── organization.py
│   │   └── membership.py
│   │
│   ├── schemas/            # Pydantic schemas
│   │
│   ├── dependencies/       # Auth dependencies
│   │   ├── auth.py
│   │   └── permissions.py
│   │
│   └── main.py             # FastAPI application entry point
│
├── requirements.txt
└── README.md
Installation
1. Clone the repository
git clone https://github.com/yourusername/authcore.git
cd authcore
2. Create a virtual environment
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables

Create a .env file:

SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./authcore.db
5. Run the application
uvicorn app.main:app --reload
API Endpoints
Authentication
Method	Endpoint	Description
POST	/auth/register	Register new user
POST	/auth/login	User login
POST	/auth/refresh	Refresh access token
POST	/auth/logout	Logout and revoke refresh token
Users
Method	Endpoint	Description
GET	/users/me	Get current user
PUT	/users/me	Update profile
PUT	/users/change-password	Change password
DELETE	/users/deactivate	Deactivate account
Organizations
Method	Endpoint	Description
POST	/organizations	Create organization
GET	/organizations	List user organizations
GET	/organizations/{org_id}	Get organization details
Membership
Method	Endpoint	Description
GET	/organizations/{org_id}/members	List members
POST	/organizations/{org_id}/invite	Invite member
POST	/organizations/{org_id}/members/{user_id}/promote	Promote to admin
POST	/organizations/{org_id}/members/{user_id}/demote	Demote admin
POST	/organizations/{org_id}/members/{user_id}/suspend	Suspend member
POST	/organizations/{org_id}/members/{user_id}/unsuspend	Unsuspend member
DELETE	/organizations/{org_id}/members/{user_id}	Remove member
Security Design

AuthCore follows several secure authentication patterns:

Short-lived access tokens

Database-stored refresh tokens

Refresh token hashing

Refresh token rotation

Automatic revocation on password change

Role-based organization permissions

These patterns help prevent:

Token replay attacks

Session hijacking

Unauthorized access

Use Cases

AuthCore can serve as the authentication backend for:

SaaS platforms

Startup MVPs

Internal company tools

Multi-tenant applications

Microservices authentication

Future Improvements

Potential extensions:

Email verification

Password reset via email

OAuth login (Google, GitHub)

Rate limiting

Audit logging

API keys for service authentication

License

MIT License
