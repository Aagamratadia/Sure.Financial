# Credit Card Statement Parser API

A robust FastAPI-based service that extracts key data points from credit card statements across 5 major card issuers using advanced PDF parsing and OCR support.

## 🚀 Features

- **5 Credit Card Issuers Supported**: Kotak Mahindra Bank, HDFC Bank, ICICI Bank, American Express, Capital One
- **5 Key Data Points Extracted**:
  - Card Issuer
  - Masked Card Number
  - Statement Period (Date Range)
  - Payment Due Date
  - Total Amount Due
- **Multiple Parsing Engines**: PyMuPDF, pdfplumber, Tesseract OCR with intelligent fallback
- **MongoDB Storage**: Async storage for jobs and results
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Confidence Scoring**: Per-field and overall confidence metrics
- **Batch Processing**: Support for multiple file uploads

## 📋 Requirements

- Python 3.11+
- MongoDB 7+
- Tesseract OCR
- Poppler (for pdf2image)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**:
```bash
cd /Users/aagam/Downloads/Sure.Financial
```

2. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Option 2: Local Installation

1. **Install system dependencies**:

**macOS**:
```bash
brew install tesseract poppler libmagic
```

**Ubuntu/Debian**:
```bash
sudo apt-get install tesseract-ocr poppler-utils libmagic1
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up MongoDB**:
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7

# Or install locally
brew install mongodb-community  # macOS
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the application**:
```bash
python -m uvicorn app.main:app --reload
```

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### 1. Upload Statement
```http
POST /api/v1/parse/upload
Content-Type: multipart/form-data

Parameters:
- file: PDF file (required)
- use_ocr: boolean (optional, default: false)

Response: ParseResult with extracted data
```

**Example using cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/parse/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@statement.pdf" \
  -F "use_ocr=false"
```

**Example using Python**:
```python
import requests

url = "http://localhost:8000/api/v1/parse/upload"
files = {"file": open("statement.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### 2. Check Job Status
```http
GET /api/v1/parse/{job_id}/status

Response: JobStatusResponse
```

### 3. Get Results
```http
GET /api/v1/parse/{job_id}/results

Response: ParseResult with extracted data
```

### 4. Batch Upload
```http
POST /api/v1/parse/batch
Content-Type: multipart/form-data

Parameters:
- files: Array of PDF files (max 10)

Response: BatchUploadResponse with job IDs
```

### 5. Health Check
```http
GET /api/v1/health

Response: Service health status
```

## 📊 Response Format

```json
{
  "job_id": "uuid",
  "status": "completed",
  "filename": "statement.pdf",
  "issuer": "HDFC Bank",
  "data": {
    "card_issuer": "HDFC Bank",
    "card_number": "5228 52XX XXXX 0591",
    "statement_period": {
      "raw": "08062019 to 28062019",
      "start_date": "2019-06-08",
      "end_date": "2019-06-28"
    },
    "payment_due_date": {
      "raw": "28062019",
      "formatted": "2019-06-28"
    },
    "total_amount_due": {
      "raw": "Rs. 45,240.00",
      "amount": 45240.0,
      "currency": "INR"
    }
  },
  "confidence_scores": {
    "card_issuer": 1.0,
    "card_number": 1.0,
    "statement_period": 1.0,
    "payment_due_date": 1.0,
    "total_amount_due": 1.0
  },
  "metadata": {
    "pages": 3,
    "processing_time_ms": 1234,
    "parser_used": "pymupdf",
    "ocr_required": false,
    "file_size_bytes": 245760
  },
  "processed_at": "2025-10-23T10:30:05Z"
}
```

## 🏗️ Project Structure

```
Sure.Financial/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── parse.py       # Parsing endpoints
│   │   │   └── health.py      # Health check
│   │   └── router.py          # API router
│   ├── core/
│   │   ├── parsers/           # PDF parsers
│   │   │   ├── pymupdf_parser.py
│   │   │   ├── pdfplumber_parser.py
│   │   │   └── tesseract_parser.py
│   │   ├── extractors/        # Bank-specific extractors
│   │   │   ├── kotak.py
│   │   │   ├── hdfc.py
│   │   │   ├── icici.py
│   │   │   ├── amex.py
│   │   │   └── capital_one.py
│   │   └── orchestrator.py    # Parser orchestration
│   ├── db/
│   │   ├── database.py        # MongoDB connection
│   │   └── repository.py      # Data access layer
│   ├── models/
│   │   ├── schemas.py         # Pydantic models
│   │   └── enums.py           # Enumerations
│   ├── services/
│   │   ├── validation.py      # File validation
│   │   ├── file_service.py    # File management
│   │   └── issuer_detection.py
│   ├── utils/
│   │   ├── date_parser.py     # Date utilities
│   │   ├── amount_parser.py   # Currency parsing
│   │   └── regex_patterns.py  # Regex patterns
│   ├── config.py              # Configuration
│   └── main.py                # FastAPI app
├── tests/
│   └── fixtures/              # Sample PDFs
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🧪 Testing

To test the API, you'll need sample PDF credit card statements. Place them in the `tests/fixtures/` directory.

**Run with sample file**:
```bash
curl -X POST "http://localhost:8000/api/v1/parse/upload" \
  -F "file=@tests/fixtures/hdfc_statement.pdf"
```

## 🔧 Configuration

Edit `.env` or set environment variables:

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=credit_card_parser
MAX_FILE_SIZE=10485760
TEMP_DIR=/tmp/pdf_parser
TESSERACT_DPI=300
DEFAULT_CURRENCY=INR
```

## 📝 Supported Banks

| Bank | Card Number Format | Date Format | Currency |
|------|-------------------|-------------|----------|
| Kotak Mahindra | 414767XXXXXX6705 | DD-MMM-YYYY | INR |
| HDFC Bank | 5228 52XX XXXX 0591 | DDMMYYYY | INR |
| ICICI Bank | XXXX XXXX XXXX 1234 | DD-MMM-YYYY | INR |
| American Express | XXXX-XXXXXX-01007 | Month DD, YYYY | INR |
| Capital One | 4811 | DDMMYYYY | GBP |

## 🚦 Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid file, validation error)
- `404`: Not Found (job_id or results not found)
- `413`: Payload Too Large (file exceeds size limit)
- `500`: Internal Server Error

## 🔒 Security Considerations

- File size limits enforced
- MIME type validation
- PDF structure verification
- Temporary file cleanup
- No permanent storage of uploaded files

## 🎯 Performance

- **Text-based PDFs**: < 2 seconds
- **Image-based PDFs (OCR)**: < 10 seconds
- **Concurrent requests**: 50+ req/sec

## 📈 Future Enhancements

- [ ] Support for more banks
- [ ] Extract transaction details
- [ ] ML-based extraction
- [ ] Background job processing (Celery)
- [ ] Authentication & rate limiting
- [ ] Export to CSV/Excel
- [ ] Web dashboard UI

## 🤝 Contributing

This is a demonstration project. For production use, consider:
- Adding authentication (JWT)
- Implementing rate limiting
- Using Redis for job queue
- Adding comprehensive logging
- Setting up monitoring

## 📄 License

MIT License

## 👨‍💻 Author

Built for Sure.Financial

---

**Questions?** Check the API documentation at `/docs` or contact support.
