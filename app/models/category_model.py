from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func
from app.db.base import Base
from sqlalchemy.orm import relationship

class CategoryModel(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(
        Integer,
        ForeignKey("user_registration.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    documents = relationship("DocumentModels", 
    back_populates="category") 