from datetime import datetime
from typing import Optional , Annotated
from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    title : Annotated[str , Field(...,min_length=1 , max_length=255 , title="Document Title" , description="Title of the document")]
    description: Annotated[Optional[str], Field(None, max_length=255 , title="Document Description" , description="Description of the document")] = None
    category_id: Annotated[Optional[int], Field(None)] = None  # nullable: ON DELETE SET NULL


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Annotated[Optional[str], Field(None, min_length=1, max_length=255 , title="Document Title" , description="Title of the document")] = None
    description: Annotated[Optional[str], Field(None, max_length=255 , title="Document Description" , description="Description of the document")] = None
    category_id: Annotated[Optional[int], Field(None)] = None


class DocumentResponse(DocumentBase):
    
    model_config = ConfigDict(from_attributes=True)
    document_id: int
    original_filename: str
    file_size: int
    mime_type: str
    user_id: int
    created_at: datetime
    updated_at: datetime


class DocumentInternal(DocumentResponse):

    stored_filename: str
    file_path: str