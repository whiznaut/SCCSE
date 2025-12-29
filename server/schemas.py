# server/schemas.py
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Bundle(BaseModel):
    """
    Generic bundle model.

    We don't fix fields here because the crypto code may add anything it wants.
    We only *expect* (but do not strictly enforce) that the JSON has:
        {
          "ciphertext": "...",
          "nonce": "...",               # AEAD nonce (optional, can also be inside metadata)
          "tag": "...",                 # auth tag (optional)
          "ephemeral_pubkey": "...",    # optional
          "metadata": {
              "sender_id": "...",
              "nonce": "...",
              "content_type": "text|url|password|file",
              "timestamp": "...",
              ...
          },
          "signature": "..."
        }
    """
    class Config:
        extra = "allow"  # accept any extra keys


class UploadResponse(BaseModel):
    status: str = Field(..., description="Status string, e.g. 'ok'")
    stored_for: str = Field(..., description="Recipient ID this bundle was stored for")


class CleanupResponse(BaseModel):
    status: str = Field(..., description="Status string, e.g. 'cleanup_done'")
    removed: int = Field(..., description="Number of expired bundles removed")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Server health status, e.g. 'ok'")
