"""
views/theme.py — Shared UI Theme & Reusable Widget Helpers
All colors, fonts, and common widget factories live here so every
view stays visually consistent. Import this in every view file.
"""

import tkinter as tk
from tkinter import ttk

# ------------------------------------------------------------------ #
#  COLOR PALETTE                                                      #
# ------------------------------------------------------------------ #

COLORS = {
    # Primary brand
    "teal":         "#1D9E75",
    "teal_light":   "#E1F5EE",
    "teal_dark":    "#085041",
    "teal_mid":     "#0F6E56",

    # Accent
    "blue":         "#378ADD",
    "blue_light":   "#E6F1FB",
    "blue_dark":    "#0C447C",

    # Roles
    "coral":        "#D85A30",
    "coral_light":  "#FAECE7",
    "coral_dark":   "#712B13",

    "amber":        "#BA7517",
    "amber_light":  "#FAEEDA",
    "amber_dark":   "#633806",

    "purple":       "#534AB7",
    "purple_light": "#EEEDFE",
    "purple_dark":  "#3C3489",

    "green":        "#639922",
    "green_light":  "#EAF3DE",
    "green_dark":   "#3B6D11",

    "red":          "#E24B4A",
    "red_light":    "#FCEBEB",
    "red_dark":     "#A32D2D",

    # Neutrals
    "gray":         "#888780",
    "gray_light":   "#F1EFE8",
    "gray_dark":    "#2C2C2A",
    "white":        "#FFFFFF",
    "bg":           "#F0F4F8",
    "surface":      "#FFFFFF",
    "border":       "#E2E8F0",
    "text":         "#1A202C",
    "text_muted":   "#718096",
}

ROLE_COLORS = {
    "admin":   {"bg": COLORS["purple_light"], "fg": COLORS["purple_dark"], "accent": COLORS["purple"]},
    "doctor":  {"bg": COLORS["teal_light"],   "fg": COLORS["teal_dark"],   "accent": COLORS["teal"]},
    "patient": {"bg": COLORS["blue_light"],   "fg": COLORS["blue_dark"],   "accent": COLORS["blue"]},
}

STATUS_COLORS = {
    "Pending":     (COLORS["amber_light"],  COLORS["amber_dark"]),
    "Confirmed":   (COLORS["teal_light"],   COLORS["teal_dark"]),
    "Completed":   (COLORS["green_light"],  COLORS["green_dark"]),
    "Cancelled":   (COLORS["red_light"],    COLORS["red_dark"]),
    "Rescheduled": (COLORS["blue_light"],   COLORS["blue_dark"]),
}

# ------------------------------------------------------------------ #
#  FONTS                                                              #
# ------------------------------------------------------------------ #

FONTS = {
    "title":    ("Georgia", 22, "bold"),
    "heading":  ("Georgia", 16, "bold"),
    "subhead":  ("Georgia", 13, "bold"),
    "body":     ("Helvetica", 12),
    "body_b":   ("Helvetica", 12, "bold"),
    "small":    ("Helvetica", 10),
    "small_b":  ("Helvetica", 10, "bold"),
    "label":    ("Helvetica", 11),
    "label_b":  ("Helvetica", 11, "bold"),
    "button":   ("Helvetica", 12, "bold"),
    "mono":     ("Courier", 11),
}

# ------------------------------------------------------------------ #
#  REUSABLE WIDGET FACTORIES                                          #
# ------------------------------------------------------------------ #

def make_frame(parent, bg=None, **kw):
    bg = bg or COLORS["bg"]
    return tk.Frame(parent, bg=bg, **kw)


def make_card(parent, **kw):
    """White card with a subtle border."""
    return tk.Frame(parent, bg=COLORS["surface"],
                    relief="flat", bd=0,
                    highlightbackground=COLORS["border"],
                    highlightthickness=1, **kw)


