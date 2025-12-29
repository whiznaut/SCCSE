import tkinter as tk
from client.ui import ClientUI
from client.clipboard import ClipboardMonitor


def main():
    root = tk.Tk()
    ui = ClientUI(root)

    monitor = ClipboardMonitor(
        tk_root=root,
        on_change=ui.update_clipboard_display,
        poll_sec=0.7
    )
    monitor.start()

    root.mainloop()


if __name__ == "__main__":
    main()
