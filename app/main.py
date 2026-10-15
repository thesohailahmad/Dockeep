from fastapi import FastAPI , APIRouter
from app.db.base import Base
from app.db.session  import engine
from app.models.user_model import UserModel
from app.models.document_model import DocumentModels
from app.models.category_model import CategoryModel
from app.routers import users
from app.routers import categories

Base.metadata.create_all(engine)


app = FastAPI(
    title="Dockeep",
    version="1.1.0",
)

app.include_router(users.router)
app.include_router(categories.router)

@app.get("/")
def root():
    return {"message": "Welcome To Dockeep"}