import tkinter as tk
from tkinter import ttk, messagebox
import time

from client.server_api import send_bundle, fetch_bundle
from client.pairing import load_my_keys, load_peer, list_peers, get_my_id
from client.history import load_history, save_to_history
from crypto.hybrid_encrypt import encrypt_bundle, decrypt_bundle


# ============================
# DESIGN SYSTEM
# ============================
COLORS = {
    "bg": "#020617",
    "panel": "#020617",
    "card": "#020617",
    "border": "#1e293b",
    "text": "#e5e7eb",
    "muted": "#94a3b8",
    "accent": "#38bdf8",
    "success": "#db8f00",
    "warn": "#fbbf24",
    "danger": "#f87171",
}

FONT_H = ("Segoe UI", 17, "bold")
FONT_M = ("Segoe UI", 11, "bold")
FONT_S = ("Segoe UI", 9)


class ClientUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("SCCSE — Secure Clipboard Exchange")
        root.geometry("980x620")
        root.configure(bg=COLORS["bg"])
        root.resizable(False, False)

        self.current_text = ""
        self.current_type = "text"

        self.my_id = get_my_id()
        if not self.my_id:
            messagebox.showerror("Error", "Run pairing first.")
            root.destroy()
            return

        self._build_layout()
        self.refresh_history()

    # ============================
    # TOAST NOTIFICATION
    # ============================
    def toast(self, message, kind="success"):
        bg = COLORS["success"] if kind == "success" else COLORS["warn"]

        t = tk.Toplevel(self.root)
        t.overrideredirect(True)
        t.configure(bg=bg)

        x = self.root.winfo_x() + self.root.winfo_width() - 260
        y = self.root.winfo_y() + self.root.winfo_height() - 90
        t.geometry(f"240x50+{x}+{y}")

        tk.Label(
            t, text=message,
            bg=bg, fg="black",
            font=FONT_S
        ).pack(expand=True, fill="both", padx=10, pady=10)

        t.after(2200, t.destroy)

    # ============================
    # LAYOUT
    # ============================
    def _build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=COLORS["panel"], width=220)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(
            self.sidebar, text="🔐 SCCSE",
            fg=COLORS["accent"], bg=COLORS["panel"],
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(22, 6))

        tk.Label(
            self.sidebar,
            text=f"Device ID\n{self.my_id}",
            fg=COLORS["muted"],
            bg=COLORS["panel"],
            font=FONT_S,
            justify="center"
        ).pack(pady=(0, 22))

        self.nav_buttons = {}
        for name in ["Clipboard", "Security Log", "About"]:
            b = tk.Button(
                self.sidebar,
                text=name,
                bg=COLORS["panel"],
                fg=COLORS["text"],
                relief="flat",
                font=FONT_M,
                command=lambda n=name: self.show_tab(n)
            )
            b.pack(fill="x", padx=20, pady=4)
            self.nav_buttons[name] = b

        self.main = tk.Frame(self.root, bg=COLORS["bg"])
        self.main.pack(side="right", fill="both", expand=True)

        self.tabs = {
            "Clipboard": self._clipboard_tab(),
            "Security Log": self._history_tab(),
            "About": self._about_tab()
        }
        self.show_tab("Clipboard")

    def show_tab(self, name):
        for t in self.tabs.values():
            t.pack_forget()
        self.tabs[name].pack(fill="both", expand=True)

        for k, b in self.nav_buttons.items():
            b.configure(fg=COLORS["accent"] if k == name else COLORS["text"])

    # ============================
    # CLIPBOARD TAB
    # ============================
    def _clipboard_tab(self):
        f = tk.Frame(self.main, bg=COLORS["bg"])

        tk.Label(f, text="Secure Clipboard", fg=COLORS["text"], bg=COLORS["bg"], font=FONT_H)\
            .pack(anchor="w", padx=30, pady=(20, 4))

        self.sec_badge = tk.Label(
            f, text="MEDIUM SECURITY",
            fg=COLORS["warn"], bg=COLORS["bg"], font=FONT_S
        )
        self.sec_badge.pack(anchor="w", padx=30)

        self.text_box = tk.Text(
            f, height=7,
            bg=COLORS["panel"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat", padx=14, pady=14
        )
        self.text_box.pack(fill="x", padx=30, pady=14)

        self.ttl_bar = ttk.Progressbar(f, length=420)
        self.ttl_bar.pack(padx=30, pady=(0, 14))

        peers = list_peers()
        self.peer_var = tk.StringVar(value=peers[0] if peers else "No peers")
        ttk.Combobox(f, values=peers, textvariable=self.peer_var, state="readonly")\
            .pack(padx=30, pady=8)

        btns = tk.Frame(f, bg=COLORS["bg"])
        btns.pack(padx=30, pady=10)

        self.send_btn = self._accent_button(btns, "🔒 Encrypt & Send", self.send_current)
        self.send_btn.pack(side="left", padx=6)

        self.recv_btn = self._ghost_button(btns, "📥 Receive & Decrypt", self.receive)
        self.recv_btn.pack(side="left", padx=6)

        return f

    # ============================
    # HISTORY TAB
    # ============================
    def _history_tab(self):
        f = tk.Frame(self.main, bg=COLORS["bg"])
        tk.Label(f, text="Security Log", fg=COLORS["text"], bg=COLORS["bg"], font=FONT_H)\
            .pack(anchor="w", padx=30, pady=20)

        self.history = tk.Listbox(
            f, bg=COLORS["panel"], fg=COLORS["muted"],
            relief="flat", height=20
        )
        self.history.pack(fill="both", padx=30, pady=10)
        return f

    def _about_tab(self):
        f = tk.Frame(self.main, bg=COLORS["bg"])
        tk.Label(
            f,
            text=(
                "SCCSE — Secure Cross-Clipboard Exchange System\n\n"
                "End-to-end encrypted clipboard transfer\n"
                "Untrusted relay server model\n"
                "Hybrid encryption + signatures\n"
                "TTL-enforced confidentiality\n\n"
                "Academic cryptographic system"
            ),
            fg=COLORS["muted"],
            bg=COLORS["bg"],
            font=FONT_S,
            justify="left"
        ).pack(padx=40, pady=40, anchor="w")
        return f

    # ============================
    # BUTTON STYLES
    # ============================
    def _accent_button(self, parent, text, cmd):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=COLORS["accent"], fg="black",
            relief="flat", font=FONT_M, padx=22, pady=10
        )

    def _ghost_button(self, parent, text, cmd):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=COLORS["panel"], fg=COLORS["text"],
            relief="flat", font=FONT_M, padx=22, pady=10
        )

    # ============================
    # CORE LOGIC HOOKS
    # ============================
    def update_clipboard_display(self, text, content_type):
        self.current_text = text
        self.current_type = content_type

        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, text)

        if content_type == "password":
            self.sec_badge.config(text="HIGH SECURITY", fg=COLORS["danger"])
            self.start_ttl(30)
        else:
            self.sec_badge.config(text="MEDIUM SECURITY", fg=COLORS["warn"])
            self.start_ttl(300)

    def start_ttl(self, seconds):
        self.ttl_total = seconds
        self.ttl_left = seconds
        self._ttl_tick()

    def _ttl_tick(self):
        self.ttl_bar["value"] = (self.ttl_left / self.ttl_total) * 100
        self.ttl_left -= 1

        if self.ttl_left >= 0:
            self.root.after(1000, self._ttl_tick)
        else:
            # 🔥 TTL expired — enforce wipe for HIGH security
            if self.current_type == "password":
                self.root.clipboard_clear()
                self.text_box.delete("1.0", tk.END)
                self.current_text = ""
                self.sec_badge.config(text="EXPIRED", fg=COLORS["muted"])
                self.toast("High-security content expired", kind="warn")


    # ============================
    # SEND / RECEIVE
    # ============================
    def send_current(self):
        if not self.current_text:
            return

        peer = load_peer(self.peer_var.get())
        keys = load_my_keys()

        bundle = encrypt_bundle(
            content=self.current_text,
            sender_signing_private=keys.ed25519_private,
            recipient_public_key=peer["x25519_public"],
            sender_id=self.my_id,
            content_type=self.current_type
        )

        send_bundle(bundle, self.peer_var.get())
        save_to_history(self.current_text, self.current_type)
        self.refresh_history()
        self.toast("Encrypted & sent securely")

    def receive(self):
        keys = load_my_keys()
        bundle = fetch_bundle(self.my_id)
        if not bundle:
            return

        metadata = bundle.get("metadata", {})
        content_type = metadata.get("content_type", "text")

        peer = load_peer(metadata["sender_id"])
        plaintext = decrypt_bundle(
            bundle,
            recipient_private_key=keys.x25519_private,
            sender_signing_public=peer["ed25519_public"]
        )

        self.root.clipboard_clear()
        self.root.clipboard_append(plaintext)

        # 🔒 Do NOT log high-security content
        if content_type != "password":
            save_to_history(plaintext, content_type)

        self.refresh_history()
        self.toast("Decrypted & copied to clipboard")


    # ============================
    # HISTORY (SAFE)
    # ============================
    def refresh_history(self):
        self.history.delete(0, tk.END)
        items = load_history()

        if not items:
            self.history.insert(tk.END, "No secure transfers yet.")
            return

        for i in items:
            if i["type"] == "password":
                entry = "✔ PASSWORD — [REDACTED]"
            else:
                entry = f"✔ {i['type'].upper()} — {i['content'][:60]}"
            self.history.insert(tk.END, entry)

