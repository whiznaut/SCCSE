import base64
import time

def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")

def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))

from crypto.aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from crypto.x25519_keys import (
    generate_keypair,
    derive_shared_secret,
    derive_aes_key,
    serialize_public_key,
    load_public_key
)
from crypto.metadata import create_metadata
from crypto.signature import sign_metadata, verify_metadata

def encrypt_bundle(content: str,
                   sender_signing_private,
                   recipient_public_key,
                   sender_id: str,
                   content_type: str):

    eph_private, eph_public = generate_keypair()

    recipient_pub = load_public_key(recipient_public_key)
    shared_secret = derive_shared_secret(eph_private, recipient_pub)
    aes_key = derive_aes_key(shared_secret)

    encrypted = aes_gcm_encrypt(content.encode(), aes_key)
    metadata = create_metadata(sender_id, content_type)
    signature = sign_metadata(metadata, sender_signing_private)

    return {
    "ciphertext": b64e(encrypted["ciphertext"]),
    "nonce": b64e(encrypted["nonce"]),
    "tag": b64e(encrypted["tag"]),
    "ephemeral_pubkey": b64e(serialize_public_key(eph_public)),
    "metadata": metadata,
    "signature": b64e(signature)
}


def decrypt_bundle(bundle: dict,
                   recipient_private_key,
                   sender_signing_public):

    eph_public = load_public_key(b64d(bundle["ephemeral_pubkey"]))
    shared_secret = derive_shared_secret(recipient_private_key, eph_public)
    aes_key = derive_aes_key(shared_secret)


    sender_pub = Ed25519PublicKey.from_public_bytes(sender_signing_public)

    verify_metadata(
        bundle["metadata"],
        b64d(bundle["signature"]),
        sender_pub
    )

    now = time.time()
    issued = bundle["metadata"]["timestamp"]
    ttl = bundle["metadata"]["ttl"]

    if now - issued > ttl:
        raise ValueError("Message expired (TTL exceeded)")

    plaintext = aes_gcm_decrypt(
        b64d(bundle["ciphertext"]),
        b64d(bundle["tag"]),
        b64d(bundle["nonce"]),
        aes_key
    )

    return plaintext.decode()


    