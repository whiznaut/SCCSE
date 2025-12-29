import requests

SERVER_URL = "http://127.0.0.1:8000"

def send_bundle(bundle: dict, recipient_id: str):
    url = f"{SERVER_URL}/upload/{recipient_id}"
    r = requests.post(url, json=bundle, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_bundle(recipient_id: str):
    url = f"{SERVER_URL}/fetch/{recipient_id}"
    r = requests.get(url, timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()

def receive_bundle(my_id: str):
    """
    Wrapper used by the UI.
    """
    return fetch_bundle(my_id)
