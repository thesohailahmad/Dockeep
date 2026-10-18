from fastapi import FastAPI , APIRouter
from app.db.base import Base
from app.db.session  import engine
from app.models.user_model import UserModel
from app.models.document_model import DocumentModels
from app.models.category_model import CategoryModel
from app.routers import users
from app.routers import categories
from app.routers import documents
import time
import logging



Base.metadata.create_all(engine)


app = FastAPI(
    title="Dockeep",
    version="1.1.0",
)

@app.middleware("http")
async def log_timing(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{ms:.1f}"
    logging.getLogger("uvicorn").info("%s %s took %.1f ms", request.method, request.url.path, ms)
    return response

app.include_router(users.router)
app.include_router(categories.router)
app.include_router(documents.router)

@app.get("/")
def root():
    return {"message": "Welcome To Dockeep"}