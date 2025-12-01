from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.models.schemas import StandardResponse
from app.services.media_service import MediaService
from app.middleware.auth import get_current_user, require_author_or_reader

router = APIRouter(prefix="/api/v1/media", tags=["media"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(require_author_or_reader)
):
    try:
        # Read file content
        file_content = await file.read()

        # Validate file size (e.g., max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")

        # Validate file type (optional, allow common types)
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'text/plain', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not allowed")

        # Upload file
        public_url = MediaService.upload_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )

        return StandardResponse(
            success=True,
            data={"url": public_url},
            message="File uploaded successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))