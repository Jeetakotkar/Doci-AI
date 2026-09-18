from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import face_verification
from app.routers import validation
from app.routers import ocr
from app.routers import tampering
from app.routers import pipeline

app = FastAPI(
    title="Doci-AI",
    description="AI-Based Fake Identity & Document Screening System (SIH PS 26188) — unified backend for all 4 modules.",
    version="1.0.0",
)

# Frontend URLs allowed to access the backend
origins = [
    "http://localhost:5173",          # Local React
    "https://doci-ai-psi.vercel.app", # Vercel frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
app.include_router(face_verification.router)
app.include_router(validation.router)
app.include_router(ocr.router)
app.include_router(tampering.router)
app.include_router(pipeline.router)


@app.get("/")
def root():
    return {
        "message": "Doci-AI Backend is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "doci-ai-backend",
        "version": "1.0.0",
    }