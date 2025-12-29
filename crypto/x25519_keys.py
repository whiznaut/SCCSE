from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey, X25519PublicKey
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization

def generate_keypair():
    private = X25519PrivateKey.generate()
    public = private.public_key()
    return private, public

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

def load_public_key(raw_bytes):
    return X25519PublicKey.from_public_bytes(raw_bytes)

def derive_shared_secret(private_key, peer_public_key):
    return private_key.exchange(peer_public_key)

def derive_aes_key(shared_secret: bytes):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'clipboard-sync'
    ).derive(shared_secret)
