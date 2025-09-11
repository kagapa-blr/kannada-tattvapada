import os
import secrets
from dotenv import load_dotenv

def kannada_to_english_digits(text: str) -> str:
    kn_to_en = str.maketrans("೦೧೨೩೪೫೬೭೮೯", "0123456789")
    return text.translate(kn_to_en)


ENV_FILE = ".env"

def generate_secure_secret(length: int = 32) -> str:
    """
    Generate a cryptographically secure random secret key.
    If SECRET_KEY already exists in .env, return it.
    Otherwise, generate a new one, save it, and return it.
    """
    load_dotenv(ENV_FILE, override=False)

    # If already set in environment or .env → return it
    existing_secret = os.getenv("SECRET_KEY")
    if existing_secret:
        return existing_secret

    # Otherwise, generate a new one
    secret = secrets.token_hex(length)

    # Append SECRET_KEY to .env
    with open(ENV_FILE, "a", encoding="utf-8") as f:
        f.write(f"\nSECRET_KEY={secret}\n")

    return secret
