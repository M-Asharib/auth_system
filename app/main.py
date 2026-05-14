from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import auth, users
from app.services.redis_service import redis_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Redis
    await redis_service.connect()
    yield
    # Shutdown: Disconnect from Redis
    await redis_service.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Advanced Asynchronous Backend System", "docs": "/docs"}
