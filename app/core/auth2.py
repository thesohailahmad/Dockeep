from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session
from app.db.config import settings
from app.db.session import get_db
from app.models.user_model import UserModel

## schema for oauth2
oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/login/')
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# function to get the current user from the token
def get_current_user(token: str = Depends(oauth2_schema) , db : Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except PyJWTError:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    user_id  = payload.get('sub')
    
    if user_id is None:
         raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Token credentials"
            )
    
    user = db.query(UserModel).filter(
       UserModel.id == int(user_id)
    ).first()

    if user is None:
             raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User Not found"
                )

    return user