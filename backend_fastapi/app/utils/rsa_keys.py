"""RSA key loading and management utilities."""
from pathlib import Path
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from loguru import logger
import os


def load_private_key(key_path: Optional[str] = None, key_string: Optional[str] = None) -> bytes:
    """
    Load RSA private key from file path or string.
    
    Args:
        key_path: Path to private key file (PEM format)
        key_string: Private key as string (PEM format)
    
    Returns:
        Private key bytes
    """
    if key_string:
        # Load from string
        try:
            return key_string.encode('utf-8')
        except Exception as e:
            logger.error(f"Error loading private key from string: {e}")
            raise ValueError("Invalid private key string")
    
    if key_path:
        # Load from file
        try:
            key_file = Path(key_path)
            if not key_file.exists():
                raise FileNotFoundError(f"Private key file not found: {key_path}")
            return key_file.read_bytes()
        except Exception as e:
            logger.error(f"Error loading private key from file {key_path}: {e}")
            raise ValueError(f"Failed to load private key: {e}")
    
    raise ValueError("Either key_path or key_string must be provided")


def load_public_key(key_path: Optional[str] = None, key_string: Optional[str] = None) -> bytes:
    """
    Load RSA public key from file path or string.
    
    Args:
        key_path: Path to public key file (PEM format)
        key_string: Public key as string (PEM format)
    
    Returns:
        Public key bytes
    """
    if key_string:
        # Load from string
        try:
            return key_string.encode('utf-8')
        except Exception as e:
            logger.error(f"Error loading public key from string: {e}")
            raise ValueError("Invalid public key string")
    
    if key_path:
        # Load from file
        try:
            key_file = Path(key_path)
            if not key_file.exists():
                raise FileNotFoundError(f"Public key file not found: {key_path}")
            return key_file.read_bytes()
        except Exception as e:
            logger.error(f"Error loading public key from file {key_path}: {e}")
            raise ValueError(f"Failed to load public key: {e}")
    
    raise ValueError("Either key_path or key_string must be provided")


def generate_rsa_key_pair(key_size: int = 2048) -> tuple[str, str]:
    """
    Generate RSA key pair for development/testing.
    
    Args:
        key_size: Key size in bits (default: 2048)
    
    Returns:
        Tuple of (private_key_pem, public_key_pem) as strings
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem


def save_key_pair(private_key: str, public_key: str, private_path: str, public_path: str):
    """Save RSA key pair to files."""
    Path(private_path).parent.mkdir(parents=True, exist_ok=True)
    Path(public_path).parent.mkdir(parents=True, exist_ok=True)
    
    Path(private_path).write_text(private_key)
    Path(public_path).write_text(public_key)
    
    # Set restrictive permissions on private key (Unix-like systems)
    if os.name != 'nt':  # Not Windows
        os.chmod(private_path, 0o600)

