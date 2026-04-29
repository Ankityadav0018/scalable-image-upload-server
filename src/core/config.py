"""Configuration management for the image service."""

from dataclasses import dataclass
import os
from functools import lru_cache


@dataclass(frozen=True)
class AppConfig:
    """System settings retrieved from environment variables."""
    
    aws_key: str
    aws_secret: str
    region_name: str
    bucket: str


@lru_cache()
def initialize_config() -> AppConfig:
    """Load and cache the application configuration."""
    return AppConfig(
        aws_key=os.getenv("AWS_ACCESS_KEY_ID", ""),
        aws_secret=os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        region_name=os.getenv("AWS_REGION", ""),
        bucket=os.getenv("S3_BUCKET_NAME", ""),
    )
