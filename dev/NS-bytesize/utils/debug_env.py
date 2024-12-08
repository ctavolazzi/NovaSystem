# Standard library
import os
from typing import Optional, List
from pathlib import Path
import sys

# Third party
from dotenv import load_dotenv, find_dotenv

def find_all_env_files() -> List[Path]:
    """
    Search for all .env files in current and parent directories
    """
    env_files = []
    current_dir = Path.cwd()
    while current_dir.as_posix() != current_dir.root:
        env_file = current_dir / '.env'
        if env_file.exists():
            env_files.append(env_file)
        current_dir = current_dir.parent
    return env_files

def print_api_key_status():
    """
    Debug utility to check OpenAI API key status.
    Prints only the first and last 4 characters if the key exists, for security.
    """
    # Clear any existing env vars
    if 'OPENAI_API_KEY' in os.environ:
        print("⚠️ OPENAI_API_KEY was already in environment")
        del os.environ['OPENAI_API_KEY']

    # Find and load all .env files
    env_files = find_all_env_files()

    print("\n=== Environment Files Found ===")
    if not env_files:
        print("⚠️ No .env files found")
    else:
        for env_file in env_files:
            print(f"\n📁 {env_file}")
            print(f"   File exists: {env_file.exists()}")
            print(f"   File size: {env_file.stat().st_size} bytes")
            # Read and display contents (excluding sensitive data)
            with open(env_file) as f:
                contents = f.readlines()
                print("   Contents:")
                for line in contents:
                    if line.strip() and not line.startswith('#'):
                        key = line.split('=')[0].strip()
                        print(f"   - {key}")
                        if key == 'OPENAI_API_KEY':
                            value = line.split('=')[1].strip()
                            print(f"     Length: {len(value)} chars")
                            print(f"     Starts with: {value[:6]}...")

    # Load the closest .env file
    if env_files:
        print(f"\nLoading environment from: {env_files[0]}")
        load_dotenv(env_files[0], override=True)

    api_key: Optional[str] = os.getenv('OPENAI_API_KEY')

    print("\n=== OpenAI API Key Status ===")
    if not api_key:
        print("❌ No API key found in environment variables")
        return

    if api_key.startswith('sk-proj-'):
        print("✅ Valid project API key format detected")
    elif api_key.startswith('sk-'):
        print("✅ Valid API key format detected")
    else:
        print("⚠️ API key doesn't start with expected prefix")

    # Only show first 4 and last 4 characters
    masked_key = f"{api_key[:6]}...{api_key[-4:]}"
    print(f"✅ API key found: {masked_key}")
    print(f"   Length: {len(api_key)} characters")

if __name__ == "__main__":
    print("Python Path:")
    for path in sys.path:
        print(f"  {path}")

    try:
        import dotenv
        print("\nDotenv found at:")
        print(f"  {dotenv.__file__}")
    except ImportError as e:
        print("\nFailed to import dotenv:")
        print(f"  {e}")

    print_api_key_status()
