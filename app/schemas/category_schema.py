from datetime import datetime
from typing import Optional , Annotated
from pydantic import BaseModel , ConfigDict , Field


class CategoryBase(BaseModel):
    name : Annotated[str , Field(...,min_length=1 , max_length=100 , title="Category Name" , description="Name of the category")]


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name : Optional[Annotated[str , Field(None,min_length=1 , max_length=100 , title="Category Name" , description="Name of the category")]] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    category_id: int
    user_id: int
    created_at: datetime