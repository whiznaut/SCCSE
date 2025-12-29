from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
import json

def generate_signing_keys():
    private = Ed25519PrivateKey.generate()
    return private, private.public_key()

def sign_metadata(metadata: dict, private_key):
    data = json.dumps(metadata, sort_keys=True).encode()
    return private_key.sign(data)

def verify_metadata(metadata: dict, signature: bytes, public_key):
    data = json.dumps(metadata, sort_keys=True).encode()
    public_key.verify(signature, data)
