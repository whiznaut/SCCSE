# server/replay_protection.py
from collections import defaultdict, deque
from typing import Deque, Dict


MAX_NONCES_PER_SENDER = 100  # keep last N nonces for each sender

# sender_id -> deque of nonces
_sender_nonces: Dict[str, Deque[str]] = defaultdict(
    lambda: deque(maxlen=MAX_NONCES_PER_SENDER)
)


def is_replay(sender_id: str, nonce: str) -> bool:
    """
    Return True if we have already seen this nonce for this sender.
    """
    return nonce in _sender_nonces[sender_id]


def store_nonce(sender_id: str, nonce: str) -> None:
    """
    Store a new nonce for a sender.
    """
    dq = _sender_nonces[sender_id]
    if nonce not in dq:
        dq.append(nonce)
