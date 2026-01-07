import customtkinter as ctk

def _create_top_label(Menu, text):
    """Create a top label for the menu"""
    lbl = ctk.CTkLabel(
        Menu,
        text=text,
        font=ctk.CTkFont(family='Consolas', size=15)
    ).pack(pady=14)
    return lbl

def _create_entry_row(Menu, label_text, show=None):
    """Create a labeled entry with buffer"""
    row = ctk.CTkFrame(Menu)
    row.pack(fill='x', pady=7, padx=10)
    labal = ctk.CTkLabel(
        row,
        text=label_text.rjust(9),
        font=('Consolas', 12)
    ).pack(side='left')
    entry = ctk.CTkEntry(row, show=show)
    entry.pack(side='left', padx=(8, 0), fill='x', expand=True)
    return entry

def _create_button_bottom(Menu, text, input_command):
    """Create a button at the bottom of the menu"""
    btn = ctk.CTkButton(
        Menu,
        text=text,
        command=input_command,
        width=180,
        height=40
    )
    btn.pack(pady=12)
    return btn