"""JWT token creation, validation, and decoding using RS256."""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from loguru import logger

from app.core.config import settings
from app.utils.rsa_keys import load_private_key, load_public_key


# Cache for loaded keys
_private_key: Optional[bytes] = None
_public_key: Optional[bytes] = None


def _parse_audience(audience_str: str) -> list[str]:
    """
    Parse audience string into a list.
    
    JWT audience (aud) can be:
    - A single string: "https://app.example.com/"
    - A comma-separated string: "https://app1.com/,https://app2.com/"
    
    Returns a list of audience values (trimmed of whitespace).
    
    Args:
        audience_str: Comma-separated audience string or single value
        
    Returns:
        List of audience strings
    """
    if "," in audience_str:
        return [aud.strip() for aud in audience_str.split(",") if aud.strip()]
    return [audience_str.strip()] if audience_str.strip() else []


def get_private_key() -> bytes:
    """Get RSA private key for signing tokens."""
    global _private_key
    if _private_key is None:
        _private_key = load_private_key(
            key_path=settings.JWT_PRIVATE_KEY_PATH,
            key_string=settings.JWT_PRIVATE_KEY
        )
        logger.info("Loaded RSA private key for JWT signing")
    return _private_key


def get_public_key() -> bytes:
    """Get RSA public key for verifying tokens."""
    global _public_key
    if _public_key is None:
        _public_key = load_public_key(
            key_path=settings.JWT_PUBLIC_KEY_PATH,
            key_string=settings.JWT_PUBLIC_KEY
        )
        logger.info("Loaded RSA public key for JWT verification")
    return _public_key


def create_access_token(data: Dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token using RS256 with standard claims.
    
    Includes standard JWT claims:
    - iss (issuer): Who issued the token
    - aud (audience): Intended recipient(s)
    - iat (issued at): When the token was issued
    - exp (expiration): When the token expires
    - sub (subject): User ID (from data)
    
    Args:
        data: Dictionary containing custom claims (sub, email, permissions, etc.)
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Calculate expiration time
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    # Add standard JWT claims
    # iss (issuer): Single string identifying who issued the token
    # aud (audience): Array of strings identifying intended recipients
    to_encode.update({
        "iss": settings.JWT_ISSUER,  # Issuer (single string)
        "aud": _parse_audience(settings.JWT_AUDIENCE),  # Audience (array/list)
        "iat": int(now.timestamp()),  # Issued at (Unix timestamp)
        "exp": int(expire.timestamp()),  # Expiration (Unix timestamp)
    })
    
    # Get private key for signing
    private_key = get_private_key()
    
    encoded_jwt = jwt.encode(
        to_encode,
        private_key,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, str]]:
    """
    Decode and validate a JWT token using RS256.
    
    Validates standard JWT claims:
    - Signature verification using public key
    - Expiration (exp) - token must not be expired
    - Issuer (iss) - must match configured issuer
    - Audience (aud) - must match configured audience
    
    Args:
        token: JWT token string to decode and validate
        
    Returns:
        Decoded payload dictionary if valid, None otherwise
    """
    try:
        # Get public key for verification
        public_key = get_public_key()
        
        # Parse audience - JWT_AUDIENCE is comma-separated string
        expected_audiences = _parse_audience(settings.JWT_AUDIENCE)
        logger.debug(f"Expected audiences: {expected_audiences}")
        
        # Decode token without audience validation (python-jose doesn't handle array audiences well)
        # We'll validate issuer and audience manually
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": False,  # We'll validate manually
                "verify_aud": False,  # We'll validate manually
            }
        )
        
        # Validate issuer manually
        token_iss = payload.get("iss")
        if token_iss != settings.JWT_ISSUER:
            raise JWTError(
                f"Token issuer '{token_iss}' does not match expected issuer '{settings.JWT_ISSUER}'"
            )
        
        # Manually validate audience
        # Token's aud can be a string or an array
        token_aud = payload.get("aud")
        logger.debug(f"Token audience (raw): {token_aud}, type: {type(token_aud)}")
        
        if token_aud is None:
            raise JWTError("Token missing audience claim")
        
        # Convert token_aud to list if it's a string
        if isinstance(token_aud, str):
            token_aud_list = [token_aud.strip()]
        elif isinstance(token_aud, list):
            token_aud_list = [str(aud).strip() for aud in token_aud]
        else:
            token_aud_list = [str(token_aud).strip()]
        
        # Normalize expected audiences (strip whitespace)
        expected_audiences_normalized = [aud.strip() for aud in expected_audiences]
        
        logger.debug(f"Token audience (normalized): {token_aud_list}")
        logger.debug(f"Expected audiences (normalized): {expected_audiences_normalized}")
        
        # Check if at least one expected audience matches (case-sensitive exact match)
        # Convert both to sets for easier comparison
        token_aud_set = set(token_aud_list)
        expected_aud_set = set(expected_audiences_normalized)
        
        if not token_aud_set.intersection(expected_aud_set):
            logger.warning(
                f"Audience mismatch - Token: {token_aud_list}, Expected: {expected_audiences_normalized}"
            )
            raise JWTError(
                f"Token audience {token_aud_list} does not match expected audiences {expected_audiences_normalized}"
            )
        
        logger.debug("Audience validation passed")
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token."""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")  # 'sub' is standard JWT claim for subject (user ID)
    return None


def get_email_from_token(token: str) -> Optional[str]:
    """Extract email from JWT token."""
    payload = decode_token(token)
    if payload:
        return payload.get("email")
    return None


def get_permissions_from_token(token: str) -> list[str]:
    """Extract permissions list from JWT token."""
    payload = decode_token(token)
    if payload:
        permissions = payload.get("permissions", [])
        if isinstance(permissions, list):
            return permissions
        return []
    return []

