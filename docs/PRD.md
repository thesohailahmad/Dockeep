# DocKeep — Product Requirements Document (PRD)

*Keep What Matters Safe.*

**Product name:** DocKeep  
**Version:** 1.0 — MVP  
**Product type:** Personal document management web application  
**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL  
**Target users:** Students, families, and individuals who need to organize important documents.

## MVP Features

1. User registration and login.
2. Password hashing and JWT authentication.
3. Document upload for PDF, JPEG, and PNG and e.t.c.
4. Document categories and metadata.
5. Search by title, category filtering, and pagination.
6. Secure document read and deletion.
7. Automated tests for authentication and access control.

## 1. Product Overview

DocKeep is a secure personal document vault that allows users to upload, organize, search, and retrieve important documents from one place.

Users can store educational certificates, medical reports, identity documents, utility bills, and other personal records without relying on scattered phone galleries or messaging applications.

## 2. Problem Statement

People often keep important documents across phones, email accounts, messaging applications, and physical places. Finding the correct document when it is needed it is difficult.

DocKeep aims to provide a centralized, organized, and access-controlled solution.

## 3. Product Goals

- Provide secure user registration and authentication.
- Allow users to upload and manage document images and PDFs.
- Organize documents into categories.
- Support document search, filtering, and pagination.
- Prevent users from accessing other users' documents.
- Build a maintainable, tested backend that can support a frontend later.

## 4. Target Users

- Students managing degrees, transcripts, and certificates.
- Individuals organizing identity documents and utility bills.
- People maintaining personal medical records.
- Families that need an organized place for personal records, with family sharing excluded from the MVP.

## 5. Core Features

### 5.1 Authentication
- User registration and login.
- Secure password hashing.
- JWT-based access authentication.
- Protected document endpoints.

### 5.2 Document Management
- Upload PDF, JPEG, and PNG files.
- Add a document title and category.
- Store metadata in PostgreSQL and file contents in separate storage.
- List, view metadata, download, and delete owned documents.
- Record file size, content type, original filename, and upload timestamp.

### 5.3 Categories
- Organize documents into categories such as Education, Health, Identity, Utilities, and Personal.
- Prevent unauthorized access to user-owned categories.
- Use predefined system categories or user-owned categories consistently.

### 5.4 Search and Filtering
- Search documents by title.
- Filter by category and file type.
- Support pagination to avoid returning every document at once.

### 5.5 Document Dates
- Optionally record issue and expiry dates.
- Store dates as metadata.
- Expiry notifications are outside the MVP.


## 9. Non-Functional Requirements

- **Maintainability:** Separate routes, schemas, models, services, and database configuration.
- **Reliability:** Handle database errors and partial file-storage failures safely.
- **Testability:** Use pytest and an isolated test database or test database configuration.
- **Performance:** Use pagination and database indexes where appropriate.
- **Privacy:** Store only the metadata needed for the application's functionality.
- **Portability:** Provide environment configuration and Docker support for later deployment.

## 10. Version 2

- OCR and automatic text extraction.
- AI-powered document classification.
- Email, SMS, or push notifications.
- Family sharing and organization accounts.
- Subscription payments.
- A native Android or iOS application.
- A production frontend.
- Public document-sharing links.


## 13. Success Metric

The primary success metric is a working, tested backend in which a user can upload a document and retrieve it later without another user being able to access it.

**Product principle:** Security and reliable retrieval come before advanced features or visual polish.