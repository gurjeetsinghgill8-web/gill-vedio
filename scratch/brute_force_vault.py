import json
import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_FILE = Path("secrets/.vault")
SALT_FILE = Path("secrets/.salt")

if not VAULT_FILE.exists() or not SALT_FILE.exists():
    print("Vault or salt file not found locally.")
    exit(1)

salt = SALT_FILE.read_bytes()
encrypted_data = VAULT_FILE.read_bytes()

passwords = [
    "Gurjeet1@1",
    "U4CJs4HKbMMJ",
    "gurjeet",
    "gurjas",
    "gurleen",
    "admin",
    "password",
    "123456",
    "12345678",
]

# Try to find if there are other passwords or let's try these
for pw in passwords:
    try:
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(pw.encode('utf-8')))
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data)
        data = json.loads(decrypted.decode('utf-8'))
        print(f"SUCCESS! Master password is: {pw}")
        print("Vault content keys:")
        for prov, info in data.get("keys", {}).items():
            print(f"- {prov}: key_len={len(info.get('key',''))}, key_start={info.get('key','')[:4]}...")
        exit(0)
    except Exception:
        pass

print("None of the standard passwords decrypted the vault.")
