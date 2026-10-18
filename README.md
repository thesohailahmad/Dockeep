# DocKeep

*Keep what matters safe.*

DocKeep is a secure personal document vault built with FastAPI. Users can upload, organize, and manage important documents such as certificates, medical reports, identity documents, and utility bills in one private place.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Running the Tests](#running-the-tests)
- [Project Structure](#project-structure)
- [Security Design](#security-design)
- [Project Status](#project-status)
- [License](#license)
- [Author](#author)

---

## Problem Statement

Important documents are usually scattered across phone galleries, email accounts, messaging apps, and physical folders. Finding the right document when it is needed is slow and stressful.

DocKeep provides a centralized, organized, and access-controlled place to keep them.

## Features

- **User accounts:** registration and login with JWT authentication.
- **Categories:** create, list, rename, and delete personal categories. Names are unique per user, and case insenstive.
- **Documents:** upload files with a title, description, and optional category. List, update, and delete them.
- **Per-user isolation:** every user can only see and change their own data.
- **File validation:** allowed file types and a maximum file size are enforced on upload.
- **Automated tests:** an API test suite covers authentication, categories, and documents.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming Language |
| FastAPI | REST API framework |
| PostgreSQL | Persistent metadata storage |
| SQLAlchemy | ORM and database queries |
| Pydantic | Request and response validation |
| JWT | Authentication tokens |
| pytest + httpx | Automated API testing |
| uv | Dependency and environment management |

## System Architecture

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

**Data model**

- A **user** owns many **categories** and many **documents**.
- A **category** can hold many documents.
- Deleting a user deletes their categories and documents.
- Deleting a category keeps its documents, which become uncategorized.

## API Endpoints

Interactive documentation at `http://127.0.0.1:8000/docs` once the server is running.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register/` | Create a new account |
| POST | `/auth/login/` | Log in and receive an access token |

### Categories (authentication required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/categories/create_category` | Create a category |
| GET | `/categories/view_category` | List your categories |
| GET | `/categories/view_category/{category_id}` | Get one category |
| PUT | `/categories/update_category/{category_id}` | Rename a category |
| DELETE | `/categories/delete_category/{category_id}` | Delete a category |

### Documents (authentication required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents/upload_document` | Upload a file with its details |
| GET | `/documents/view_document` | List your documents (supports `skip` and `limit`) |
| PUT | `/documents/update_document/{document_id}` | Update title, description, or category |
| DELETE | `/documents/delete_document/{document_id}` | Delete a document and its stored file |

## Getting Started

### Prerequisites

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
- A PostgreSQL database (PgAdmin)

### Installation

```bash
git clone https://github.com/thesohailahmad/Dockeep.git
cd Dockeep
uv sync
```

### Configuration

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

At minimum, set your database connection and a JWT secret key. Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```


### Run the server

```bash
uv run uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000` and the documentation at `http://127.0.0.1:8000/docs`.

## Running the Tests

```bash
uv run pytest -v
```

Run a single file:

- For Example ->
```bash
uv run pytest tests/test_documents.py -v
```

The suite covers authentication, category CRUD, document upload and management, and ownership rules (a user cannot read, change, or delete another user's data). Each test registers its own random user, so tests do not depend on existing data. Uploaded test files are written to a temporary folder.

## Project Structure

```text
Dockeep/
├── app/
│   ├── core/        # Authentication and security helpers
│   ├── db/          # Database configuration, session, and base model
│   ├── models/      # SQLAlchemy models (user, category, document)
│   ├── routers/     # API routes (users, categories, documents)
│   ├── schemas/     # Pydantic schemas
│   ├── services/    # Business logic
│   └── main.py      # Application entry point
├── tests/           # Automated API tests
├── docs/            # Project documentation
├── pyproject.toml
└── README.md
```

## Security Design

- **Ownership checks:** every query filters by the logged-in user. Requesting another user's category or document returns `404`, so the API does not reveal the other user data.
- **Password storage:** passwords is stored in hashed.
- **Safe file storage:** uploaded files are stored under random generated names, and file paths are never exposed in API responses.
- **Upload validation:** file type and size limits are enforced, and other validation is implemented.
- **User Validation:**  if user delete account the data also deleted.
- **Cleanup:** deleting a document also removes its file from storage.

**Guiding principle:** build a small, reliable document vault first. Protecting each user's documents matters more than adding advanced features.

## Project Status

**Completed**

- Project setup and database connection
- User, category, and document models and schemas
- User, category, and document routers
- JWT authentication and per-user authorization
- Automated API test suite

**Planned**

- Document download endpoint
- Backup Documents
- Search across documents
- Continuous integration with GitHub Actions
- Docker setup
- CI/CD
- Deployment

## License

Copyright (c) 2026 Sohail Ahmad. All rights reserved.

This repository is publicly available for viewing and educational/portfolio purposes. No permission is granted to copy, modify, distribute, sublicense, or use this software or substantial portions of it for other projects without prior written permission from the copyright holder.

For permission to use this project, please contact the author.

## Author

**Sohail Ahmad**

- GitHub: [github.com/thesohailahmad](https://github.com/thesohailahmad)
- LinkedIn: [linkedin.com/in/thesohailahmad](https://www.linkedin.com/in/thesohailahmad)