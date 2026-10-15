## DocKeep 

*Keep What Matters Safe.*

## Product Overview

**DocKeep** is a secure personal document vault that allows users to upload, organize, search, and retrieve important documents from one place.

Users can store educational certificates, medical reports, identity documents, utility bills, and other personal records without relying on scattered phone galleries or messaging applications.

## 2. Problem Statement

People often keep important documents across phones, email accounts, messaging applications, and physical places. Finding the correct document when it is needed it is difficult.

**DocKeep** aims to provide a centralized, organized, and access-controlled solution.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| FastAPI | REST API |
| PostgreSQL | Persistent metadata storage |
| SQLAlchemy | ORM and database queries |
| Pydantic | Data validation |

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

## Project Work Done

- Intilize project folder
- Database Connection
- User , Category , Documents Models
- User , Category , Documents Schemas
- User and Category Routers
- Authentication for user
- Authorization in category 

**Guiding principle:** Build a small, reliable document vault first. Protecting each user's documents is more important than adding advanced features.

## 📜 License

Copyright (c) 2026 Sohail Ahmad. All rights reserved.

This repository is publicly available for viewing and educational/
portfolio purposes. No permission is granted to copy, modify,
distribute, sublicense, or use this software or substantial portions
of it for other projects without prior written permission from the
copyright holder.

For permission to use this project, please contact the author.

## 14. ✒️ Author

Sohail Ahmad

GitHub: (https://github.com/thesohailahmad)
