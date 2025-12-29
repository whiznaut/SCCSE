from crypto.hybrid_encrypt import encrypt_bundle, decrypt_bundle
from client.pairing import load_my_keys, load_peer


def encrypt_for_peer(
    plaintext: str,
    content_type: str,
    sender_id: str,
    recipient_id: str,
):
    # Load keys
    my_keys = load_my_keys()
    peer = load_peer(recipient_id)

    if not my_keys or not peer:
        raise RuntimeError("Keys not initialized or peer not paired")

    return encrypt_bundle(
        content=plaintext,
        sender_signing_private=my_keys.ed25519_private,
        recipient_public_key=peer["x25519_public"],
        sender_id=sender_id,
        content_type=content_type
    )


def decrypt_from_peer(bundle: dict):
    my_keys = load_my_keys()
    sender_id = bundle["metadata"]["sender_id"]
    peer = load_peer(sender_id)

    if not my_keys or not peer:
        raise RuntimeError("Missing keys or peer")

    return decrypt_bundle(
        bundle=bundle,
        recipient_private_key=my_keys.x25519_private,
        sender_signing_public=peer["ed25519_public"]
    )
