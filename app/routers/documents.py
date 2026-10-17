from fastapi import status
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File , Form , Query
from pathlib import Path
from uuid import uuid4
import os
from typing import Annotated , List
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.document_model import DocumentModels
from app.models.user_model import UserModel
from app.models.category_model import CategoryModel
from app.schemas.document_schema import DocumentCreate, DocumentResponse , DocumentUpdate

from app.core.auth2 import get_current_user


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIRECTORY = Path("storage/documents")
UPLOAD_DIRECTORY.mkdir(exist_ok=True , parents=True)

MAX_FILE_SIZE = 1024 * 1024 * 20
CHUNK_SIZE = 1024 * 1024 

MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "text/plain": ".txt",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}

def get_category_by_id(db: Session, category_id: int , user_id: int) -> CategoryModel:
    category = db.query(CategoryModel).filter(CategoryModel.category_id == category_id, CategoryModel.user_id == user_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.post("/upload_document", response_model=DocumentResponse,
status_code= status.HTTP_201_CREATED
)

async def upload_document(
    title: Annotated[str, Form(..., min_length=1, max_length=255)],
    file: Annotated[UploadFile, File(...)],
    description: Annotated[str | None,  Form( max_length=255)] = None,
    category_id: Annotated[int |  None , Form()] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    if file.content_type not in MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )
    if category_id is not None:
        get_category_by_id(db, category_id, current_user.user_id)
    size = 0
    while chunk := await file.read(CHUNK_SIZE):
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds the maximum limit of 20MB"
            )

        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

    await file.seek(0)

    original_filename = file.filename or "uploaded_file"
    file_extension = Path(original_filename).suffix.lower()
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = UPLOAD_DIRECTORY / unique_filename
    try:
        with open(file_path, "xb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                f.write(chunk)

    except os.error as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the file"
        )
    finally:
        await file.close()
    
    document = DocumentModels(
        title=title,
        description=description,
        original_filename=original_filename,
        stored_filename=unique_filename,
        file_path=str(file_path),
        file_size=size,
        mime_type=file.content_type,
        user_id=current_user.user_id,
        category_id=category_id
    )
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception as e:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the document metadata"
        )
    return document

@router.get("/view_document", response_model=List[DocumentResponse] , status_code= status.HTTP_200_OK)
def view_documents(db: Session = Depends(get_db), 
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user)):
    
    documents = (
    db.query(DocumentModels)
    .filter(DocumentModels.user_id == current_user.user_id)
    .offset(skip)
    .limit(limit)
    .all()
    )
    return documents

@router.get("/view_document/{document_id}", response_model=DocumentResponse , status_code= status.HTTP_200_OK)
def view_document(document_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    document = db.query(DocumentModels).filter(
        DocumentModels.document_id == document_id,
        DocumentModels.user_id == current_user.user_id
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.put("/update_document/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):
    document = db.query(DocumentModels).filter(
        DocumentModels.document_id == document_id,
        DocumentModels.user_id == current_user.user_id
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    update_data = payload.model_dump(exclude_unset=True)
    if "title" in update_data and update_data["title"] is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "title cannot be null")
    
    if update_data.get("category_id") is not None:
        get_category_by_id(db, update_data["category_id"], current_user.user_id)
 
    for field, value in update_data.items():
        setattr(document, field, value)
 
    db.commit()
    db.refresh(document)
    return document

@router.delete("/delete_document/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(document_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    document = db.query(DocumentModels).filter(
        DocumentModels.document_id == document_id,
        DocumentModels.user_id == current_user.user_id
    ).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    file_path = Path(document.file_path)
    db.delete(document)
    db.commit()
    file_path.unlink(missing_ok=True)
    return {"message": "Document deleted successfully"}