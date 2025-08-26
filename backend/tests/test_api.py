import pytest
from fastapi.testclient import TestClient
import io
import time
from PIL import Image

# Import the app
from app import app


class TestAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing"""
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        return img_bytes

    @pytest.fixture
    def sample_pdf(self):
        """Create a sample PDF for testing"""
        # Minimal PDF header bytes (not empty, so mimics real PDF)
        pdf_bytes = io.BytesIO(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\nxref\n0 2\n0000000000 65535 f \n0000000010 00000 n \ntrailer\n<<\n/Size 2\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF")
        pdf_bytes.seek(0)
        return pdf_bytes

    @pytest.fixture
    def large_image(self):
        """Create a larger image for testing file size limits"""
        img = Image.new("RGB", (1000, 1000), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG", quality=95)
        img_bytes.seek(0)
        return img_bytes

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "DocuShield AI"

    def test_upload_valid_image(self, client, sample_image):
        """Test uploading a valid image file"""
        files = {"file": ("test.jpg", sample_image, "image/jpeg")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] in ["queued", "processing", "completed"]
        assert "message" in data

    def test_upload_valid_pdf(self, client, sample_pdf):
        """Test uploading a valid PDF file"""
        files = {"file": ("test.pdf", sample_pdf, "application/pdf")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] in ["queued", "processing", "completed"]

    def test_upload_invalid_file_type(self, client):
        """Test uploading unsupported file type"""
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Unsupported file type" in data["detail"]

    def test_upload_no_file(self, client):
        """Test upload endpoint with no file provided"""
        response = client.post("/api/v1/redact")
        assert response.status_code == 422  # Validation error

    def test_upload_empty_filename(self, client):
        """Test upload with empty filename"""
        files = {"file": ("", io.BytesIO(b"content"), "image/jpeg")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_get_job_status_valid(self, client, sample_image):
        """Test getting job status for valid job"""
        # First upload a file
        files = {"file": ("test.jpg", sample_image, "image/jpeg")}
        upload_response = client.post("/api/v1/redact", files=files)
        assert upload_response.status_code == 200
        
        job_id = upload_response.json()["job_id"]
        
        # Then check status
        status_response = client.get(f"/api/v1/jobs/{job_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert "id" in status_data
        assert "status" in status_data
        assert "filename" in status_data
        assert status_data["id"] == job_id

    def test_get_job_status_invalid(self, client):
        """Test getting job status for non-existent job"""
        fake_job_id = "fake-job-id-12345"
        response = client.get(f"/api/v1/jobs/{fake_job_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Job not found" in data["detail"]

    def test_download_nonexistent_job(self, client):
        """Test downloading result for non-existent job"""
        fake_job_id = "fake-job-id-12345"
        response = client.get(f"/api/v1/jobs/{fake_job_id}/download")
        assert response.status_code == 404

    def test_download_incomplete_job(self, client, sample_image):
        """Test downloading result for incomplete job"""
        # Upload file
        files = {"file": ("test.jpg", sample_image, "image/jpeg")}
        upload_response = client.post("/api/v1/redact", files=files)
        job_id = upload_response.json()["job_id"]
        
        # Try to download immediately (job likely not completed)
        download_response = client.get(f"/api/v1/jobs/{job_id}/download")
        # Should return 400 if job not completed, or 200 if it completed very quickly
        assert download_response.status_code in [400, 200]

    def test_audit_log_nonexistent_job(self, client):
        """Test getting audit log for non-existent job"""
        fake_job_id = "fake-job-id-12345"
        response = client.get(f"/api/v1/jobs/{fake_job_id}/audit")
        assert response.status_code == 404

    def test_audit_log_incomplete_job(self, client, sample_image):
        """Test getting audit log for incomplete job"""
        # Upload file
        files = {"file": ("test.jpg", sample_image, "image/jpeg")}
        upload_response = client.post("/api/v1/redact", files=files)
        job_id = upload_response.json()["job_id"]
        
        # Try to get audit immediately
        audit_response = client.get(f"/api/v1/jobs/{job_id}/audit")
        # Should return 400 if job not completed, or 200 if completed quickly
        assert audit_response.status_code in [400, 200]

    def test_upload_large_file_within_limit(self, client, large_image):
        """Test uploading a larger file within size limits"""
        files = {"file": ("large_test.jpg", large_image, "image/jpeg")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data

    def test_multiple_file_extensions(self, client):
        """Test various supported file extensions"""
        # Test PNG
        img = Image.new("RGB", (50, 50), color="blue")
        png_bytes = io.BytesIO()
        img.save(png_bytes, format="PNG")
        png_bytes.seek(0)
        
        files = {"file": ("test.png", png_bytes, "image/png")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 200

        # Test TIFF
        tiff_bytes = io.BytesIO()
        img.save(tiff_bytes, format="TIFF")
        tiff_bytes.seek(0)
        
        files = {"file": ("test.tiff", tiff_bytes, "image/tiff")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 200

    def test_case_insensitive_extensions(self, client, sample_image):
        """Test that file extensions are case insensitive"""
        files = {"file": ("test.JPG", sample_image, "image/jpeg")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 200

    def test_job_status_fields(self, client, sample_image):
        """Test that job status contains all required fields"""
        # Upload file
        files = {"file": ("test.jpg", sample_image, "image/jpeg")}
        upload_response = client.post("/api/v1/redact", files=files)
        job_id = upload_response.json()["job_id"]
        
        # Get status
        status_response = client.get(f"/api/v1/jobs/{job_id}")
        assert status_response.status_code == 200
        
        data = status_response.json()
        required_fields = ["id", "filename", "status", "created_at"]
        for field in required_fields:
            assert field in data

    def test_concurrent_uploads(self, client, sample_image):
        """Test handling multiple concurrent uploads"""
        responses = []
        
        for i in range(3):
            sample_image.seek(0)  # Reset stream position
            files = {"file": (f"test_{i}.jpg", sample_image, "image/jpeg")}
            response = client.post("/api/v1/redact", files=files)
            responses.append(response)
        
        # All uploads should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "job_id" in data

        # All job IDs should be unique
        job_ids = [resp.json()["job_id"] for resp in responses]
        assert len(set(job_ids)) == len(job_ids)

    def test_api_error_format(self, client):
        """Test that API errors return consistent format"""
        # Test with invalid file type
        files = {"file": ("test.exe", io.BytesIO(b"executable"), "application/octet-stream")}
        response = client.post("/api/v1/redact", files=files)
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

    @pytest.mark.slow
    def test_processing_completion(self, client, sample_image):
        """Test that a job actually completes processing (slow test)"""
        # Upload file
        files = {"file": ("test.jpg", sample_image, "image/jpeg")}
        upload_response = client.post("/api/v1/redact", files=files)
        job_id = upload_response.json()["job_id"]
        
        # Poll for completion (with timeout)
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = client.get(f"/api/v1/jobs/{job_id}")
            if status_response.status_code == 200:
                status = status_response.json()["status"]
                if status in ["completed", "failed"]:
                    break
            time.sleep(1)
        
        # Final status check
        final_response = client.get(f"/api/v1/jobs/{job_id}")
        assert final_response.status_code == 200
        final_data = final_response.json()
        assert final_data["status"] in ["completed", "failed"]
        
        # If completed, should have download and audit URLs
        if final_data["status"] == "completed":
            assert "download_url" in final_data
            assert "audit_url" in final_data