# DocuShield AI 🛡️

**Privacy-Preserving Document Deidentification Pipeline**

DocuShield AI is a comprehensive, offline-first solution for detecting and redacting personally identifiable information (PII) from documents and images. Built with privacy by design, all processing happens locally without sending data to external servers.

## 🌟 Features

### Document Processing
- **PDF Support**: Both text-based and scanned documents
- **Image Support**: JPG, PNG, TIFF formats  
- **Streaming**: Memory-efficient processing for large files (>50MB)
- **Multi-page**: Batch processing with progress tracking

### PII Detection
- **Text PII**: Names, emails, phones, Indian IDs (Aadhaar, PAN, IFSC)
- **Visual PII**: Faces, signatures, stamps using computer vision
- **OCR**: Optical character recognition for scanned documents
- **Custom Rules**: Configurable regex patterns and validation

### Redaction Methods
- **Masking**: Black rectangles over sensitive areas
- **Blurring**: Gaussian blur for visual elements
- **Replacement**: Placeholder text substitution
- **Removal**: Complete deletion of content

### Privacy & Security
- **Offline Operation**: No external API calls or data transmission
- **In-Memory Processing**: Optional temporary disk storage
- **Audit Logging**: Detailed tracking without storing raw content
- **Secure Deletion**: Buffer overwriting after processing

## 🚀 Quick Start

### Option 1: Local Installation (Recommended)

#### Linux/macOS
```bash
git clone <repository-url>
cd DocuShieldAI

# Make scripts executable
chmod +x scripts/*.sh

# Run the application
./scripts/run_local_linux.sh
```

#### Windows
```powershell
git clone <repository-url>
cd DocuShieldAI

# Run the application  
powershell -ExecutionPolicy Bypass -File scripts\run_local_windows.ps1
```

### Option 2: Docker

```bash
# Build and run
docker build -t docushield-ai .
docker run -p 8080:8080 docushield-ai

# Or use docker-compose
docker-compose up --build
```

### Option 3: Docker Compose (Production)

```bash
docker-compose up -d
```

## 🌐 Access

After starting the application:
- **Web Interface**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/api/v1/health

## 📖 Usage

### Web Interface

1. **Upload**: Drag and drop files or click to browse
2. **Configure**: Adjust redaction policies in Settings
3. **Process**: Monitor real-time progress
4. **Download**: Get redacted files and audit logs

### REST API

```bash
# Upload and process document
curl -X POST "http://localhost:8080/api/v1/redact" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"

# Check processing status  
curl "http://localhost:8080/api/v1/jobs/{job_id}"

# Download redacted file
curl "http://localhost:8080/api/v1/jobs/{job_id}/download" \
     --output redacted_document.pdf
```

### Command Line Interface

```bash
# Single file
python -m backend.cli redact document.pdf --out ./output/

# Batch processing
python -m backend.cli redact ./input/ --out ./output/ --recursive

# With custom policies
python -m backend.cli redact ./input/ \
    --policy configs/policies.yaml \
    --audit audit.json \
    --recursive
```

## ⚙️ Configuration

### Redaction Policies (`configs/policies.yaml`)
```yaml
PERSON: mask          # Names
PHONE: replace        # Phone numbers  
EMAIL: mask           # Email addresses
AADHAAR: mask         # Aadhaar numbers
PAN: mask             # PAN numbers
FACE: blur            # Facial images
SIGNATURE: blur       # Signatures
```

### Detection Thresholds (`configs/default.yaml`)
```yaml
ocr:
  min_confidence: 0.5
ner:
  min_confidence: 0.6  
visual:
  face_threshold: 0.5
  signature_threshold: 0.35
redaction:
  padding_px: 4
```

## 🧪 Testing

```bash
# Run backend tests
cd backend
python -m pytest tests/

# Run frontend tests  
cd frontend
npm test

# Run end-to-end tests
python -m pytest tests/integration/

# Verify models
python scripts/verify_models.py
```

## 📁 Project Structure

```
DocuShieldAI/
├── backend/                    # FastAPI backend
│   ├── app.py                 # Main application
│   ├── pipeline/              # Processing pipeline
│   │   ├── processor.py       # Document processor
│   │   ├── pii_text.py        # Text PII detection
│   │   ├── pii_visual.py      # Visual PII detection  
│   │   └── redaction.py       # Redaction engine
│   ├── configs/               # Configuration files
│   └── tests/                 # Test suites
├── frontend/                  # React frontend
│   ├── src/                   # Source code
│   ├── dist/                  # Built assets (committed)
│   └── public/                # Static assets
├── models/                    # ML models (vendored)
│   ├── manifest.json          # Model checksums
│   ├── paddleocr/             # OCR models
│   ├── spacy/                 # NLP models
│   └── visual/                # Computer vision models
├── scripts/                   # Utility scripts
├── assets/                    # Sample files and fonts
└── docs/                      # Documentation
```

## 🛠️ Development

### Requirements
- Python 3.10+
- Node.js 18+
- Docker (optional)

### Setup Development Environment
```bash
# Backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

pip install -r backend/requirements.txt

# Frontend  
cd frontend
npm install
npm run dev

# Build frontend for production
npm run build
```

### Model Management
Models are vendored locally for offline operation:
- Verify with: `python scripts/verify_models.py`
- Models stored in `models/` directory
- Checksums tracked in `models/manifest.json`

## 📊 Performance

- **Memory Usage**: < 2GB for typical documents
- **Processing Speed**: ~30 seconds for 50-page PDF
- **File Size Limit**: 200MB (configurable)
- **Concurrent Jobs**: CPU core limited

## 🔒 Security Features

- **No External Calls**: All processing happens locally
- **Memory Safety**: Secure buffer management
- **Audit Trails**: Comprehensive logging without content storage
- **Input Validation**: File type and size restrictions
- **Error Handling**: Graceful failure without data leaks

## 🌍 Internationalization

Current support:
- **English**: Full text and visual PII detection
- **Indian Languages**: Aadhaar, PAN, IFSC pattern recognition

Planned support:
- Hindi, Bengali text processing
- Additional regional ID formats

## 📈 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8080/api/v1/health

# Model verification  
python scripts/verify_models.py
```

### Metrics
- Processing throughput
- Memory usage
- Detection accuracy
- Error rates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)  
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend
- Add tests for new features
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: `/docs` directory
- **Security**: See [SECURITY.md](SECURITY.md)

## 🏆 Acknowledgments

- PaddleOCR for OCR capabilities
- spaCy for natural language processing
- FastAPI for the web framework
- React for the user interface

---

**Built with Privacy in Mind** 🔒  
DocuShield AI processes your documents locally, ensuring your sensitive data never leaves your system.