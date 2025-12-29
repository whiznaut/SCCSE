import os
import json
import base64
from dataclasses import dataclass
from typing import Dict, Optional

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

# DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

DEVICE_PROFILE = os.environ.get("SCCSE_DEVICE", "A")
DATA_DIR = os.path.join(os.path.dirname(__file__), f"data_device_{DEVICE_PROFILE}") # For testing on same device

KEYS_FILE = os.path.join(DATA_DIR, "keys.json")



def _b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")


def _b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


@dataclass
class MyKeys:
    x25519_private: X25519PrivateKey
    x25519_public: X25519PublicKey
    ed25519_private: Ed25519PrivateKey
    ed25519_public: Ed25519PublicKey


def generate_keys() -> MyKeys:
    x_priv = X25519PrivateKey.generate()
    x_pub = x_priv.public_key()

    e_priv = Ed25519PrivateKey.generate()
    e_pub = e_priv.public_key()

    return MyKeys(x_priv, x_pub, e_priv, e_pub)


def save_my_keys(my_id: str, keys: MyKeys):
    _ensure_dir()
    data = load_all()

    x_priv_raw = keys.x25519_private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    x_pub_raw = keys.x25519_public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    e_priv_raw = keys.ed25519_private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    e_pub_raw = keys.ed25519_public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    data["me"] = {
        "my_id": my_id,
        "x25519_private": _b64e(x_priv_raw),
        "x25519_public": _b64e(x_pub_raw),
        "ed25519_private": _b64e(e_priv_raw),
        "ed25519_public": _b64e(e_pub_raw),
    }
    _write(data)


def load_my_keys() -> Optional[MyKeys]:
    data = load_all()
    me = data.get("me")
    if not me:
        return None

    x_priv = X25519PrivateKey.from_private_bytes(_b64d(me["x25519_private"]))
    x_pub = X25519PublicKey.from_public_bytes(_b64d(me["x25519_public"]))

    e_priv = Ed25519PrivateKey.from_private_bytes(_b64d(me["ed25519_private"]))
    e_pub = Ed25519PublicKey.from_public_bytes(_b64d(me["ed25519_public"]))

    return MyKeys(x_priv, x_pub, e_priv, e_pub)


def get_my_id() -> Optional[str]:
    data = load_all()
    me = data.get("me")
    return me.get("my_id") if me else None


def save_peer(peer_id: str, peer_x25519_public_raw: bytes, peer_ed25519_public_raw: bytes):
    _ensure_dir()
    data = load_all()
    peers = data.setdefault("peers", {})
    peers[peer_id] = {
        "x25519_public": _b64e(peer_x25519_public_raw),
        "ed25519_public": _b64e(peer_ed25519_public_raw),
    }
    _write(data)


def load_peer(peer_id: str) -> Optional[Dict[str, bytes]]:
    data = load_all()
    peers = data.get("peers", {})
    p = peers.get(peer_id)
    if not p:
        return None
    return {
        "x25519_public": _b64d(p["x25519_public"]),
        "ed25519_public": _b64d(p["ed25519_public"]),
    }


def list_peers():
    data = load_all()
    return sorted(list((data.get("peers", {}) or {}).keys()))


def export_my_public_bundle() -> Dict[str, str]:
    """هذا تستخدمينه في pairing: تعطيه للجهاز الثاني."""
    data = load_all()
    me = data.get("me")
    if not me:
        raise RuntimeError("No keys found. Generate keys first.")

    return {
        "my_id": me["my_id"],
        "x25519_public": me["x25519_public"],
        "ed25519_public": me["ed25519_public"],
    }


def import_peer_public_bundle(bundle: Dict[str, str]):
    peer_id = bundle["my_id"]
    x_pub = _b64d(bundle["x25519_public"])
    e_pub = _b64d(bundle["ed25519_public"])
    save_peer(peer_id, x_pub, e_pub)


def load_all():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(data: dict):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python -m client.pairing [export|import]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "export":
        bundle = export_my_public_bundle()
        print(json.dumps(bundle, indent=2))

    elif cmd == "import":
        print("Paste peer public bundle JSON, then press Ctrl+D (Linux/macOS) or Ctrl+Z + Enter (Windows):")
        raw = sys.stdin.read()
        data = json.loads(raw)
        import_peer_public_bundle(data)
        print("✔ Peer imported successfully")

    else:
        print("Unknown command:", cmd)
