"""
Google Cloud Storage utility module
"""

import os
from typing import Optional
from datetime import timedelta
from google.cloud import storage
from fastapi import UploadFile
from src.configs.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StorageService:
    """
    Service for handling file uploads to Google Cloud Storage
    """
    
    def __init__(self):
        """Initialize Google Cloud Storage client"""
        try:
            if settings.gcs_credentials_path:
                self.client = storage.Client.from_service_account_json(
                    settings.gcs_credentials_path,
                    project=settings.gcs_project_id
                )
            else:
                # Use default credentials (from environment or instance metadata)
                self.client = storage.Client(project=settings.gcs_project_id)
            
            self.bucket = self.client.bucket(settings.gcs_bucket_name)
            logger.info(f"StorageService initialized with bucket: {settings.gcs_bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize StorageService: {e}")
            raise
    
    async def upload_file(self, file: UploadFile, destination_path: str) -> str:
        """
        Upload a file to Google Cloud Storage
        
        Args:
            file: The uploaded file
            destination_path: The destination path in GCS (e.g., "inputs/task_id/filename.pdf")
            
        Returns:
            The public URL of the uploaded file
        """
        try:
            # Read file content
            content = await file.read()
            
            # Create blob and upload
            blob = self.bucket.blob(destination_path)
            blob.upload_from_string(
                content,
                content_type=file.content_type
            )
            
            
            logger.info(f"File uploaded successfully to {self.bucket.name}/{destination_path}")
            return destination_path
            
        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {e}")
            raise
        finally:
            # Reset file pointer for potential reuse
            await file.seek(0)
    
    def get_signed_url(self, blob_name: str, expiration: int = 3600) -> str:
        """
        Generate a signed URL for a blob
        
        Args:
            blob_name: The name of the blob in GCS
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Signed URL
        """
        try:
            blob = self.bucket.blob(blob_name)
            # Convert seconds to timedelta for generate_signed_url
            url = blob.generate_signed_url(expiration=timedelta(seconds=expiration))
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from Google Cloud Storage
        
        Args:
            blob_name: The name of the blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"File deleted successfully: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from GCS: {e}")
            return False


# Global storage service instance
storage_service = StorageService()

