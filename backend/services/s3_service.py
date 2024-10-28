# backend/services/s3_service.py
import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
from backend.models.schemas import S3Object
from backend.config.settings import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_BUCKET_NAME

    def list_objects(self, prefix: str = "", file_extension: Optional[str] = None) -> List[S3Object]:
        try:
            # Ensure prefix ends with '/'
            if prefix and not prefix.endswith('/'):
                prefix += '/'

            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter='/')

            objects = []
            
            for page in pages:
                # Handle folders (CommonPrefixes)
                for folder in page.get('CommonPrefixes', []):
                    folder_key = folder.get('Prefix', '')
                    objects.append(
                        S3Object(
                            key=folder_key,
                            size=0,
                            last_modified=None,
                            is_folder=True
                        )
                    )

                # Handle files
                for obj in page.get('Contents', []):
                    if obj['Key'] != prefix:  # Skip the prefix itself
                        if file_extension:
                            if obj['Key'].lower().endswith(file_extension.lower()):
                                objects.append(
                                    S3Object(
                                        key=obj['Key'],
                                        size=obj['Size'],
                                        last_modified=obj['LastModified'],
                                        is_folder=False
                                    )
                                )
                        else:
                            objects.append(
                                S3Object(
                                    key=obj['Key'],
                                    size=obj['Size'],
                                    last_modified=obj['LastModified'],
                                    is_folder=False
                                )
                            )

            return objects

        except ClientError as e:
            logger.error(f"Error listing S3 objects: {str(e)}")
            raise Exception(f"Error listing S3 objects: {str(e)}")

    def get_object_url(self, key: str, download: bool = False) -> str:
        try:
            params = {'Bucket': self.bucket_name, 'Key': key}
            if download:
                params['ResponseContentDisposition'] = 'attachment'  # Force download
            else:
                # To view in browser, 'inline' or no disposition
                params['ResponseContentDisposition'] = 'inline'

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise Exception(f"Error generating presigned URL: {str(e)}")
