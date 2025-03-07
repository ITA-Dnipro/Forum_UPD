# File: utils/encryption_utils.py

from cryptography.fernet import Fernet
import os

# Load the encryption key from the environment (or another secure place)
CRYPTOGRAPHY_KEY = os.environ.get("CRYPTOGRAPHY_KEY")

if CRYPTOGRAPHY_KEY is None:
    raise ValueError("CRYPTOGRAPHY_KEY environment variable is not set.")

cipher_suite = Fernet(CRYPTOGRAPHY_KEY)


def encrypt_text(plain_text: str) -> str:
    """Encrypt the plain text."""
    return cipher_suite.encrypt(plain_text.encode()).decode()


def decrypt_text(encrypted_text: str) -> str:
    """Decrypt the encrypted text."""
    return cipher_suite.decrypt(encrypted_text.encode()).decode()
