import os
import logging
from typing import List
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

from .models import PIIDetection, PIIType
from .config import Config

logger = logging.getLogger(__name__)

class RedactionEngine:
    def __init__(self, config: Config):
        self.config = config
        self.padding_px = config.get("redaction.padding_px", 4)
        self.policies = config.policies
    
    async def redact_pdf(self, input_path: str, detections: List[PIIDetection], filename: str) -> str:
        """Redact PDF document"""
        import fitz  # PyMuPDF
        
        try:
            # Open PDF
            doc = fitz.open(input_path)
            
            # Group detections by page
            page_detections = {}
            for detection in detections:
                page_num = detection.page
                if page_num not in page_detections:
                    page_detections[page_num] = []
                page_detections[page_num].append(detection)
            
            # Apply redaction to each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                if page_num in page_detections:
                    for detection in page_detections[page_num]:
                        method = self.policies.get(detection.pii_type.value, "mask")
                        
                        # Create redaction rectangle
                        rect = fitz.Rect(
                            detection.bbox.x - self.padding_px,
                            detection.bbox.y - self.padding_px,
                            detection.bbox.x + detection.bbox.width + self.padding_px,
                            detection.bbox.y + detection.bbox.height + self.padding_px
                        )
                        
                        if method == "mask":
                            # Add black rectangle
                            page.add_redact_annot(rect, fill=(0, 0, 0))
                        elif method == "blur":
                            # For blur, we'd need to rasterize and blur the region
                            page.add_redact_annot(rect, fill=(0.8, 0.8, 0.8))
                        elif method == "replace":
                            # Replace with placeholder text
                            page.add_redact_annot(rect, text="[REDACTED]", fill=(1, 1, 1))
                
                # Apply redactions
                page.apply_redactions()
            
            # Save redacted PDF
            job_id = os.path.basename(input_path).split('_')[0]
            output_path = f"output/{job_id}_redacted_{filename}"
            doc.save(output_path)
            doc.close()
            
            logger.info(f"PDF redaction completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error redacting PDF: {str(e)}")
            raise
    
    async def redact_image(self, input_path: str, detections: List[PIIDetection], filename: str) -> str:
        """Redact image file"""
        try:
            # Open image
            with Image.open(input_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create drawing context
                draw = ImageDraw.Draw(img)
                
                # Apply redactions
                for detection in detections:
                    method = self.policies.get(detection.pii_type.value, "mask")
                    
                    # Calculate coordinates with padding
                    x1 = max(0, detection.bbox.x - self.padding_px)
                    y1 = max(0, detection.bbox.y - self.padding_px)
                    x2 = min(img.width, detection.bbox.x + detection.bbox.width + self.padding_px)
                    y2 = min(img.height, detection.bbox.y + detection.bbox.height + self.padding_px)
                    
                    if method == "mask":
                        # Draw black rectangle
                        draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))
                    elif method == "blur":
                        # Extract region, blur it, and paste back
                        region = img.crop((x1, y1, x2, y2))
                        blurred = region.filter(ImageFilter.GaussianBlur(radius=10))
                        img.paste(blurred, (x1, y1))
                    elif method == "replace":
                        # Draw white rectangle
                        draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255))
                
                # Save redacted image
                job_id = os.path.basename(input_path).split('_')[0]
                output_path = f"output/{job_id}_redacted_{filename}"
                img.save(output_path)
            
            logger.info(f"Image redaction completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error redacting image: {str(e)}")
            raise
    
    def _apply_pixelation(self, img: Image.Image, x1: int, y1: int, x2: int, y2: int, pixel_size: int = 10) -> None:
        """Apply pixelation to a region"""
        # Extract region
        region = img.crop((x1, y1, x2, y2))
        
        # Resize down and up to create pixelation effect
        small = region.resize(
            (max(1, region.width // pixel_size), max(1, region.height // pixel_size)),
            Image.Resampling.NEAREST
        )
        pixelated = small.resize(region.size, Image.Resampling.NEAREST)
        
        # Paste back
        img.paste(pixelated, (x1, y1))