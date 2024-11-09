from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1.endpoints import auth, files

from .auth import get_current_user

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Set up CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://skydrive.akshatsaraswat.in"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(
    files.router, prefix=f"{settings.API_V1_PREFIX}/files", tags=["files"]
)


# Example protected endpoint
@app.get("/protected")
async def protected_route(user=Depends(get_current_user)):
    return {"message": "This is a protected route", "user": user}


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI with Supabase"}
