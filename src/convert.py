#!/usr/bin/env python3
"""
FastAPI router for DOCX to PDF conversion endpoint
"""

import tempfile
import zipfile
import logging
from pathlib import Path
from typing import List, Union
import aiofiles
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, Response
from src.lib.libreoffice_converter import convert_single_file_libreoffice

# Get logger instance
logger = logging.getLogger(__name__)

# Create router for conversion endpoints
router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.docx', '.doc', '.odt', '.rtf'}

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


async def save_uploaded_file(file: UploadFile, temp_dir: str) -> Path:
    """Save uploaded file to temporary directory"""
    input_path = Path(temp_dir) / file.filename
    async with aiofiles.open(input_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
    return input_path


async def convert_single_uploaded_file(file: UploadFile, temp_dir: str) -> Response:
    """Convert a single uploaded file to PDF"""
    logger.info(f"Starting conversion for file: {file.filename}")
    logger.info(f"File size: {file.size if hasattr(file, 'size') else 'unknown'} bytes")
    
    # Save uploaded file
    input_path = await save_uploaded_file(file, temp_dir)
    logger.info(f"File saved locally at: {input_path}")
    
    # Verify file was saved correctly
    if not input_path.exists():
        logger.error(f"File was not saved correctly: {input_path}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    
    logger.info(f"Local file size: {input_path.stat().st_size} bytes")
    
    # Generate output path
    output_filename = f"{input_path.stem}.pdf"
    output_path = Path(temp_dir) / output_filename
    
    try:
        # Convert using LibreOffice
        logger.info(f"Starting LibreOffice conversion: {input_path} -> {output_path}")
        result = convert_single_file_libreoffice(
            str(input_path), 
            str(output_path)
        )
        
        if result and Path(result).exists():
            logger.info(f"Conversion successful. PDF created at: {result}")
            pdf_file_path = Path(result)
            logger.info(f"PDF file size: {pdf_file_path.stat().st_size} bytes")
            
            # Read the PDF file content asynchronously
            async with aiofiles.open(pdf_file_path, "rb") as pdf_file:
                pdf_content = await pdf_file.read()
            
            logger.info(f"Read PDF content: {len(pdf_content)} bytes")
            
            # Return the PDF content as a response
            return Response(
                content=pdf_content,
                media_type='application/pdf',
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}",
                    "Cache-Control": "no-cache",
                    "Content-Length": str(len(pdf_content))
                }
            )
        else:
            logger.error(f"Conversion failed - PDF file was not created at expected path: {result}")
            raise HTTPException(
                status_code=500,
                detail=f"Conversion failed - PDF file was not created at expected path: {result}"
            )
    except FileNotFoundError as e:
        logger.error(f"Input file error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Input file error: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"File format error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"File format error: {str(e)}"
        )
    except RuntimeError as e:
        logger.error(f"LibreOffice conversion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"LibreOffice conversion error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during conversion: {str(e)}"
        )


async def process_multiple_files(files: List[UploadFile], temp_dir: str) -> tuple:
    """Process multiple files and return converted files and failed files"""
    converted_files = []
    failed_files = []
    
    for file in files:
        try:
            logger.info(f"Processing file: {file.filename}")
            
            # Save uploaded file
            input_path = await save_uploaded_file(file, temp_dir)
            
            # Generate output path
            output_filename = f"{input_path.stem}.pdf"
            output_path = Path(temp_dir) / output_filename
            
            # Convert using LibreOffice
            result = convert_single_file_libreoffice(
                str(input_path), 
                str(output_path)
            )
            
            if result and Path(result).exists():
                converted_files.append((result, output_filename))
                logger.info(f"Successfully converted: {file.filename}")
            else:
                failed_files.append(file.filename)
                logger.warning(f"Failed to convert: {file.filename}")
                
        except Exception as e:
            failed_files.append(f"{file.filename} (Error: {str(e)})")
            logger.error(f"Error converting {file.filename}: {str(e)}")
    
    return converted_files, failed_files


def create_zip_response(converted_files: List[tuple], temp_dir: str) -> FileResponse:
    """Create ZIP file with converted PDFs and return FileResponse"""
    zip_path = Path(temp_dir) / "converted_documents.zip"
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for pdf_path, pdf_filename in converted_files:
            zip_file.write(pdf_path, pdf_filename)
    
    response_filename = f"converted_documents_{len(converted_files)}_files.zip"
    return FileResponse(
        path=str(zip_path),
        filename=response_filename,
        media_type='application/zip'
    )


