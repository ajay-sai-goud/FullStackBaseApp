"""Audio file API endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException, Path as PathParam, Body
from loguru import logger

from app.schemas.audio import (
    AudioFileListResponse,
    AudioPlayResponse,
    AudioFileResponse,
    AudioFileListQueryParams,
    AudioFileIdPathParams,
    AudioFileUpdate
)
from app.core.dependencies import (
    get_audio_service,
    require_auth,
    require_permissions
)
from app.core.constants import Permissions
from app.schemas.user.models import User
from app.services.audio.interfaces import IAudioService
from app.core.observability import TracingAPIRoute

router = APIRouter(route_class=TracingAPIRoute, prefix="/audio", tags=["Audio"])


@router.get(
    "",
    response_model=AudioFileListResponse,
    status_code=status.HTTP_200_OK
)
async def list_audio_files(
    query: AudioFileListQueryParams = Depends(),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.READ_AUDIO)),
    audio_service: IAudioService = Depends(get_audio_service)
) -> AudioFileListResponse:
    """
    List all audio files for the authenticated user.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    
    **Required Permission:** `read:audio` or `admin`
    
    Returns list of audio files with metadata.
    """
    logger.info(f"Listing audio files for user: {current_user.id}")
    
    files = await audio_service.list_user_files(
        user_id=current_user.id,
        skip=query.skip,
        limit=query.limit
    )
    
    return AudioFileListResponse(files=files)


@router.get(
    "/{id}/play",
    response_model=AudioPlayResponse,
    status_code=status.HTTP_200_OK
)
async def play_audio_file(
    id: str = PathParam(..., min_length=1, description="File ID"),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.READ_AUDIO)),
    audio_service: IAudioService = Depends(get_audio_service)
) -> AudioPlayResponse:
    """
    Get signed URL for audio file playback.
    
    - **id**: File ID
    
    **Required Permission:** `read:audio` or `admin`
    
    Returns presigned URL that expires in 1 hour (3600 seconds).
    Verifies file ownership before returning URL to ensure users can only access their own files.
    The presigned URL can be used directly in HTML5 `<audio>` tags for playback.
    """
    # Validate using schema
    path_params = AudioFileIdPathParams(id=id)
    logger.info(f"Getting playback URL for file {path_params.id} for user {current_user.id}")
    
    return await audio_service.get_file_for_playback(
        file_id=path_params.id,
        user_id=current_user.id
    )


@router.post(
    "/upload",
    response_model=AudioFileResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_audio_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.WRITE_AUDIO)),
    audio_service: IAudioService = Depends(get_audio_service)
) -> AudioFileResponse:
    """
    Upload an audio file to cloud storage.
    
    - **file**: Audio file (multipart/form-data)
    
    **Supported Formats:**
    - MP3 (`.mp3`, `audio/mpeg`)
    - WAV (`.wav`, `audio/wav`, `audio/wave`)
    - AAC/M4A (`.m4a`, `.aac`, `audio/mp4`, `audio/aac`)
    - OGG (`.ogg`, `.oga`, `audio/ogg`, `audio/oga`)
    - OPUS (`.opus`, `audio/opus`)
    
    **File Size Limit:**
    - Maximum: 100MB (configurable via `MAX_AUDIO_FILE_SIZE_MB` environment variable)
    
    **S3 Storage Structure:**
    - Files are stored in S3 with structure: `users/{user_id}/{file_id}/{filename}`
    - This ensures direct mapping between S3 keys and database file_id
    
    **Required Permission:** `write:audio` or `admin`
    
    Uploads file to S3, stores metadata in database, and returns file details.
    Validates file type, extension, and size before upload.
    """
    logger.info(f"Uploading audio file for user: {current_user.id}")
    
    return await audio_service.upload_file(
        file=file,
        user_id=current_user.id
    )


@router.put(
    "/{id}",
    response_model=AudioFileResponse,
    status_code=status.HTTP_200_OK
)
async def update_audio_file(
    id: str = PathParam(..., min_length=1, description="File ID"),
    update_data: AudioFileUpdate = Body(...),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.WRITE_AUDIO)),
    audio_service: IAudioService = Depends(get_audio_service)
) -> AudioFileResponse:
    """
    Update audio file metadata.
    
    - **id**: File ID
    - **file_name**: New filename for the audio file (optional)
    
    **Required Permission:** `write:audio` or `admin`
    
    Updates file metadata in the database. Verifies file ownership before allowing update.
    Currently supports updating the file name only.
    """
    # Validate using schema
    path_params = AudioFileIdPathParams(id=id)
    logger.info(f"Updating file {path_params.id} for user {current_user.id}")
    
    return await audio_service.update_file(
        file_id=path_params.id,
        user_id=current_user.id,
        file_name=update_data.file_name
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_audio_file(
    id: str = PathParam(..., min_length=1, description="File ID"),
    current_user: User = Depends(require_auth),
    permission: None = Depends(require_permissions(Permissions.DELETE_AUDIO)),
    audio_service: IAudioService = Depends(get_audio_service)
):
    """
    Delete an audio file.
    
    - **id**: File ID
    
    **Required Permission:** `delete:audio` or `admin`
    
    Deletes the file from S3 storage and removes the record from the database.
    Verifies file ownership before allowing delete to ensure users can only delete their own files.
    """
    # Validate using schema
    path_params = AudioFileIdPathParams(id=id)
    logger.info(f"Deleting file {path_params.id} for user {current_user.id}")
    
    await audio_service.delete_file(
        file_id=path_params.id,
        user_id=current_user.id
    )
    
    return None

