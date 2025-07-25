#!/usr/bin/env python3
"""
FastAPI application for DOCX to PDF conversion using LibreOffice
"""

from fastapi import FastAPI
from src.convert import router as convert_router

# Create FastAPI application
app = FastAPI(
    title="Doc2PDF Converter",
    description="Convert DOCX files to PDF using LibreOffice",
    version="1.0.0"
)

# Include the convert router
app.include_router(convert_router)

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Doc2PDF Converter",
        "version": "1.0.0",
        "description": "Upload single or multiple documents to convert to PDF",
        "endpoints": {
            "convert": "POST /convert - Upload single or multiple files (.docx, .doc, .odt, .rtf)",
            "healthcheck": "GET /healthcheck - Health check endpoint"
        },
        "supported_formats": [".docx", ".doc", ".odt", ".rtf"],
        "response_types": {
            "single_file": "Returns PDF file directly",
            "multiple_files": "Returns ZIP archive with all converted PDFs"
        }
    }

@app.get("/healthcheck")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "doc2pdf-converter"
    }


if __name__ == "__main__":
    # Start FastAPI application
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
