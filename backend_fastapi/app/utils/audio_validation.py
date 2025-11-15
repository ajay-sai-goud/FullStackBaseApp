"""Audio file validation utility for upload validation."""
from typing import Tuple
from fastapi import UploadFile


# Supported audio MIME types
ALLOWED_AUDIO_MIME_TYPES = {
    "audio/mpeg",      # MP3
    "audio/wav",        # WAV
    "audio/wave",       # WAV (alternative)
    "audio/x-wav",      # WAV (alternative)
    "audio/aac",        # AAC
    "audio/mp4",        # M4A/AAC
    "audio/x-m4a",      # M4A
    "audio/ogg",        # OGG
    "audio/oga",        # OGG Audio
    "audio/opus",       # OPUS
}

# Supported audio file extensions
ALLOWED_AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac",
    ".ogg", ".oga", ".opus"
}


def extract_file_extension(filename: str) -> str:
    """Extract file extension from filename.
    
    Args:
        filename: Original filename
        
    Returns:
        File extension with leading dot (e.g., '.mp3') or empty string if no extension
    """
    if not filename or '.' not in filename:
        return ""
    
    # Get the last part after the last dot
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
        return f".{parts[1].lower()}"
    return ""


def validate_audio_file(
    file: UploadFile,
    max_size_bytes: int
) -> Tuple[bool, str | None]:
    """Validate audio file for upload.
    
    Validates:
    1. MIME type is in allowed list
    2. File extension is in allowed list
    3. File extension matches MIME type (basic check)
    4. File size is within limit
    
    Args:
        file: FastAPI UploadFile object
        max_size_bytes: Maximum allowed file size in bytes
        
    Returns:
        Tuple of (is_valid: bool, error_message: str | None)
        If is_valid is True, error_message is None
        If is_valid is False, error_message contains the validation error
    """
    # Check if file has a filename
    if not file.filename:
        return False, "File must have a filename"
    
    # Extract file extension
    file_extension = extract_file_extension(file.filename)
    
    # Validate file extension
    if not file_extension:
        return False, "File must have a valid extension"
    
    if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
        return False, f"Invalid file extension. Supported formats: MP3, WAV, AAC/M4A, OGG, OPUS"
    
    # Validate MIME type
    if not file.content_type:
        return False, "File must have a content type"
    
    if file.content_type not in ALLOWED_AUDIO_MIME_TYPES:
        return False, f"Invalid audio format. Supported formats: MP3, WAV, AAC/M4A, OGG, OPUS"
    
    # Basic check: extension should match MIME type
    extension_to_mime = {
        ".mp3": ["audio/mpeg"],
        ".wav": ["audio/wav", "audio/wave", "audio/x-wav"],
        ".m4a": ["audio/mp4", "audio/x-m4a", "audio/aac"],
        ".aac": ["audio/aac", "audio/mp4"],
        ".ogg": ["audio/ogg", "audio/oga"],
        ".oga": ["audio/ogg", "audio/oga"],
        ".opus": ["audio/opus"],
    }
    
    expected_mimes = extension_to_mime.get(file_extension, [])
    if expected_mimes and file.content_type not in expected_mimes:
        return False, f"File extension does not match MIME type. Expected one of: {', '.join(expected_mimes)}"
    
    # Validate file size
    # Note: file.size may not always be available, so we'll check it if available
    # The actual size will be validated when reading the file content
    if hasattr(file, 'size') and file.size is not None:
        if file.size > max_size_bytes:
            max_size_mb = max_size_bytes / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_size_mb:.0f}MB"
    
    return True, None