async def handle_single_file_conversion(file: UploadFile) -> Response:
    """Handle single file conversion with proper error handling"""
    logger.info("Processing single file conversion (Java client compatible)")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = await convert_single_uploaded_file(file, temp_dir)
            logger.info("=== PDF Conversion Request Completed Successfully ===")
            return result
            
        except HTTPException:
            logger.error("=== PDF Conversion Request Failed (HTTPException) ===")
            raise
        except Exception as e:
            logger.error(f"=== PDF Conversion Request Failed (Unexpected Error): {str(e)} ===")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )


async def handle_multiple_files_conversion(files: List[UploadFile]) -> FileResponse:
    """Handle multiple files conversion with proper error handling"""
    logger.info("Processing multiple files conversion")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            converted_files, failed_files = await process_multiple_files(files, temp_dir)
            
            # Check if any files were converted
            if not converted_files:
                logger.error(f"No files could be converted. Failed files: {', '.join(failed_files)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"No files could be converted. Failed files: {', '.join(failed_files)}"
                )
            
            logger.info(f"Successfully converted {len(converted_files)} files")
            if failed_files:
                logger.warning(f"Failed to convert {len(failed_files)} files: {', '.join(failed_files)}")
            
            result = create_zip_response(converted_files, temp_dir)
            logger.info("=== Multiple Files Conversion Request Completed Successfully ===")
            return result
            
        except HTTPException:
            logger.error("=== Multiple Files Conversion Request Failed (HTTPException) ===")
            raise
        except Exception as e:
            logger.error(f"=== Multiple Files Conversion Request Failed (Unexpected Error): {str(e)} ===")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )


def validate_files(files: List[UploadFile]) -> None:
    """Validate all uploaded files"""
    for file in files:
        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{file.filename}'. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
            )

@router.post("/convert")
async def convert_document(files: Union[UploadFile, List[UploadFile]] = File(alias="files")):
    """
    Convert DOCX file(s) to PDF - Compatible with Java OkHttp client
    
    - **files**: Single or multiple files to convert (.docx, .doc, .odt, .rtf)
    
    Returns:
    - Single file: PDF file directly (as expected by Java client)
    - Multiple files: ZIP archive containing all converted PDFs
    
    Java client compatibility:
    - Accepts single file sent as multipart form data with field name "files"
    - Returns PDF directly with proper content-type headers
    - Includes detailed logging for debugging
    """
    logger.info("=== PDF Conversion Request Started ===")
    
    # Handle case where files might be a single file or list
    if not isinstance(files, list):
        files = [files]
    
    logger.info(f"Number of files received: {len(files)}")
    for i, file in enumerate(files):
        logger.info(f"File {i+1}: {file.filename}, Content-Type: {file.content_type}")
    
    # Validate all files first
    validate_files(files)
    
    # Route to appropriate handler based on number of files
    if len(files) == 1:
        return await handle_single_file_conversion(files[0])
    else:
        return await handle_multiple_files_conversion(files)


@router.post("/convert/single")
async def convert_single_document_java_compatible(files: UploadFile = File(alias="files")):
    """
    Convert a single DOCX file to PDF - Optimized for Java OkHttp client
    
    This endpoint is specifically designed for Java clients using OkHttp.
    It accepts exactly one file and returns the PDF directly.
    
    - **files**: Single file to convert (.docx, .doc, .odt, .rtf)
    
    Returns: PDF file directly with proper headers for Java client compatibility
    """
    logger.info("=== Single File PDF Conversion (Java Compatible) ===")
    logger.info(f"File: {files.filename}, Content-Type: {files.content_type}")
    
    # Validate single file
    if not is_allowed_file(files.filename):
        logger.error(f"Invalid file type: {files.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{files.filename}'. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = await convert_single_uploaded_file(files, temp_dir)
            logger.info("=== Single File Conversion Completed Successfully ===")
            return result
            
        except HTTPException:
            logger.error("=== Single File Conversion Failed (HTTPException) ===")
            raise
        except Exception as e:
            logger.error(f"=== Single File Conversion Failed: {str(e)} ===")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
