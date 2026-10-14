from fastapi import FastAPI
from app.db.base import Base
from app.db.session  import engine
from app.models.user_model import UserModel
from app.models.document_model import DocumentModels
from app.models.category_model import CategoryModel
# Create the database tables
Base.metadata.create_all(engine)

# expose the FastAPI app
app = FastAPI(
    title="Dockeep",
    version="1.1.0",
)

@app.get("/")
def root():
    return {"message": "Welcome To Dockeep"}
