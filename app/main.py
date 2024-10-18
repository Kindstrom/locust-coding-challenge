from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_db
from app.routes import router


# Lifespan event that is run on app start up. See docs here: https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(router)
