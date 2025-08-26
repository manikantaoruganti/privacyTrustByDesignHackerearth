from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class PIIType(Enum):
    PERSON = "PERSON"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    IFSC = "IFSC"
    ACCOUNT_NO = "ACCOUNT_NO"
    FACE = "FACE"
    SIGNATURE = "SIGNATURE"
    STAMP = "STAMP"
    DATE = "DATE"
    ORG = "ORG"

class RedactionMethod(Enum):
    MASK = "mask"
    BLUR = "blur"
    REPLACE = "replace"
    REMOVE = "remove"

@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int

@dataclass
class PIIDetection:
    text: str
    pii_type: PIIType
    confidence: float
    bbox: BoundingBox
    page: int = 0

@dataclass
class AuditEntry:
    pii_type: str
    method: str
    bbox: Dict[str, int]
    page: int
    confidence: float
    timestamp: str

@dataclass
class ProcessResult:
    job_id: str
    filename: str
    total_pages: int
    detections_count: int
    audit_entries: List[AuditEntry]
    output_path: str
    summary: Dict[str, Any]

class JobStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"