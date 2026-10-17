from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.category_model import CategoryModel
from app.models.user_model import UserModel
from app.schemas.category_schema import CategoryCreate , CategoryResponse , CategoryUpdate
from app.core.auth2 import get_current_user  


router = APIRouter(prefix="/categories", tags=["Categories"])



def get_categories(db: Session, category_id: int, user_id: int) -> CategoryModel:
    category = (
        db.query(CategoryModel)
        .filter(
            CategoryModel.category_id == category_id,
            CategoryModel.user_id == user_id,
        )
        .first()
    )
    if not category:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found for this user",
        )
    return category

def check_name(db: Session, user_id: int, name: str, exclude_id: int | None = None) -> None:
    
    query = db.query(CategoryModel).filter(
        CategoryModel.user_id == user_id,
        func.lower(CategoryModel.name) == name.lower(),
    )
    if exclude_id is not None:
        query = query.filter(CategoryModel.category_id != exclude_id)

    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{name}' already exists"
        )

@router.post("/create_category", 
response_model=CategoryResponse, 
status_code=status.HTTP_201_CREATED
)

def create_category(payload: CategoryCreate,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    name = payload.name.strip()
    if name is None or name == "":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, 
        detail="Name cannot be blank")

    check_name(db, current_user.user_id, name)

    category = CategoryModel(name=name, user_id=current_user.user_id)
    try:
        db.add(category)
        db.commit()
        db.refresh(category)
    except IntegrityError:

        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, 
        detail=f"Category '{name}' already exists")

    return category


@router.get("/view_category", 
    response_model=List[CategoryResponse] , 
    status_code=status.HTTP_200_OK,)

def list_categories( skip: int = Query(0, ge=0),limit: int = Query(100, ge=1, le=200),db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    
    return (
        db.query(CategoryModel)
        .filter(CategoryModel.user_id == current_user.user_id)
        .order_by(func.lower(CategoryModel.name))
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/view_category/{category_id}", 
        response_model=CategoryResponse , 
        status_code=status.HTTP_200_OK,
)

def get_category(category_id: int,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    
    return get_categories(db, category_id, current_user.user_id)


@router.put("/update_category/{category_id}",
                response_model=CategoryResponse , 
                status_code=status.HTTP_200_OK
                )
def update_category(category_id: int,payload: CategoryUpdate,db: Session = Depends(get_db),current_user: UserModel = Depends(get_current_user)):
    category = get_categories(db, category_id, current_user.user_id)

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        new_name = (update_data["name"] or "").strip()
        if not new_name:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, "Name cannot be blank"
            )
        check_name(
            db, current_user.user_id, new_name, exclude_id=category.category_id
        )
        category.name = new_name

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Category name already exists")

    return category


@router.delete("/delete_category/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    category = get_categories(db, category_id, current_user.user_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found for this user",
        )
    response_data = CategoryResponse.model_validate(category)
    db.delete(category)
    db.commit()
    return response_data