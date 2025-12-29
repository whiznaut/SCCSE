import time
import threading
import re
from typing import Callable, Optional

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def detect_content_type(text: str) -> str:
    t = text.strip()

    if _URL_RE.match(t):
        return "url"

    # Password heuristic (simple):
    # long + has digits + letters + special
    if len(t) >= 8 and any(c.isdigit() for c in t) and any(c.isalpha() for c in t) and any(not c.isalnum() for c in t):
        return "password"

    return "text"


class ClipboardMonitor:
    def __init__(self, tk_root, on_change: Callable[[str, str], None], poll_sec: float = 0.7):
        self.root = tk_root
        self.on_change = on_change
        self.poll_sec = poll_sec
        self._last = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            try:
                txt = self.root.clipboard_get()
            except Exception:
                txt = ""

            if txt and txt != self._last:
                self._last = txt
                ctype = detect_content_type(txt)
                self.on_change(txt, ctype)

            time.sleep(self.poll_sec)
