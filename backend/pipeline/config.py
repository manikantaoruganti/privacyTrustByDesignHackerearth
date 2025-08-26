import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self, config_data: Dict[str, Any]):
        self.data = config_data
    
    @classmethod
    def load(cls, config_path: str = "configs/default.yaml"):
        """Load configuration from YAML file"""
        config_file = Path(__file__).parent.parent / config_path
        
        # Default configuration if file doesn't exist
        default_config = {
            "ocr": {
                "lang": "en",
                "min_confidence": 0.5
            },
            "layout": {
                "score_threshold": 0.25
            },
            "ner": {
                "min_confidence": 0.6,
                "enable_rules": True
            },
            "visual": {
                "face_threshold": 0.5,
                "signature_threshold": 0.35
            },
            "redaction": {
                "padding_px": 4,
                "mode": "mask"
            },
            "io": {
                "max_pdf_mb": 200,
                "use_ramdisk": True
            },
            "logs": {
                "level": "INFO",
                "audit_enabled": True
            }
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(config_data)
        
        return cls(default_config)
    
    def get(self, key: str, default=None):
        """Get configuration value by dot notation"""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def policies(self) -> Dict[str, str]:
        """Load redaction policies"""
        policies_file = Path(__file__).parent.parent / "configs" / "policies.yaml"
        
        default_policies = {
            "PERSON": "mask",
            "PHONE": "replace",
            "EMAIL": "mask",
            "AADHAAR": "mask",
            "PAN": "mask",
            "IFSC": "mask",
            "ACCOUNT_NO": "mask",
            "SIGNATURE": "blur",
            "FACE": "blur",
            "STAMP": "mask",
            "DATE": "mask",
            "ORG": "mask"
        }
        
        if policies_file.exists():
            with open(policies_file, 'r') as f:
                policies = yaml.safe_load(f)
                default_policies.update(policies)
        
        return default_policies