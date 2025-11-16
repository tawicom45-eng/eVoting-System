import os
from typing import List, Optional

def build_redshift_copy_command(s3_path: str, table: str, iam_role: Optional[str] = None, access_key: Optional[str] = None, secret_key: Optional[str] = None, region: str = 'us-east-1', extra: str = '') -> str:
    """Return a Redshift COPY command string to load CSVs from S3.

    Either `iam_role` or `access_key`+`secret_key` must be provided.
    """
    copy = [f"COPY {table}", f"FROM '{s3_path}'", "CSV", "IGNOREHEADER 1", "DELIMITER ','"]
    if iam_role:
        copy.append(f"IAM_ROLE '{iam_role}'")
    else:
        copy.append(f"ACCESS_KEY_ID '{access_key}'")
        copy.append(f"SECRET_ACCESS_KEY '{secret_key}'")

    copy.append(f"REGION '{region}'")
    import os
    from typing import Optional

    from etl.load import load_to_s3


    def build_redshift_copy_command(
        s3_path: str,
        table: str,
        iam_role: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: str = "us-east-1",
        extra: str = "",
    ) -> str:
        """Return a Redshift COPY command string to load CSVs from S3.

        Either `iam_role` or (`access_key` and `secret_key`) must be provided. The
        returned string is a COPY statement suitable for execution in Redshift.
        """
        copy = [f"COPY {table}", f"FROM '{s3_path}'", "CSV", "IGNOREHEADER 1", "DELIMITER ','"]
        if iam_role:
            copy.append(f"IAM_ROLE '{iam_role}'")
        else:
            copy.append(f"ACCESS_KEY_ID '{access_key}'")
            copy.append(f"SECRET_ACCESS_KEY '{secret_key}'")

        copy.append(f"REGION '{region}'")
        if extra:
            copy.append(extra)

        return " \\\n+".join(copy) + ";"


    def upload_and_build_copy(
        local_path: str,
        s3_bucket: str,
        s3_key_prefix: str,
        table: str,
        iam_role: Optional[str] = None,
        region: str = "us-east-1",
    ) -> str:
        """Upload `local_path` to S3 under `s3_bucket/s3_key_prefix/` and return a COPY command.

        This function uses `etl.load.load_to_s3.upload_file` to perform the upload,
        then constructs a COPY command referencing the uploaded object.
        """
        base = os.path.basename(local_path)
        key = f"{s3_key_prefix.rstrip('/')}/{base}"
        ok = load_to_s3.upload_file(local_path, s3_bucket, key, region=region)
        if not ok:
            raise RuntimeError(f"Failed to upload {local_path} to s3://{s3_bucket}/{key}")
        s3_path = f"s3://{s3_bucket}/{key}"
        return build_redshift_copy_command(s3_path, table, iam_role=iam_role, region=region)
