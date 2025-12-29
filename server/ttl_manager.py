# server/ttl_manager.py
from datetime import datetime, timedelta
from typing import Dict, Any, Protocol

# Time-to-live settings per content type
TTL_MAP = {
    "password": timedelta(minutes=5),
    "text": timedelta(minutes=30),
    "url": timedelta(minutes=30),
    "file": timedelta(hours=2),
}


def _extract_content_type(bundle: Dict[str, Any]) -> str:
    """
    Try to find the content_type inside the bundle.

    Expected:
        bundle["metadata"]["content_type"]
    Fallbacks:
        bundle["content_type"]
    Default:
        "text"
    """
    meta = bundle.get("metadata") or {}
    ctype = meta.get("content_type") or bundle.get("content_type") or "text"
    return str(ctype).lower()


def is_expired(bundle: Dict[str, Any], stored_at: datetime) -> bool:
    """
    Returns True if this bundle is past its TTL.
    """
    ctype = _extract_content_type(bundle)
    ttl = TTL_MAP.get(ctype, TTL_MAP["text"])
    return datetime.utcnow() > stored_at + ttl


class DatabaseLike(Protocol):
    def get_all_items(self): ...
    def delete_bundle(self, recipient_id: str): ...


def cleanup_expired(db) -> int:
    """
    Delete all expired bundles from the given database module.

    Returns:
        number of deleted bundles.
    """
    removed = 0
    # copy to list() so we can modify during iteration
    for rid, bundle, ts in list(db.get_all_items()):
        if is_expired(bundle, ts):
            db.delete_bundle(rid)
            removed += 1
    return removed
