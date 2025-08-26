import pytest
from pipeline.pii_text import TextPIIDetector
from pipeline.config import Config
from pipeline.models import PIIType

class TestTextPIIDetector:
    
    @pytest.fixture
    def detector(self):
        config = Config.load()
        return TextPIIDetector(config)
    
    def test_aadhaar_detection(self, detector):
        """Test Aadhaar number detection"""
        text = "My Aadhaar number is 1234 5678 9012"
        detections = detector.detect_pii(text, 0)
        
        aadhaar_detections = [d for d in detections if d.pii_type == PIIType.AADHAAR]
        assert len(aadhaar_detections) == 1
        assert aadhaar_detections[0].text == "1234 5678 9012"
    
    def test_pan_detection(self, detector):
        """Test PAN number detection"""  
        text = "PAN: ABCDE1234F"
        detections = detector.detect_pii(text, 0)
        
        pan_detections = [d for d in detections if d.pii_type == PIIType.PAN]
        assert len(pan_detections) == 1
        assert pan_detections[0].text == "ABCDE1234F"
    
    def test_email_detection(self, detector):
        """Test email detection"""
        text = "Contact me at john.doe@example.com for details"
        detections = detector.detect_pii(text, 0)
        
        email_detections = [d for d in detections if d.pii_type == PIIType.EMAIL]
        assert len(email_detections) == 1
        assert email_detections[0].text == "john.doe@example.com"
    
    def test_phone_detection(self, detector):
        """Test phone number detection"""
        text = "Call me at +91 9876543210 or 9876543210"
        detections = detector.detect_pii(text, 0)
        
        phone_detections = [d for d in detections if d.pii_type == PIIType.PHONE]
        assert len(phone_detections) == 2
    
    def test_no_false_positives(self, detector):
        """Test that normal text doesn't trigger false positives"""
        text = "This is a normal sentence with no PII information."
        detections = detector.detect_pii(text, 0)
        
        assert len(detections) == 0
    
    def test_multiple_pii_types(self, detector):
        """Test detection of multiple PII types in same text"""
        text = """
        Name: John Doe
        Email: john@example.com  
        Phone: 9876543210
        Aadhaar: 1234 5678 9012
        PAN: ABCDE1234F
        """
        
        detections = detector.detect_pii(text, 0)
        
        # Should detect at least email, phone, aadhaar, pan
        pii_types = {d.pii_type for d in detections}
        expected_types = {PIIType.EMAIL, PIIType.PHONE, PIIType.AADHAAR, PIIType.PAN}
        
        assert expected_types.issubset(pii_types)
    
    def test_pan_validation(self, detector):
        """Test PAN validation"""
        assert detector.validate_pan("ABCDE1234F") == True
        assert detector.validate_pan("INVALID123") == False
        assert detector.validate_pan("12345ABCDE") == False
    
    def test_aadhaar_validation(self, detector):
        """Test Aadhaar validation"""
        assert detector.validate_aadhaar("123456789012") == True
        assert detector.validate_aadhaar("1234 5678 9012") == True
        assert detector.validate_aadhaar("12345") == False
        assert detector.validate_aadhaar("abcd efgh ijkl") == False

if __name__ == "__main__":
    pytest.main([__file__])