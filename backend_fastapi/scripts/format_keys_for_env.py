"""Helper script to format PEM keys for .env file."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def format_key_for_env(key_path: Path) -> str:
    """
    Read PEM key file and format it for .env file.
    
    Args:
        key_path: Path to PEM key file
        
    Returns:
        Formatted key string ready for .env file
    """
    if not key_path.exists():
        raise FileNotFoundError(f"Key file not found: {key_path}")
    
    # Read the key file
    key_content = key_path.read_text().strip()
    
    # Replace newlines with \n and wrap in quotes
    formatted = key_content.replace('\n', '\\n')
    
    return f'"{formatted}"'


def main():
    """Format RSA keys for .env file."""
    keys_dir = Path(__file__).parent.parent / "keys"
    
    private_key_path = keys_dir / "jwt_private_key.pem"
    public_key_path = keys_dir / "jwt_public_key.pem"
    
    # Try alternative names
    if not private_key_path.exists():
        private_key_path = keys_dir / "private_key.pem"
    if not public_key_path.exists():
        public_key_path = keys_dir / "public_key.pem"
    
    if not private_key_path.exists() or not public_key_path.exists():
        print("❌ Error: Key files not found!")
        print(f"Expected files in: {keys_dir}")
        print("  - jwt_private_key.pem or private_key.pem")
        print("  - jwt_public_key.pem or public_key.pem")
        print("\nGenerate keys first using:")
        print("  python scripts/generate_rsa_keys.py")
        sys.exit(1)
    
    print("Formatting PEM keys for .env file...\n")
    
    private_key_formatted = format_key_for_env(private_key_path)
    public_key_formatted = format_key_for_env(public_key_path)
    
    print("Add these to your .env file:\n")
    print("=" * 70)
    print("JWT_PRIVATE_KEY=" + private_key_formatted)
    print()
    print("JWT_PUBLIC_KEY=" + public_key_formatted)
    print("=" * 70)
    print("\n✅ Keys formatted successfully!")
    print("\n💡 Tip: Copy the output above and paste into your .env file")


if __name__ == "__main__":
    main()

