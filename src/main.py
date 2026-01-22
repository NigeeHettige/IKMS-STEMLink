from fastapi import FastAPI
from src.app.api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config import get_settings



app = FastAPI(
    title="Class 12 Multi-Agent RAG Demo",
    description=(
        "Demo API for asking questions about a vector databases paper. "
        "The `/qa` endpoint currently returns placeholder responses and "
        "will be wired to a multi-agent RAG pipeline in later user stories."
    ),
    version="0.1.0",
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       settings.allowed_origin
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to IKMS-STEMLink API"}


app.include_router(api_router)