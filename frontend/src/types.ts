export interface JobStatus {
  id: string;
  filename: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  created_at: number;
  error?: string;
  download_url?: string;
  audit_url?: string;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface AuditEntry {
  pii_type: string;
  method: string;
  bbox: BoundingBox;
  page: number;
  confidence: number;
  timestamp: string;
}

export interface ProcessResult {
  job_id: string;
  filename: string;
  total_pages: number;
  detections_count: number;
  audit_entries: AuditEntry[];
  summary: {
    total_pages: number;
    total_detections: number;
    pii_types_found: string[];
    pii_counts: Record<string, number>;
    processing_complete: boolean;
  };
}

export interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface ApiError {
  detail: string;
}