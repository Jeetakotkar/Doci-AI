from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import face_verification
# --- Teammates will add their routers here as they finish them ---
# from app.routers import ocr
# from app.routers import validation
# from app.routers import tampering
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
app.include_router(face_verification.router)   # Module 4 — you
app.include_router(pipeline.router)            # Orchestration endpoint — you
# app.include_router(ocr.router)               # Module 1 — P1, uncomment once ready
# app.include_router(validation.router)        # Module 2 — P2/P3, uncomment once ready
# app.include_router(tampering.router)         # Module 3 — P1, uncomment once ready


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "sih-ps26188-backend"}
