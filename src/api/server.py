"""Main API entrypoint for the Image Processing Service."""

import os
import logging
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.core.config import initialize_config
from src.services.storage import ImageStorageHandler

# Setup application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ImageService")

app = FastAPI(title="Media Upload API", version="2.0.0")

# Constants
VALID_TYPES = {"image/jpeg", "image/png"}
MAX_SIZE = 2 * 1024 * 1024
INSTANCE_ID = os.getenv("BACKEND_PORT", "Node-X")


@app.get("/")
async def read_index():
    """Serve the frontend homepage."""
    return FileResponse("src/api/static/index.html")


@app.get("/status")
async def check_status():
    """Service health check."""
    return {
        "active": True,
        "node": INSTANCE_ID,
        "service": "MediaManager"
    }


def _validate_payload(upload: UploadFile):
    """Internal validation for incoming files."""
    if not upload:
        raise HTTPException(status_code=400, detail="Payload is empty")
    
    if upload.content_type not in VALID_TYPES:
        raise HTTPException(
            status_code=415, 
            detail=f"Content type {upload.content_type} is not supported"
        )


@app.post("/upload")
async def handle_media_upload(file: UploadFile = File(...)):
    """Primary endpoint for processing and storing images."""
    logger.info(f"Processing request on instance: {INSTANCE_ID}")
    
    _validate_payload(file)
    
    # Read content
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (Max 2MB)")

    try:
        cfg = initialize_config()
        handler = ImageStorageHandler(cfg)
        
        # Process: resize and upload
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "png"
        storage_path = handler.process_and_store(content, file_ext, file.content_type)
        
        # Get secure link
        download_url = handler.get_signed_link(storage_path)
        
        return {
            "success": True,
            "data": {
                "link": download_url,
                "ref": storage_path,
                "processed_by": INSTANCE_ID
            },
            "meta": {"msg": "Image processed successfully"}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Uncaught exception during upload")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Operation failed", "details": str(e)}
        )

# Mount static uploads for local fallback
app.mount("/uploads", StaticFiles(directory="src/api/static/uploads"), name="uploads")
