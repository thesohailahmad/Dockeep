from sqlalchemy import Column, TIMESTAMP, ForeignKey, Integer, String , Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class DocumentModels(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False, index=True)
    
    description = Column(Text, nullable=True)

    
    original_filename = Column(String(255), nullable=False)
    
    stored_filename = Column(String(255), nullable=False, unique=True)
    
    file_path = Column(
        String(500), nullable=False
    )  
    
    file_size = Column(Integer, nullable=False) 
    
    mime_type = Column(
        String(100), nullable=False
    ) 

    user_id = Column(
        Integer, ForeignKey("user_registration.user_id", ondelete="CASCADE"), nullable=False , index=True
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.category_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    user = relationship("UserModel", back_populates="documents")
    category = relationship("CategoryModel", back_populates="documents")