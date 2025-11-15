"""Script to generate RSA key pair for JWT signing."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.rsa_keys import generate_rsa_key_pair, save_key_pair


def main():
    """Generate RSA key pair and save to files."""
    print("Generating RSA key pair (2048 bits)...")
    
    private_key, public_key = generate_rsa_key_pair(key_size=2048)
    
    # Save to keys directory
    keys_dir = Path(__file__).parent.parent / "keys"
    keys_dir.mkdir(exist_ok=True)
    
    private_path = keys_dir / "private_key.pem"
    public_path = keys_dir / "public_key.pem"
    
    save_key_pair(private_key, public_key, str(private_path), str(public_path))
    
    print(f"\n✅ RSA key pair generated successfully!")
    print(f"Private key saved to: {private_path}")
    print(f"Public key saved to: {public_path}")
    print("\n⚠️  IMPORTANT: Keep the private key secure and never commit it to version control!")
    print("\n📝 To use keys in .env file (recommended for Docker):")
    print("   Run: python scripts/format_keys_for_env.py")
    print("\n📁 To use keys as file paths:")
    print(f"   JWT_PRIVATE_KEY_PATH={private_path}")
    print(f"   JWT_PUBLIC_KEY_PATH={public_path}")


if __name__ == "__main__":
    main()

