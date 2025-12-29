# server/main.py
from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from .schemas import (
    Bundle,
    UploadResponse,
    CleanupResponse,
    HealthResponse,
)
from . import database, ttl_manager, replay_protection

app = FastAPI(
    title="Secure Clipboard Relay Server",
    description=(
        "Relay server used by the clipboard client. "
        "It stores encrypted bundles for a short time and never decrypts them."
    ),
    version="1.0.0",
)


def _extract_sender_and_nonce(bundle: Dict[str, Any]):
    """
    Helper to get (sender_id, nonce) from the bundle.

    Expected location:
        bundle["metadata"]["sender_id"]
        bundle["metadata"]["nonce"]
    Fallback:
        bundle["sender_id"], bundle["nonce"]
    """
    meta = bundle.get("metadata") or {}
    sender_id = meta.get("sender_id") or bundle.get("sender_id")
    nonce = meta.get("nonce") or bundle.get("nonce")
    return sender_id, nonce


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Simple endpoint to check that the server is running.
    """
    return HealthResponse(status="ok")


@app.post("/upload/{recipient_id}", response_model=UploadResponse)
def upload_bundle(recipient_id: str, bundle: Bundle) -> UploadResponse:
    """
    Receive an encrypted bundle for a given recipient.

    Steps:
      1. Convert to raw dict (we accept arbitrary crypto fields).
      2. Extract sender_id + nonce for replay protection.
      3. If replay -> 409 error.
      4. Save bundle in in-memory database.
    """
    data = bundle.dict()

    sender_id, nonce = _extract_sender_and_nonce(data)
    if not sender_id or not nonce:
        # This forces the crypto code to provide proper metadata.
        raise HTTPException(
            status_code=400,
            detail="metadata.sender_id and metadata.nonce are required",
        )

    if replay_protection.is_replay(sender_id, nonce):
        raise HTTPException(status_code=409, detail="Replay detected")

    replay_protection.store_nonce(sender_id, nonce)

    database.save_bundle(recipient_id, data)
    return UploadResponse(status="ok", stored_for=recipient_id)


@app.get("/fetch/{recipient_id}")
def fetch_bundle(recipient_id: str):
    """
    Fetch the pending bundle for a recipient.

    - If nothing stored: 404
    - If expired: delete and return 410
    - If valid: delete and return the raw JSON bundle
    """
    stored = database.get_bundle_with_timestamp(recipient_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="No bundle for this recipient")

    bundle, stored_at = stored

    if ttl_manager.is_expired(bundle, stored_at):
        database.delete_bundle(recipient_id)
        raise HTTPException(status_code=410, detail="Bundle expired")

    # one-time delivery: delete then return
    database.delete_bundle(recipient_id)
    return bundle  # FastAPI returns this as JSON directly


@app.post("/cleanup", response_model=CleanupResponse)
def manual_cleanup() -> CleanupResponse:
    """
    Manually trigger cleanup of expired bundles.

    (You could also schedule this as a background job.)
    """
    removed = ttl_manager.cleanup_expired(database)
    return CleanupResponse(status="cleanup_done", removed=removed)
