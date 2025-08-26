import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

from .models import ProcessResult, PIIDetection, AuditEntry, PIIType
from .pii_text import TextPIIDetector
from .pii_visual import VisualPIIDetector
from .redaction import RedactionEngine
from .config import Config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.text_detector = TextPIIDetector(config)
        self.visual_detector = VisualPIIDetector(config)
        self.redaction_engine = RedactionEngine(config)
    
    async def process_document(self, file_path: str, filename: str) -> ProcessResult:
        """Process a document and return results"""
        logger.info(f"Processing document: {filename}")
        
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            return await self._process_pdf(file_path, filename)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            return await self._process_image(file_path, filename)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    async def _process_pdf(self, file_path: str, filename: str) -> ProcessResult:
        """Process PDF document"""
        import fitz  # PyMuPDF
        
        detections = []
        audit_entries = []
        
        try:
            # Open PDF
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Extract text and images from page
                text_blocks = page.get_text("dict")
                page_image = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                
                # Detect text PII
                page_text = page.get_text()
                text_detections = await self.text_detector.detect_pii(
                    page_text, page_num
                )
                detections.extend(text_detections)
                
                # Detect visual PII (convert page to image)
                img_data = page_image.tobytes()
                visual_detections = await self.visual_detector.detect_pii(
                    img_data, page_num
                )
                detections.extend(visual_detections)
            
            doc.close()
            
            # Create audit entries
            for detection in detections:
                audit_entries.append(AuditEntry(
                    pii_type=detection.pii_type.value,
                    method=self.config.policies.get(detection.pii_type.value, "mask"),
                    bbox={
                        "x": detection.bbox.x,
                        "y": detection.bbox.y,
                        "width": detection.bbox.width,
                        "height": detection.bbox.height
                    },
                    page=detection.page,
                    confidence=detection.confidence,
                    timestamp=datetime.now().isoformat()
                ))
            
            # Apply redaction
            output_path = await self.redaction_engine.redact_pdf(
                file_path, detections, filename
            )
            
            # Create summary
            summary = self._create_summary(detections, total_pages)
            
            return ProcessResult(
                job_id="",  # Will be set by caller
                filename=filename,
                total_pages=total_pages,
                detections_count=len(detections),
                audit_entries=audit_entries,
                output_path=output_path,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    async def _process_image(self, file_path: str, filename: str) -> ProcessResult:
        """Process image file"""
        from PIL import Image
        
        detections = []
        audit_entries = []
        
        try:
            # Open image
            with Image.open(file_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Detect text PII (OCR first)
                # For now, skip OCR and focus on visual PII
                
                # Detect visual PII
                img_bytes = img.tobytes()
                visual_detections = await self.visual_detector.detect_pii(
                    img_bytes, 0
                )
                detections.extend(visual_detections)
            
            # Create audit entries
            for detection in detections:
                audit_entries.append(AuditEntry(
                    pii_type=detection.pii_type.value,
                    method=self.config.policies.get(detection.pii_type.value, "mask"),
                    bbox={
                        "x": detection.bbox.x,
                        "y": detection.bbox.y,
                        "width": detection.bbox.width,
                        "height": detection.bbox.height
                    },
                    page=detection.page,
                    confidence=detection.confidence,
                    timestamp=datetime.now().isoformat()
                ))
            
            # Apply redaction
            output_path = await self.redaction_engine.redact_image(
                file_path, detections, filename
            )
            
            # Create summary
            summary = self._create_summary(detections, 1)
            
            return ProcessResult(
                job_id="",
                filename=filename,
                total_pages=1,
                detections_count=len(detections),
                audit_entries=audit_entries,
                output_path=output_path,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise
    
    def _create_summary(self, detections: List[PIIDetection], total_pages: int) -> Dict[str, Any]:
        """Create processing summary"""
        pii_counts = {}
        for detection in detections:
            pii_type = detection.pii_type.value
            pii_counts[pii_type] = pii_counts.get(pii_type, 0) + 1
        
        return {
            "total_pages": total_pages,
            "total_detections": len(detections),
            "pii_types_found": list(pii_counts.keys()),
            "pii_counts": pii_counts,
            "processing_complete": True
        }