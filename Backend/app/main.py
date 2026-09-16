from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import face_verification
from app.routers import pipeline

app = FastAPI(
    title="AI-Based Fake Identity & Document Screening System",
    description="SIH PS 26188 — unified backend for all 4 modules.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: restrict to frontend's real origin before final demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mount each module's router ---
app.include_router(face_verification.router)   
app.include_router(pipeline.router)            


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "sih-ps26188-backend"}
