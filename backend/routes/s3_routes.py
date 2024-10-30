from fastapi import APIRouter, Depends, Query
from typing import Optional, Dict
from backend.controllers.s3_controller import S3Controller
from backend.services.s3_service import S3Service
from backend.models.schemas import S3ListResponse

router = APIRouter(prefix="/api/s3", tags=["S3"])

# Dependency Injection
def get_s3_controller() -> S3Controller:
    s3_service = S3Service()
    return S3Controller(s3_service)

@router.get("/list", response_model=S3ListResponse)
async def list_objects(
    prefix: Optional[str] = Query("", description="Prefix of the S3 objects"),
    file_extension: Optional[str] = Query(None, description="Filter by file extension (e.g., .pdf)"),
    controller: S3Controller = Depends(get_s3_controller)
):
    """
    List objects in the S3 bucket with an optional prefix and file extension filter.
    """
    return await controller.list_objects(prefix, file_extension)

@router.get("/url", response_model=Dict[str, str])
async def get_object_url(
    key: str = Query(..., description="The S3 object key"),
    download: bool = Query(False, description="Set to true to generate a download URL"),
    controller: S3Controller = Depends(get_s3_controller)
):
    """
    Get a presigned URL for the specified S3 object key.
    """
    return await controller.get_object_url(key, download)
