from ..storage.connection import get_supabase_client
from fastapi import UploadFile, File, HTTPException, status
import time
import logging

logger = logging.getLogger(__name__)

async def uploadFile(file: UploadFile = File(...)):
    
    # Enforce PDF-only uploads
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    try:
        contents = await file.read()
       
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{file.filename}"

        logger.info(f"Starting upload for {file.filename}")
        
        supabase, bucket_name = get_supabase_client()

        supabase.storage.from_(bucket_name).upload(
            path=unique_filename,
            file=contents,
            file_options={
                "content-type": "application/pdf",
                "upsert": False,
            },
        )

        logger.info(f"Successfully uploaded to Supabase: {unique_filename}")

        file_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)
        
        return {
            "filename": unique_filename,
            "url": file_url,
        }

    except Exception as e:
        logger.error(f"Supabase upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file",
        )
