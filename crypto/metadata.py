import os
import time 

def create_metadata(sender_id: str, content_type: str):
    security_level = "HIGH" if content_type == "password" else "MEDIUM"

    ttl = 30 if security_level == "HIGH" else 300

    return {
        "timestamp": time.time(),
        "ttl": ttl,
        "nonce": os.urandom(16).hex(),
        "sender_id": sender_id,
        "content_type": content_type,
        "security_level": security_level
    }
