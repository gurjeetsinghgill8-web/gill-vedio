"""
GILL VEDIO - Security Module
Handles AES-256 encryption for API keys and sensitive data.
Keys are encrypted with Fernet and stored in a local .vault file.
"""

import os
import json
import hashlib
import base64
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

# Paths
SECRETS_DIR = Path(__file__).parent / "secrets"
VAULT_FILE = SECRETS_DIR / ".vault"
SALT_FILE = SECRETS_DIR / ".salt"


def _ensure_secrets_dir():
    """Create secrets directory if it doesn't exist."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)


def _derive_key_from_password(password: str, salt: bytes = None) -> tuple:
    """Derive a Fernet-compatible key from a master password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    return key, salt


def _load_salt() -> bytes:
    """Load or create salt for key derivation."""
    _ensure_secrets_dir()
    if SALT_FILE.exists():
        return SALT_FILE.read_bytes()
    salt = os.urandom(16)
    SALT_FILE.write_bytes(salt)
    return salt


def _get_fernet(master_password: str) -> Fernet:
    """Get a Fernet instance from master password."""
    salt = _load_salt()
    key, _ = _derive_key_from_password(master_password, salt)
    return Fernet(key)


def initialize_vault(master_password: str) -> bool:
    """
    Initialize the encrypted vault with a master password.
    Creates the vault file if it doesn't exist.
    Returns True if successful.
    """
    _ensure_secrets_dir()
    fernet = _get_fernet(master_password)
    
    if not VAULT_FILE.exists():
        # Create new vault with empty data
        vault_data = {"keys": {}, "social_tokens": {}, "initialized": True}
        encrypted = fernet.encrypt(json.dumps(vault_data).encode('utf-8'))
        VAULT_FILE.write_bytes(encrypted)
        logger.info("New vault created successfully.")
        return True
    else:
        # Verify password by trying to decrypt
        try:
            encrypted = VAULT_FILE.read_bytes()
            fernet.decrypt(encrypted)
            logger.info("Vault unlocked successfully.")
            return True
        except Exception:
            logger.error("Invalid master password or corrupted vault.")
            return False


def _read_vault(master_password: str) -> dict:
    """Read and decrypt the vault."""
    fernet = _get_fernet(master_password)
    try:
        encrypted = VAULT_FILE.read_bytes()
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode('utf-8'))
    except Exception as e:
        logger.error(f"Failed to read vault: {e}")
        return {"keys": {}, "social_tokens": {}, "initialized": False}


def _write_vault(master_password: str, vault_data: dict):
    """Encrypt and write data to vault."""
    fernet = _get_fernet(master_password)
    encrypted = fernet.encrypt(json.dumps(vault_data).encode('utf-8'))
    VAULT_FILE.write_bytes(encrypted)


def save_api_key(master_password: str, provider: str, api_key: str, tier: str = "free"):
    """
    Save an API key encrypted in the vault.
    provider: 'google_veo', 'groq', 'gemini', 'nvidia', 'openai', 'anthropic'
    tier: 'free' or 'paid'
    """
    vault = _read_vault(master_password)
    vault["keys"][provider] = {
        "key": api_key,
        "tier": tier,
        "active": True
    }
    _write_vault(master_password, vault)
    logger.info(f"API key saved for {provider} ({tier} tier)")


def get_api_key(master_password: str, provider: str) -> dict:
    """
    Retrieve a decrypted API key from the vault.
    Returns: {"key": "...", "tier": "free", "active": True} or None
    """
    vault = _read_vault(master_password)
    key_data = vault.get("keys", {}).get(provider)
    if key_data and key_data.get("active", False):
        return key_data
    return None


def get_all_api_keys(master_password: str) -> dict:
    """Get all stored API keys."""
    vault = _read_vault(master_password)
    return vault.get("keys", {})


def delete_api_key(master_password: str, provider: str):
    """Remove an API key from the vault."""
    vault = _read_vault(master_password)
    if provider in vault.get("keys", {}):
        del vault["keys"][provider]
        _write_vault(master_password, vault)
        logger.info(f"API key deleted for {provider}")


def save_social_token(master_password: str, platform: str, token: str, username: str = ""):
    """Save social media access token encrypted in vault."""
    vault = _read_vault(master_password)
    vault["social_tokens"][platform] = {
        "token": token,
        "username": username,
        "connected": True
    }
    _write_vault(master_password, vault)
    logger.info(f"Social token saved for {platform}")


def get_social_token(master_password: str, platform: str) -> dict:
    """Retrieve a social media token."""
    vault = _read_vault(master_password)
    return vault.get("social_tokens", {}).get(platform)


def get_all_social_tokens(master_password: str) -> dict:
    """Get all social media tokens."""
    vault = _read_vault(master_password)
    return vault.get("social_tokens", {})


def delete_social_token(master_password: str, platform: str):
    """Remove a social media token."""
    vault = _read_vault(master_password)
    if platform in vault.get("social_tokens", {}):
        del vault["social_tokens"][platform]
        _write_vault(master_password, vault)


def is_vault_initialized() -> bool:
    """Check if the vault has been initialized."""
    return VAULT_FILE.exists()


def verify_password(master_password: str) -> bool:
    """Verify if the master password can decrypt the vault."""
    if not is_vault_initialized():
        return False
    try:
        fernet = _get_fernet(master_password)
        encrypted = VAULT_FILE.read_bytes()
        fernet.decrypt(encrypted)
        return True
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Create a SHA-256 hash of password (for non-critical storage)."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()