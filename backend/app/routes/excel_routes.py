"""
Excel Upload API Routes
Handles Excel file uploads and parsing for bid simulation.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import os
import shutil
from pathlib import Path
from datetime import datetime

from app.services.excel_parser import parse_excel_file


router = APIRouter(prefix="/api/v1/excel", tags=["Excel Upload"])

# Upload directory
UPLOAD_DIR = Path("/home/user/webapp/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_excel_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and parse an Excel file containing bid simulation data.
    
    **Request:**
    - File upload (multipart/form-data)
    - Accepted formats: .xlsx, .xls
    
    **Response:**
    - Parsed metadata (발주처, 공사명, 추정가격, 예가범위)
    - Company information list
    - Simulation matrix (예가율별 투찰 금액)
    """
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .xlsx and .xls files are accepted."
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = file.filename
    safe_filename = f"{timestamp}_{original_filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse the Excel file
        parsed_data = parse_excel_file(str(file_path))
        
        if not parsed_data.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse Excel file: {parsed_data.get('error', 'Unknown error')}"
            )
        
        # Add file information to response
        parsed_data["file_info"] = {
            "original_filename": original_filename,
            "saved_filename": safe_filename,
            "file_path": str(file_path),
            "upload_time": timestamp
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File uploaded and parsed successfully",
                "data": parsed_data
            }
        )
        
    except HTTPException:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        file.file.close()


@router.get("/uploads")
async def list_uploaded_files() -> Dict[str, Any]:
    """
    List all uploaded Excel files.
    
    **Response:**
    - List of uploaded files with metadata
    """
    try:
        files = []
        for file_path in UPLOAD_DIR.glob("*.xlsx"):
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "upload_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(file_path)
            })
        
        # Sort by upload time (newest first)
        files.sort(key=lambda x: x["upload_time"], reverse=True)
        
        return {
            "total": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )


@router.delete("/uploads/{filename}")
async def delete_uploaded_file(filename: str) -> Dict[str, str]:
    """
    Delete an uploaded Excel file.
    
    **Parameters:**
    - filename: Name of the file to delete
    
    **Response:**
    - Success message
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {filename}"
        )
    
    try:
        file_path.unlink()
        return {
            "message": f"File deleted successfully: {filename}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )


@router.post("/parse/{filename}")
async def reparse_uploaded_file(filename: str) -> Dict[str, Any]:
    """
    Re-parse a previously uploaded Excel file.
    
    **Parameters:**
    - filename: Name of the file to parse
    
    **Response:**
    - Parsed data
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {filename}"
        )
    
    try:
        parsed_data = parse_excel_file(str(file_path))
        
        if not parsed_data.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse Excel file: {parsed_data.get('error', 'Unknown error')}"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "File parsed successfully",
                "data": parsed_data
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing file: {str(e)}"
        )
