"""S3 upload helper for processed CSV files.

This module provides a small helper to upload a local file to S3 using boto3.
The function expects AWS credentials to be available via environment variables,
shared credentials file, or an attached IAM role.

Functions:
- `upload_file(file_path, bucket, key, region)` -> bool: uploads the file and
  returns True on success, False on failure.
"""

import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError


def upload_file(file_path: str, bucket: str, key: str, region: str = 'us-east-1') -> bool:
    """Upload a local file to S3.

    Args:
        file_path: Path to the local file to upload.
        bucket: S3 bucket name.
        key: S3 object key (path within the bucket).
        region: AWS region for the S3 client (default: 'us-east-1').

    Returns:
        True if upload succeeded, False otherwise.
    """
    s3 = boto3.client("s3", region_name=region)
    try:
        s3.upload_file(file_path, bucket, key)
        print(f"Uploaded {file_path} to s3://{bucket}/{key}")
        return True
    except ClientError as e:
        print("S3 upload failed:", e)
        return False


def get_s3_path(bucket: str, key: str) -> str:
    """Return an S3 URI for the given bucket and key."""
    return f"s3://{bucket}/{key}"
