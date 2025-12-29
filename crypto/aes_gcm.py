from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def aes_gcm_encrypt(plaintext: bytes, key: bytes):
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return {
        "ciphertext": ciphertext[:-16],
        "tag": ciphertext[-16:],
        "nonce": nonce
    }

def aes_gcm_decrypt(ciphertext: bytes, tag: bytes, nonce: bytes, key: bytes):
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext + tag, None)
