from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreate , UserResponse , UserLogin , Token
from fastapi import APIRouter , Depends , status , HTTPException , Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import hash_password , verify_password , create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth" , tags=["User"])


@router.post("/register/",
            response_model=UserResponse,
            status_code= status.HTTP_201_CREATED,
)

def register_user(data:UserCreate , db : Session = Depends(get_db)):

    existing_user = db.query(UserModel).filter(
        UserModel.username == data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    existing_email = db.query(UserModel).filter(
        UserModel.email == data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    if len(data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    new_user = UserModel(
        name=data.name,
        username=data.username,
        hash_password=hash_password(data.password),
        email=data.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login/",
            response_model=Token,
            status_code= status.HTTP_200_OK,
)
def login_user(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(
    UserModel.username == data.username
).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or Password"
        )
    if not verify_password(data.password, user.hash_password):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )
    access_token = create_access_token(
    {"sub": str(user.user_id)}
)
    return {
    "access_token": access_token,
    "token_type": "bearer"
}
    

    
