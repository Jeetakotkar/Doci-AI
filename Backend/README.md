# SIH PS 26188 — Backend

Single FastAPI backend serving all 4 modules of the AI-Based Fake Identity
& Document Screening System, plus a combined pipeline endpoint.

## Team ownership map

| Who | Owns |
|---|---|
| P1 | Module 1 (OCR) — `app/services/ocr/`, `app/routers/ocr.py` |
| P1 | Module 3 (Tampering Detection) — `app/services/tampering/`, `app/routers/tampering.py` |
| P2/P3 | Module 2 (Validation) — `app/services/validation/`, `app/routers/validation.py` |
| P2/P3 | Database — `app/db/`, `app/models/db_models.py` |
| **You** | Module 4 (Face Verification) — `app/services/face_verification/`, `app/routers/face_verification.py` |
| **You** | Backend integration — `app/main.py`, `app/routers/pipeline.py`, deployment |
| P5 | Frontend — separate repo, calls this backend's API |

## Why one repo, one FastAPI app

Instead of 4 separate servers, every module is a **router + service pair**
mounted onto one `FastAPI()` instance in `app/main.py`. This means:
- One port, one base URL for the frontend team (`localhost:8000`)
- One `/docs` page showing every endpoint from all 4 modules together
- One shared CORS config, one shared `requirements.txt`
- Easy to combine module outputs in `pipeline.py` for a single "scan full
  document" demo flow — strong for judges to see

## Folder structure

```
app/
├── main.py                    # mounts all routers — THE entrypoint
├── routers/                   # one file per module, defines API endpoints
│   ├── face_verification.py   # (you) Module 4 endpoint
│   ├── pipeline.py            # (you) orchestrates all 4 modules together
│   ├── ocr.py                 # (P1) Module 1 — add when ready
│   ├── validation.py          # (P2/P3) Module 2 — add when ready
│   └── tampering.py           # (P1) Module 3 — add when ready
├── services/                  # business logic, no FastAPI code here
│   ├── face_verification/     # (you) liveness.py, face_match.py
│   ├── ocr/                   # (P1)
│   ├── validation/            # (P2/P3)
│   └── tampering/             # (P1)
├── models/                    # Pydantic schemas (API contracts) + DB models
├── db/                        # (P2/P3) database connection/session setup
└── utils/                     # shared helpers, e.g. image decoding
```

**Rule of thumb for teammates:** routers only handle HTTP (parse request,
call a service function, return response). All actual logic goes in
`services/`. Keeps things testable and keeps routers thin.

## How to run it

### 1. Clone / pull the repo, set up a virtual environment

```bash
cd sih-backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Download DeepFace's model weights (once, needs internet)

DeepFace auto-downloads ArcFace weights the first time it's used. Trigger
this ahead of time (e.g. by hitting `/api/v1/face-verification/verify` once
with any test images) rather than during your live demo.

### 3. Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

- API root: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

`--reload` auto-restarts the server on file changes — keep this on during
development, drop it for the actual demo (slightly more stable without it).

### 4. Test Module 4 standalone

Use `/docs` — it gives you a UI to upload files and hit the endpoint
without writing a test script. Or use curl:

```bash
curl -X POST http://localhost:8000/api/v1/face-verification/verify \
  -F "document_face=@sample_id_photo.jpg" \
  -F "live_frames=@frame1.jpg" \
  -F "live_frames=@frame2.jpg" \
  -F "live_frames=@frame3.jpg" \
  -F "live_frames=@frame4.jpg" \
  -F "live_frames=@frame5.jpg" \
  -F "challenge=blink"
```

## How teammates plug in their modules

Each teammate:
1. Writes their logic as plain Python functions inside their `services/<module>/` folder — no FastAPI code, just functions that take inputs and return results (mirrors how `liveness.py` and `face_match.py` are written).
2. Creates a router file in `routers/<module>.py` that imports their service functions and exposes them as endpoints (mirrors `face_verification.py`).
3. You (backend owner) add one line in `main.py`: `app.include_router(their_module.router)`.
4. You wire their service functions into `pipeline.py` to contribute to `overall_risk_score`.

This keeps merge conflicts low — everyone mostly touches their own folder,
and `main.py` only needs a one-line addition per teammate.

## Git workflow suggestion

- One shared repo, `main` branch protected.
- Each person works on a feature branch (`feature/module1-ocr`, `feature/module4-face`, etc.), PRs into `main`.
- You review/merge PRs since you own integration — catches import path issues early instead of at 2am before demo day.
