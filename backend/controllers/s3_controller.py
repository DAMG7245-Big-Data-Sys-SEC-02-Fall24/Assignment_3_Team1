# backend/controllers/s3_controller.py
from fastapi import HTTPException
from typing import Optional, Dict
from backend.models.schemas import S3ListResponse
from backend.services.s3_service import S3Service
import asyncio
import functools
import logging

logger = logging.getLogger(__name__)

class S3Controller:
    def __init__(self, s3_service: S3Service):
        self.s3_service = s3_service

    async def list_objects(self, prefix: Optional[str] = "", file_extension: Optional[str] = None) -> S3ListResponse:
        try:
            loop = asyncio.get_event_loop()
            # Run the blocking list_objects method in a thread pool
            objects = await loop.run_in_executor(
                None, functools.partial(self.s3_service.list_objects, prefix, file_extension)
            )
            logger.info(f"Listed {len(objects)} objects with prefix '{prefix}' and extension '{file_extension}'")
            return S3ListResponse(objects=objects, prefix=prefix)
        except Exception as e:
            logger.error(f"Error listing objects: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_object_url(self, key: str, download: bool = False) -> Dict[str, str]:
        try:
            logger.info(f"Generating {'download' if download else 'view'} presigned URL for key: '{key}'")
            url = self.s3_service.get_object_url(key, download)
            return {"url": url}
        except Exception as e:
            logger.error(f"Error generating presigned URL for key '{key}': {e}")
            raise HTTPException(status_code=500, detail=str(e))
