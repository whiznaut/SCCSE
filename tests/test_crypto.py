from crypto.x25519_keys import generate_keypair
from crypto.signature import generate_signing_keys
from crypto.hybrid_encrypt import encrypt_bundle, decrypt_bundle

# Keys
alice_priv, alice_pub = generate_keypair()
bob_priv, bob_pub = generate_keypair()

alice_sign_priv, alice_sign_pub = generate_signing_keys()

# Encrypt
bundle = encrypt_bundle(
    content="HELLO REIM 🔐",
    sender_signing_private=alice_sign_priv,
    recipient_public_key=bob_pub,
    sender_id="alice",
    content_type="text"
)

# Decrypt
plaintext = decrypt_bundle(
    bundle,
    recipient_private_key=bob_priv,
    sender_signing_public=alice_sign_pub
)

print("Decrypted:", plaintext)
