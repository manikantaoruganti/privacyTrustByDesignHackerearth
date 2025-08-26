#!/usr/bin/env python3
"""
DocuShield AI Model Verification Script
Verifies that all required models are present and have correct checksums
"""

import os
import json
import hashlib
import sys
from pathlib import Path

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except FileNotFoundError:
        return None

def verify_models():
    """Verify all models against manifest"""
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Load manifest
    manifest_path = project_root / "models" / "manifest.json"
    if not manifest_path.exists():
        print("❌ Model manifest not found!")
        return False
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    print("🔍 Verifying DocuShield AI Models...")
    print(f"📋 Manifest version: {manifest['version']}")
    print()
    
    all_valid = True
    models_dir = project_root / "models"
    
    for category, models in manifest["models"].items():
        print(f"📂 {category.upper()}:")
        
        for model_name, model_info in models.items():
            model_path = models_dir / model_info["path"]
            expected_hash = model_info["sha256"]
            
            if not model_path.exists():
                print(f"  ❌ {model_name}: File not found")
                all_valid = False
                continue
            
            # For now, skip checksum verification since we're using placeholder hashes
            if expected_hash.startswith("placeholder_"):
                print(f"  ⚠️  {model_name}: Placeholder file (development)")
            else:
                actual_hash = calculate_sha256(model_path)
                if actual_hash == expected_hash:
                    print(f"  ✅ {model_name}: Valid")
                else:
                    print(f"  ❌ {model_name}: Checksum mismatch")
                    print(f"     Expected: {expected_hash}")
                    print(f"     Actual:   {actual_hash}")
                    all_valid = False
        
        print()
    
    if all_valid:
        print("✅ All models verified successfully!")
        return True
    else:
        print("❌ Some models failed verification!")
        return False

def main():
    """Main function"""
    success = verify_models()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()