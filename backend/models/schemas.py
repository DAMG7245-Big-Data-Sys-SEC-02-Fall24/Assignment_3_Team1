# backend/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class S3Object(BaseModel):
    key: str
    size: Optional[int]
    last_modified: Optional[datetime]
    is_folder: bool

class S3ListResponse(BaseModel):
    objects: List[S3Object]
    prefix: str
