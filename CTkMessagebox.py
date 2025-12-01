try:
    # Use CTkMessagebox from customtkinter when available
    from customtkinter import CTkMessagebox  # type: ignore
except Exception:
    # Fallback shim using tkinter.messagebox for environments without CTkMessagebox
    import tkinter.messagebox as _tk_messagebox

    class CTkMessagebox:
        def __init__(self, title: str = "", message: str = "", icon: str | None = None):
            icon_name = (icon or "").lower()
            if icon_name in ("cancel", "error", "stop", "warning"):
                _tk_messagebox.showerror(title, message)
            else:
                _tk_messagebox.showinfo(title, message)
