# Media Management System

A high-performance, scalable image processing and storage API built with FastAPI and AWS S3. This system is designed to handle media uploads, optimize images on-the-fly, and provide secure, temporary access links.

## System Architecture

The service is structured into three primary layers:
- **API Layer (`src/api`)**: Handles request routing, payload validation, and HTTP responses.
- **Service Layer (`src/services`)**: Manages business logic, including image optimization (resizing) and storage interactions.
- **Core Layer (`src/core`)**: Centralized configuration management and system-wide utilities.

## Core Features

- **Asynchronous Processing**: Leverages FastAPI's async capabilities for high concurrency.
- **Image Optimization**: Automatically resizes large images to maintain a consistent aspect ratio and reduce storage costs.
- **Secure Storage**: Integrates with AWS S3 using best practices for security, returning presigned URLs for temporary object access.
- **Load Balanced**: Designed to run across multiple nodes behind a reverse proxy like NGINX.
- **Validated**: Strict payload validation for file types (JPG/PNG) and size (2MB limit).

## Getting Started

### Installation

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file:
   ```env
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_REGION=your_region
   S3_BUCKET_NAME=your_bucket
   ```

### Running the Service

Start the application using Uvicorn:
```bash
# Instance 1
export BACKEND_PORT=3001 && uvicorn src.api.server:app --port 3001

# Instance 2
export BACKEND_PORT=3002 && uvicorn src.api.server:app --port 3002
```

## Testing

The project includes an integration test suite. Run it using:
```bash
pytest
```

## API Documentation

Once the service is running, interactive documentation is available at:
- Swagger UI: `http://localhost:3001/docs`
- ReDoc: `http://localhost:3001/redoc`
