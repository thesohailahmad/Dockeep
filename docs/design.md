# DocKeep — Technical Design Document

*Keep What Matters Safe.*

**Version:** 1.0  
**Project:** Personal Document Vault  
**Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| FastAPI | REST API |
| PostgreSQL | Persistent metadata storage |
| SQLAlchemy | ORM and database queries |
| Alembic | Database migrations |
| Pydantic | Data validation |
| pydantic-settings | Environment configuration |
| pwdlib with Argon2 | Password hashing |
| PyJWT | JWT authentication |
| python-multipart | File uploads |
| pytest and HTTPX | Automated API testing |
| Ruff | Code quality |
| uv | Dependencies and virtual environment |

## 4. System Architecture

```text
Client
  |
  v
FastAPI Routers
  |
  v
Authentication and Authorization
  |
  v
Service Layer
  |
  +---------------------+
  |                     |
  v                     v
PostgreSQL          Private File Storage
(Document metadata) (PDFs and images)
```

Responsibilities:
- Routers handle HTTP requests and responses.
- Schemas validate input and define output.
- Models define database tables and relationships.
- Services contain business logic and ownership checks.
- The database module manages SQLAlchemy sessions.
- The storage module handles private file operations.

## 5. Database Design

### Users

Table: `users`

| Column | Purpose |
|---|---|
| id | Primary key |
| email | Unique account email |
| hashed_password | Secure password hash |
| created_at | Account creation timestamp |

### Categories

Table: `categories`

| Column | Purpose |
|---|---|
| id | Primary key |
| name | Category name |
| owner_id | Optional user foreign key for custom categories |
| created_at | Creation timestamp |

Predefined categories can be global. Custom categories should belong to their creator.

### Documents

Table: `documents`

| Column | Purpose |
|---|---|
| id | Primary key |
| owner_id | Foreign key to users |
| category_id | Foreign key to categories |
| title | User-friendly document title |
| original_filename | Original filename for display |
| storage_key | Server-generated file identifier |
| content_type | Validated media type |
| size_bytes | File size |
| issue_date | Optional issue date |
| expiry_date | Optional expiry date |
| created_at | Upload timestamp |

### Relationships

- One user can own many documents.
- One user can own many custom categories.
- One category can contain many documents.
- Each document has exactly one owner.
- Every document query must enforce ownership.


## 6. File Storage Design

Store metadata in PostgreSQL and actual file contents in private storage.

Example:

```text
private_storage/
    random-file-key-1
    random-file-key-2
```


## 7. Authentication and Authorization

### Registration
- Validate email and password.
- Hash passwords using Argon2.
- Enforce unique email addresses.
- Enforce unique username.

### Login
- Verify the password against the stored hash.
- Issue a signed JWT access token with an expiration.


### Authorization
- Require authentication for private document operations.
- Derive the current user from the verified token.
- Scope every document read, download, update, and delete operation to the current user.
- if the user not authorized Return 404 for documents that do not exist or are not accessible, according to the chosen access policy.


## 9. Project Structure

```text
DocKeep/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── auth.py
│   │   └── security.py
│   ├── db/
│   │   └── session.py
        └── config.py
        └── base.py
│   ├── models/
│   │   ├── user.py
│   │   ├── category.py
│   │   └── document.py
│   ├── schemas/
│   ├── routers/
│   │   ├── users.py
│   │   ├── documents.py
│   │   └── categories.py
│   ├── services/
│   │   └── document_service.py
│   └── storage/
│       └── local_storage.py
├── tests/
├── docs/
├── private_storage/
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## 10. Environment Configuration

Example `.env.example`:

```dotenv
APP_NAME=DocKeep
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/dockeep
JWT_SECRET_KEY=replace-with-a-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```


## 11. Testing Strategy

### Authentication
- Valid registration succeeds.
- Duplicate email is rejected.
- Duplicate username is rejected.
- Passwords are stored as hashes.
- Valid login succeeds.
- Invalid credentials and invalid tokens are rejected.

### Documents
- Valid files can be uploaded.
- Unsupported, empty, and oversized files are rejected.
- Document metadata persists in PostgreSQL.
- User A cannot read, download, or delete User B's documents.
- Missing files and database failures are handled safely.

### Categories
- Available categories are listed correctly.
- Invalid category IDs are rejected.
- Users cannot modify another user's custom categories.

Use a separate test database or isolated test configuration.


## 14. Design Decisions to Confirm

1. UUID or integer primary keys.
2. Predefined categories only, or user-created categories too.
3. Maximum permitted upload size.
4. Local file storage for development.
5. Safe handling of partial failures during file deletion.

**Guiding principle:** Build a small, reliable document vault first. Protecting each user's documents is more important than adding advanced features.