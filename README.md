# DOCX to PDF Converter API

This service provides API to convert DOCX files to PDF format using LibreOffice

## Quick Start

1. **Start the service:**
   ```bash
   docker compose up --build
   ```

2. **Convert a single file:**
   ```bash
   curl -X POST "http://localhost:8000/convert" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@your-document.docx" \
     --output "converted.pdf"
   ```

3. **Access API documentation:**
   Open http://localhost:8000/docs in your browser

## Run Steps

1. Run `docker compose up --build` to start the service using docker

## API Examples

### Single File Conversion

```bash
# Convert a single DOCX file to PDF
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/document.docx" \
  --output "converted.pdf"

# Using the single file endpoint
curl -X POST "http://localhost:8000/convert/single" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/document.docx" \
  --output "converted.pdf"
```

### Multiple Files Conversion

```bash
# Convert multiple files (returns ZIP archive)
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.docx" \
  -F "files=@document2.docx" \
  -F "files=@document3.doc" \
  --output "converted_files.zip"
```

### Health Check

```bash
# Check service health
curl http://localhost:8000/healthcheck

# Expected response:
# {"status":"healthy","service":"doc2pdf-converter"}
```

### Service Information

```bash
# Get service information and available endpoints
curl http://localhost:8000/

# Expected response includes:
# - Service description
# - Available endpoints
# - Supported file formats
# - Response types
```

### Supported File Formats

- `.docx` - Microsoft Word Document
- `.doc` - Microsoft Word 97-2003 Document
- `.odt` - OpenDocument Text
- `.rtf` - Rich Text Format

### Response Types

| Scenario | Response Type | Content-Type | Description |
|----------|---------------|--------------|-------------|
| Single file | PDF file | `application/pdf` | Direct PDF file download |
| Multiple files | ZIP archive | `application/zip` | ZIP containing all converted PDFs |

### Error Responses

#### Invalid File Type

```json
{
  "detail": "Invalid file type 'document.txt'. Allowed extensions: .docx, .doc, .odt, .rtf"
}
```

#### File Too Large

```json
{
  "detail": "File size exceeds maximum allowed size"
}
```

#### Conversion Error

```json
{
  "detail": "Internal server error: LibreOffice conversion failed"
}
```

