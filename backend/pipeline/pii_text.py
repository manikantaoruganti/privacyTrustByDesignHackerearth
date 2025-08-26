import re
from typing import List
import logging

from .models import PIIDetection, PIIType, BoundingBox
from .config import Config

logger = logging.getLogger(__name__)

class TextPIIDetector:
    def __init__(self, config: Config):
        self.config = config
        self.min_confidence = config.get("ner.min_confidence", 0.6)
        
        # Define regex patterns for Indian PII
        self.patterns = {
            PIIType.AADHAAR: r'\b\d{4}\s?\d{4}\s?\d{4}\b',
            PIIType.PAN: r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
            PIIType.IFSC: r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
            PIIType.PHONE: r'\b(?:\+?91[- ]?)?[6-9]\d{9}\b',
            PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            PIIType.ACCOUNT_NO: r'\b\d{9,18}\b',
            PIIType.DATE: r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        }
        
        # Common Indian names and organizations for basic NER
        self.name_indicators = [
            'mr', 'mrs', 'ms', 'dr', 'prof', 'shri', 'smt', 'kumar', 'singh', 'sharma', 'gupta'
        ]
        
        self.org_indicators = [
            'ltd', 'limited', 'pvt', 'private', 'corp', 'corporation', 'inc', 'company', 'bank', 'hospital'
        ]
    
    async def detect_pii(self, text: str, page_num: int = 0) -> List[PIIDetection]:
        """Detect PII in text using regex patterns and simple NER"""
        detections = []
        
        # Apply regex patterns
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Create a simple bounding box (would need OCR coordinates in real implementation)
                bbox = BoundingBox(
                    x=0,  # Would get from OCR
                    y=0,
                    width=len(match.group()) * 10,  # Estimated
                    height=20
                )
                
                detection = PIIDetection(
                    text=match.group(),
                    pii_type=pii_type,
                    confidence=0.9,  # High confidence for regex matches
                    bbox=bbox,
                    page=page_num
                )
                detections.append(detection)
        
        # Simple person name detection
        words = text.split()
        for i, word in enumerate(words):
            # Check for name indicators
            if word.lower() in self.name_indicators:
                # Next word might be a name
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word.istitle() and len(next_word) > 2:
                        bbox = BoundingBox(x=0, y=0, width=len(next_word) * 10, height=20)
                        detection = PIIDetection(
                            text=next_word,
                            pii_type=PIIType.PERSON,
                            confidence=0.7,
                            bbox=bbox,
                            page=page_num
                        )
                        detections.append(detection)
        
        # Simple organization detection
        for i, word in enumerate(words):
            if word.lower() in self.org_indicators:
                # Previous words might be org name
                start_idx = max(0, i - 3)
                org_words = words[start_idx:i + 1]
                org_name = ' '.join(org_words)
                
                bbox = BoundingBox(x=0, y=0, width=len(org_name) * 8, height=20)
                detection = PIIDetection(
                    text=org_name,
                    pii_type=PIIType.ORG,
                    confidence=0.6,
                    bbox=bbox,
                    page=page_num
                )
                detections.append(detection)
        
        logger.info(f"Detected {len(detections)} PII items in text")
        return detections
    
    def validate_aadhaar(self, aadhaar: str) -> bool:
        """Validate Aadhaar number using simple checksum"""
        # Remove spaces
        aadhaar = re.sub(r'\s', '', aadhaar)
        
        if len(aadhaar) != 12 or not aadhaar.isdigit():
            return False
        
        # Simple validation (not the actual Aadhaar algorithm)
        return True
    
    def validate_pan(self, pan: str) -> bool:
        """Validate PAN format"""
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
        return bool(re.match(pattern, pan))