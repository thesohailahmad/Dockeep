from sqlalchemy import Column,Integer,String , TIMESTAMP , func
from app.db.base import Base
from sqlalchemy.orm import relationship

#class for user model
#table to store user data
#UserModel class inherits from Base class which is imported from base.py file

class UserModel(Base):
    __tablename__ = "user_registration"

    user_id = Column(Integer , primary_key=True , index=True)
    name = Column(String(100) , nullable=False)
    username = Column(String(100) , unique=True, nullable=False)
    hash_password = Column(String(100) , nullable=False)
    email = Column(String(120) , unique=True, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    documents = relationship("DocumentModels", 
    back_populates="user",
    cascade="all, delete-orphan")