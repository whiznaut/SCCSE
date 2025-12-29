import os
import json
import base64
from typing import List, Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.enc")
HISTORY_KEY_FILE = os.path.join(DATA_DIR, "history_key.bin")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _get_history_key() -> bytes:
    _ensure_dir()
    if os.path.exists(HISTORY_KEY_FILE):
        with open(HISTORY_KEY_FILE, "rb") as f:
            return f.read()
    key = AESGCM.generate_key(bit_length=256)
    with open(HISTORY_KEY_FILE, "wb") as f:
        f.write(key)
    return key


def _encrypt_json(obj: dict) -> bytes:
    key = _get_history_key()
    aes = AESGCM(key)
    nonce = os.urandom(12)
    plaintext = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    ct = aes.encrypt(nonce, plaintext, None)
    return nonce + ct


def _decrypt_json(blob: bytes) -> dict:
    key = _get_history_key()
    aes = AESGCM(key)
    nonce = blob[:12]
    ct = blob[12:]
    pt = aes.decrypt(nonce, ct, None)
    return json.loads(pt.decode("utf-8"))


def load_history() -> List[Dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "rb") as f:
        blob = f.read()
    data = _decrypt_json(blob)
    return data.get("items", [])


def save_to_history(content: str, content_type: str):
    # we dont save the password 
    if content_type.lower() == "password":
        return

    items = load_history()
    items.insert(0, {"type": content_type, "content": content})
    items = items[:50]   #last 50 only 

    blob = _encrypt_json({"items": items})
    with open(HISTORY_FILE, "wb") as f:
        f.write(blob)
