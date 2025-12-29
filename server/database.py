# server/database.py
from datetime import datetime
from typing import Dict, Tuple, List, Optional, Any

# recipient_id -> (bundle_dict, stored_at)
_store: Dict[str, Tuple[Dict[str, Any], datetime]] = {}


def save_bundle(recipient_id: str, bundle: Dict[str, Any]) -> None:
    """
    Save (or overwrite) a bundle for the given recipient.
    """
    _store[recipient_id] = (bundle, datetime.utcnow())


def get_bundle_with_timestamp(
    recipient_id: str,
) -> Optional[Tuple[Dict[str, Any], datetime]]:
    """
    Return (bundle, stored_at) for the recipient, or None if not found.
    """
    return _store.get(recipient_id)


def delete_bundle(recipient_id: str) -> None:
    """
    Delete bundle for this recipient if it exists.
    """
    _store.pop(recipient_id, None)


def get_all_items() -> List[Tuple[str, Dict[str, Any], datetime]]:
    """
    Return list of (recipient_id, bundle, stored_at) for all stored bundles.
    Used by the TTL manager during cleanup.
    """
    return [
        (rid, bundle, ts)
        for rid, (bundle, ts) in _store.items()
    ]
