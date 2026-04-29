"""Handles interactions with cloud storage providers."""

import io
import uuid
import logging
from typing import Tuple

import boto3
from PIL import Image

from src.core.config import AppConfig

logger = logging.getLogger(__name__)


class ImageStorageHandler:
    """Service class for managing image persistence in S3 with local fallback."""

    def __init__(self, cfg: AppConfig):
        self.bucket = cfg.bucket
        self.use_local = not all([cfg.aws_key, cfg.aws_secret, cfg.bucket])
        
        if not self.use_local:
            self.s3_client = boto3.client(
                "s3",
                region_name=cfg.region_name,
                aws_access_key_id=cfg.aws_key,
                aws_secret_access_key=cfg.aws_secret,
            )
        else:
            logger.warning("AWS credentials missing. Falling back to local storage.")

    def process_and_store(self, raw_data: bytes, ext: str, mime_type: str) -> str:
        """Resizes the image and uploads it to S3 or saves locally."""
        processed_data = self._optimize_image(raw_data)
        unique_id = uuid.uuid4()
        path = f"uploads/{unique_id}.{ext.strip('.')}"
        
        if self.use_local:
            local_dir = "src/api/static/uploads"
            import os
            os.makedirs(local_dir, exist_ok=True)
            with open(f"{local_dir}/{unique_id}.{ext.strip('.')}", "wb") as f:
                f.write(processed_data)
            return path
        else:
            # Perform S3 upload
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=f"cdn/{path}",
                Body=processed_data,
                ContentType=mime_type,
            )
            return f"cdn/{path}"

    def get_signed_link(self, path: str, ttl: int = 3600) -> str:
        """Returns a temporary access link for a stored object or local path."""
        if self.use_local:
            # Return a relative link for local serving
            return f"/{path}"
        
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": path},
            ExpiresIn=ttl,
        )

    def _optimize_image(self, blob: bytes, base_width: int = 1024) -> bytes:
        """Internal helper to resize images while maintaining ratio."""
        with Image.open(io.BytesIO(blob)) as img:
            if img.width > base_width:
                w_percent = base_width / float(img.width)
                h_size = int(float(img.height) * float(w_percent))
                img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format=img.format)
            return buffer.getvalue()
