import { JobStatus, ProcessResult, UploadResponse, ApiError } from './types';

const API_BASE = '/api/v1';

class ApiClient {
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/redact`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to get job status');
    }

    return response.json();
  }

  async getAuditLog(jobId: string): Promise<{ audit_entries: any[]; summary: any }> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}/audit`);

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to get audit log');
    }

    return response.json();
  }

  async downloadResult(jobId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/jobs/${jobId}/download`);

    if (!response.ok) {
      throw new Error('Download failed');
    }

    return response.blob();
  }

  async checkHealth(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${API_BASE}/health`);

    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }
}

export const apiClient = new ApiClient();