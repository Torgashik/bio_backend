from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api import auth, biometric, organizations
from .database.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(biometric.router, prefix=f"{settings.API_V1_STR}/biometric", tags=["biometric"])
app.include_router(organizations.router, prefix=settings.API_V1_STR, tags=["organizations"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Biometric Data Management API",
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs"
    } 