# AuthCore

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

> A minimalist, production-ready authentication and organization management API — built to be dropped into any multi-tenant SaaS, startup MVP, or microservices backend.

AuthCore handles the authentication layer most apps need but few get right: short-lived JWT access tokens, database-backed refresh tokens with **rotation and revocation**, hashed token storage, and role-based organization membership — all in a clean, modular FastAPI structure.

---

## Why AuthCore?

Most auth tutorials stop at "here's a JWT login endpoint." AuthCore implements what production apps actually need:

| Pattern | What it prevents |
|---|---|
| Short-lived access tokens (15 min) | Stolen token abuse |
| Refresh token hashing in DB | Token exposure via DB leak |
| Refresh token rotation | Token replay attacks |
| Auto-revocation on password change | Session hijacking after credential change |
| Role-based org permissions | Unauthorized access across tenants |

---

## Features

### Authentication
- JWT access token authentication
- Refresh tokens stored and hashed in the database
- Refresh token rotation on every use
- Token revocation on logout
- Auto-revoke all tokens on password change

### User Management
- Register, login, logout
- View and update profile
- Change password
- Deactivate account

### Organization Management
- Create organizations
- List organizations a user belongs to
- View organization details

### Membership Management
- Invite members to an organization
- List all organization members
- Promote members to admin / demote admins
- Suspend and unsuspend members
- Remove members

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy |
| Database | PostgreSQL (SQLite supported for dev) |
| Migrations | Alembic |
| Auth | JWT (PyJWT) + bcrypt |
| Containerization | Docker + Docker Compose |
| Validation | Pydantic v2 |

---

## Project Structure

```
authcore/
├── app/
│   ├── api/                  # Route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── organizations.py
│   ├── core/                 # Security & config
│   │   ├── config.py
│   │   └── security.py
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py
│   │   ├── organization.py
│   │   └── membership.py
│   ├── schemas/              # Pydantic schemas
│   ├── dependencies/         # Auth & permission dependencies
│   │   ├── auth.py
│   │   └── permissions.py
│   └── main.py               # Application entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example              # Environment variable template
```

---

## Quick Start

### Option A — Docker (recommended)

```bash
git clone https://github.com/learnwithtosin/authcore-app.git
cd authcore-app
cp .env.example .env          # Fill in your values
docker-compose up --build
```

API will be live at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### Option B — Local

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Fill in your values
uvicorn app.main:app --reload
```

---

## Environment Variables

Copy `.env.example` to `.env` and set the following:

```env
SECRET_KEY=your_strong_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./authcore.db   # or your PostgreSQL URL
```

> Never commit your `.env` file. It is already in `.gitignore`.

---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive tokens | No |
| POST | `/auth/refresh` | Rotate refresh token | Refresh token |
| POST | `/auth/logout` | Revoke refresh token | Yes |

### Users

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| GET | `/users/me` | Get current user profile | Yes |
| PUT | `/users/me` | Update profile | Yes |
| PUT | `/users/change-password` | Change password (revokes all tokens) | Yes |
| DELETE | `/users/deactivate` | Deactivate account | Yes |

### Organizations

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/organizations` | Create organization | Yes |
| GET | `/organizations` | List user's organizations | Yes |
| GET | `/organizations/{org_id}` | Get organization details | Yes |

### Membership

| Method | Endpoint | Description | Role required |
|---|---|---|---|
| GET | `/organizations/{org_id}/members` | List members | Member |
| POST | `/organizations/{org_id}/invite` | Invite a member | Admin |
| POST | `/organizations/{org_id}/members/{user_id}/promote` | Promote to admin | Admin |
| POST | `/organizations/{org_id}/members/{user_id}/demote` | Demote admin | Admin |
| POST | `/organizations/{org_id}/members/{user_id}/suspend` | Suspend member | Admin |
| POST | `/organizations/{org_id}/members/{user_id}/unsuspend` | Unsuspend member | Admin |
| DELETE | `/organizations/{org_id}/members/{user_id}` | Remove member | Admin |

---

## Security Design

AuthCore follows production authentication patterns throughout:

- **Access tokens** expire in 15 minutes — limiting the window for token misuse
- **Refresh tokens** are stored as bcrypt hashes — a DB breach does not expose usable tokens
- **Token rotation** issues a new refresh token on every use and invalidates the old one
- **Password change** triggers revocation of all existing refresh tokens across all devices
- **RBAC** enforces admin-only routes at the dependency level, not inside route handlers

---

## Use Cases

AuthCore is designed to be the authentication backend for:

- SaaS platforms with team/workspace features
- Startup MVPs needing secure auth from day one
- Internal tools with role-based access
- Multi-tenant applications
- Microservices needing a centralized auth service

---

## Roadmap

- [ ] Email verification on registration
- [ ] Password reset via email (token-based)
- [ ] OAuth2 login (Google, GitHub)
- [ ] Rate limiting on auth endpoints
- [ ] Audit logging (login attempts, role changes)
- [ ] API key authentication for service-to-service calls

---

## License

MIT — use it, extend it, ship it.