def make_label(parent, text, font_key="body", fg=None, bg=None, **kw):
    fg = fg or COLORS["text"]
    bg = bg or parent.cget("bg")
    return tk.Label(parent, text=text, font=FONTS[font_key],
                    fg=fg, bg=bg, **kw)


def make_entry(parent, width=28, show=None, **kw):
    e = tk.Entry(parent, font=FONTS["body"], width=width,
                 bg=COLORS["white"], fg=COLORS["text"],
                 relief="flat", bd=0,
                 highlightbackground=COLORS["border"],
                 highlightthickness=1,
                 insertbackground=COLORS["text"],
                 **kw)
    if show:
        e.config(show=show)
    # hover highlight
    e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=COLORS["teal"], highlightthickness=2))
    e.bind("<FocusOut>", lambda _: e.config(highlightbackground=COLORS["border"], highlightthickness=1))
    return e


def make_combobox(parent, values, width=26, **kw):
    style = ttk.Style()
    style.configure("Clinic.TCombobox",
                     fieldbackground=COLORS["white"],
                     background=COLORS["white"],
                     foreground=COLORS["text"],
                     arrowcolor=COLORS["teal"])
    cb = ttk.Combobox(parent, values=values, width=width,
                       font=FONTS["body"], state="readonly",
                       style="Clinic.TCombobox", **kw)
    return cb


def make_button(parent, text, command, style="primary", width=None, **kw):
    """
    style options: primary | secondary | danger | success | info | ghost
    """
    configs = {
        "primary":   {"bg": COLORS["teal"],       "fg": COLORS["white"],      "abg": COLORS["teal_dark"]},
        "secondary": {"bg": COLORS["gray_light"],  "fg": COLORS["gray_dark"],  "abg": COLORS["border"]},
        "danger":    {"bg": COLORS["red"],         "fg": COLORS["white"],      "abg": COLORS["red_dark"]},
        "success":   {"bg": COLORS["green"],       "fg": COLORS["white"],      "abg": COLORS["green_dark"]},
        "info":      {"bg": COLORS["blue"],        "fg": COLORS["white"],      "abg": COLORS["blue_dark"]},
        "ghost":     {"bg": COLORS["white"],       "fg": COLORS["teal"],       "abg": COLORS["teal_light"]},
        "purple":    {"bg": COLORS["purple"],      "fg": COLORS["white"],      "abg": COLORS["purple_dark"]},
        "coral":     {"bg": COLORS["coral"],       "fg": COLORS["white"],      "abg": COLORS["coral_dark"]},
    }
    cfg = configs.get(style, configs["primary"])
    kw_btn = dict(
        text=text, command=command,
        font=FONTS["button"],
        bg=cfg["bg"], fg=cfg["fg"],
        relief="flat", bd=0,
        cursor="hand2",
        padx=18, pady=8,
        activebackground=cfg["abg"],
        activeforeground=cfg["fg"],
    )
    if width:
        kw_btn["width"] = width
    btn = tk.Button(parent, **kw_btn, **kw)
    return btn


def make_scrollable(parent, bg=None):
    """Return (outer_frame, canvas, inner_frame) for scrollable content."""
    bg = bg or COLORS["bg"]
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)

    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return outer, canvas, inner


def make_separator(parent, bg=None):
    bg = bg or COLORS["border"]
    return tk.Frame(parent, bg=bg, height=1)


def make_badge(parent, text, bg, fg, **kw):
    return tk.Label(parent, text=text, font=FONTS["small_b"],
                    bg=bg, fg=fg, padx=8, pady=3,
                    relief="flat", **kw)


def show_error(parent_window, message: str):
    from tkinter import messagebox
    messagebox.showerror("Error", message, parent=parent_window)


def show_success(parent_window, message: str):
    from tkinter import messagebox
    messagebox.showinfo("Success", message, parent=parent_window)


def show_confirm(parent_window, message: str) -> bool:
    from tkinter import messagebox
    return messagebox.askyesno("Confirm", message, parent=parent_window)
