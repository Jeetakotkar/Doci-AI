from pydantic import BaseModel, Field
from enum import Enum


class ChallengeTypeSchema(str, Enum):
    BLINK = "blink"
    HEAD_TURN = "head_turn"


class Verdict(str, Enum):
    VERIFIED = "VERIFIED"                 # face matches + liveness passed
    FACE_MISMATCH = "FACE_MISMATCH"       # liveness passed, but face doesn't match doc
    LIVENESS_FAILED = "LIVENESS_FAILED"   # spoof suspected — don't even trust the match
    ERROR = "ERROR"                       # couldn't process (bad image, no face found, etc.)


class LivenessResponse(BaseModel):
    passed: bool
    challenge: str
    confidence: float
    reason: str
    frames_with_face: int
    frames_total: int


class FaceMatchResponse(BaseModel):
    matched: bool
    similarity: float
    distance: float
    threshold: float
    reason: str


class Module4Response(BaseModel):
    verdict: Verdict
    risk_score: float = Field(..., description="0 (safe) to 100 (high risk) — feeds into overall document risk score")
    liveness: LivenessResponse | None = None
    face_match: FaceMatchResponse | None = None
    message: str
