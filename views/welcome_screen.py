"""
views/welcome_screen.py — Welcome / Landing Screen
The very first screen users see:
  - Animated logo + branding
  - Two big buttons: "Sign Up" and "Log In"
  - Role selector (Admin / Doctor / Patient) appears after choosing action
  - Routes to the correct auth form
"""

import tkinter as tk
from views.theme import COLORS, FONTS, make_frame, make_label, make_button, make_card
from views.auth_screen import AuthScreen


class WelcomeScreen(tk.Frame):
    """
    Fullscreen landing page with Sign Up / Log In entry points.
    """

    def __init__(self, master, db):
        super().__init__(master, bg=COLORS["bg"])
        self.master = master
        self.db = db
        self._build()

    def _build(self):
        # ── Left panel: branding ──────────────────────────────────────
        left = tk.Frame(self, bg=COLORS["teal"], width=400)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Decorative circles
        canvas = tk.Canvas(left, bg=COLORS["teal"], highlightthickness=0, width=400, height=680)
        canvas.pack(fill="both", expand=True)
        canvas.create_oval(-80, -80, 220, 220, fill=COLORS["teal_mid"], outline="")
        canvas.create_oval(200, 500, 480, 780, fill=COLORS["teal_mid"], outline="")
        canvas.create_oval(300, 200, 450, 350, fill=COLORS["teal_dark"], outline="")

        # Logo
        canvas.create_text(200, 240, text="🏥", font=("Helvetica", 64), fill=COLORS["white"])
        canvas.create_text(200, 320, text="Smart Clinic", font=("Georgia", 26, "bold"), fill=COLORS["white"])
        canvas.create_text(200, 355, text="Management System", font=("Georgia", 14), fill="#9FE1CB")
        canvas.create_text(200, 420, text="Alexandria National University", font=("Helvetica", 11), fill="#9FE1CB")
        canvas.create_text(200, 442, text="Faculty of Computer & Information", font=("Helvetica", 11), fill="#9FE1CB")
        canvas.create_text(200, 470, text="Software Engineering Project", font=("Helvetica", 10, "italic"), fill="#5DCAA5")

      

        # ── Right panel: action buttons ───────────────────────────────
        right = tk.Frame(self, bg=COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)

        # Vertical center wrapper
        center = tk.Frame(right, bg=COLORS["bg"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="Welcome Back", font=FONTS["title"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(0, 4))
        tk.Label(center, text="Choose an option to continue",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(pady=(0, 40))

        # Sign Up card
        signup_card = tk.Frame(center, bg=COLORS["surface"],
                               highlightbackground=COLORS["border"], highlightthickness=1,
                               padx=24, pady=20, cursor="hand2")
        signup_card.pack(fill="x", pady=8)
        signup_card.bind("<Button-1>", lambda e: self._show_role_picker("signup"))
        signup_card.bind("<Enter>", lambda e: signup_card.config(highlightbackground=COLORS["teal"], highlightthickness=2))
        signup_card.bind("<Leave>", lambda e: signup_card.config(highlightbackground=COLORS["border"], highlightthickness=1))

        top_s = tk.Frame(signup_card, bg=COLORS["surface"])
        top_s.pack(fill="x")
        tk.Label(top_s, text="✦", font=("Helvetica", 22), bg=COLORS["surface"], fg=COLORS["teal"]).pack(side="left", padx=(0, 12))
        lbl_s = tk.Frame(top_s, bg=COLORS["surface"])
        lbl_s.pack(side="left")
        tk.Label(lbl_s, text="Create an Account", font=FONTS["body_b"], bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(lbl_s, text="Register as Admin, Doctor, or Patient", font=FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        tk.Label(top_s, text="→", font=("Helvetica", 18), bg=COLORS["surface"], fg=COLORS["teal"]).pack(side="right")

        # Log In card
        login_card = tk.Frame(center, bg=COLORS["surface"],
                              highlightbackground=COLORS["border"], highlightthickness=1,
                              padx=24, pady=20, cursor="hand2")
        login_card.pack(fill="x", pady=8)
        login_card.bind("<Button-1>", lambda e: self._show_role_picker("login"))
        login_card.bind("<Enter>", lambda e: login_card.config(highlightbackground=COLORS["blue"], highlightthickness=2))
        login_card.bind("<Leave>", lambda e: login_card.config(highlightbackground=COLORS["border"], highlightthickness=1))

        top_l = tk.Frame(login_card, bg=COLORS["surface"])
        top_l.pack(fill="x")
        tk.Label(top_l, text="◎", font=("Helvetica", 22), bg=COLORS["surface"], fg=COLORS["blue"]).pack(side="left", padx=(0, 12))
        lbl_l = tk.Frame(top_l, bg=COLORS["surface"])
        lbl_l.pack(side="left")
        tk.Label(lbl_l, text="Log In", font=FONTS["body_b"], bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(lbl_l, text="Access your existing account", font=FONTS["small"], bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")
        tk.Label(top_l, text="→", font=("Helvetica", 18), bg=COLORS["surface"], fg=COLORS["blue"]).pack(side="right")

        # Demo hint
        hint = tk.Frame(center, bg=COLORS["bg"])
        hint.pack(pady=(24, 0))
        tk.Label(hint, text="Demo accounts:  admin/admin123 • dr.ahmed/doc123 • youssef/pat123",
                 font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_muted"]).pack()

    def _show_role_picker(self, action: str):
        """
        Slide in a role-picker overlay (Admin / Doctor / Patient)
        before going to the auth form.
        """
        # Clear right panel and show role selection
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget("bg") == COLORS["bg"]:
                widget.destroy()

        right = tk.Frame(self, bg=COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)

        center = tk.Frame(right, bg=COLORS["bg"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        action_label = "Create Account As" if action == "signup" else "Log In As"
        tk.Label(center, text=action_label, font=FONTS["title"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(0, 8))
        tk.Label(center, text="Select your role to continue",
                 font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(pady=(0, 32))

        roles = [
            ("admin",   "⚙",  "Admin",   "Full system control",          COLORS["purple"], COLORS["purple_light"], COLORS["purple_dark"]),
            ("doctor",  "🩺", "Doctor",  "Manage appointments & records", COLORS["teal"],   COLORS["teal_light"],   COLORS["teal_dark"]),
            ("patient", "🧑", "Patient", "Book & track appointments",     COLORS["blue"],   COLORS["blue_light"],   COLORS["blue_dark"]),
        ]

        for role, icon, title, subtitle, accent, bg_c, fg_c in roles:
            card = tk.Frame(center, bg=COLORS["surface"],
                            highlightbackground=COLORS["border"], highlightthickness=1,
                            padx=24, pady=18, cursor="hand2")
            card.pack(fill="x", pady=6)

            row = tk.Frame(card, bg=COLORS["surface"])
            row.pack(fill="x")

            icon_lbl = tk.Label(row, text=icon, font=("Helvetica", 26),
                                bg=bg_c, fg=fg_c, padx=10, pady=6)
            icon_lbl.pack(side="left", padx=(0, 14))

            info = tk.Frame(row, bg=COLORS["surface"])
            info.pack(side="left")
            tk.Label(info, text=title, font=FONTS["body_b"],
                     bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
            tk.Label(info, text=subtitle, font=FONTS["small"],
                     bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(anchor="w")

            arrow = tk.Label(row, text="→", font=("Helvetica", 18),
                             bg=COLORS["surface"], fg=accent)
            arrow.pack(side="right")

            # Capture role in closure
            _role = role
            _action = action
            _accent = accent
            for w in [card, row, info, arrow, icon_lbl]:
                w.bind("<Button-1>", lambda e, r=_role, a=_action: self._go_auth(r, a))
                w.bind("<Enter>", lambda e, c=card, ac=_accent: c.config(highlightbackground=ac, highlightthickness=2))
                w.bind("<Leave>", lambda e, c=card: c.config(highlightbackground=COLORS["border"], highlightthickness=1))

        # Back button
        tk.Label(center, bg=COLORS["bg"]).pack(pady=8)
        back_btn = make_button(center, "← Back", command=self._rebuild, style="ghost")
        back_btn.pack()

    def _go_auth(self, role: str, action: str):
        """Navigate to the AuthScreen for the chosen role and action."""
        for widget in self.winfo_children():
            widget.destroy()
        auth = AuthScreen(self, self.db, role=role, action=action,
                          on_success=self._on_login_success,
                          on_back=self._rebuild)
        auth.pack(fill="both", expand=True)

    def _on_login_success(self, user_obj, profile):
        """Called by AuthScreen after successful login/signup. Launch dashboard."""
        from views.dashboard_router import DashboardRouter
        for widget in self.winfo_children():
            widget.destroy()
        router = DashboardRouter(self, self.db, user_obj, profile)
        router.pack(fill="both", expand=True)

    def _rebuild(self):
        """Go back to the initial welcome screen."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build()
