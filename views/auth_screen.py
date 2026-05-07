"""
views/auth_screen.py — Authentication Screen
Handles both Sign Up and Log In for all three roles.
  - Admin:   username + password only
  - Doctor:  username + password + name + specialty + phone + schedule + city
  - Patient: username + password + name + age + gender + phone + address + city
Role-specific fields appear dynamically based on role + action.
Security: password hashed before any DB call.
"""

import tkinter as tk
from tkinter import ttk
from views.theme import (
    COLORS, FONTS, ROLE_COLORS,
    make_frame, make_label, make_entry, make_button,
    make_combobox, make_separator, show_error
)
from models.user import User
from models.patient import Patient, CITIES
from models.doctor import Doctor, SPECIALTIES, SCHEDULE_DAYS


class AuthScreen(tk.Frame):
    """
    Combined login / signup form — role-aware.
    Calls on_success(user_obj, profile_dict) when auth succeeds.
    Calls on_back() when user presses Back.
    """

    def __init__(self, master, db, role: str, action: str,
                 on_success, on_back):
        super().__init__(master, bg=COLORS["bg"])
        self.db         = db
        self.role       = role      # 'admin' | 'doctor' | 'patient'
        self.action     = action    # 'login' | 'signup'
        self.on_success = on_success
        self.on_back    = on_back
        self._fields    = {}        # widget references keyed by field name
        self._build()

    # ------------------------------------------------------------------ #
    #  BUILD UI                                                            #
    # ------------------------------------------------------------------ #

    def _build(self):
        rc = ROLE_COLORS[self.role]
        action_word = "Create Account" if self.action == "signup" else "Sign In"
        role_label  = self.role.capitalize()

        # ── Left accent strip ────────────────────────────────────────
        strip = tk.Frame(self, bg=rc["accent"], width=8)
        strip.pack(side="left", fill="y")

        # ── Scrollable main area ─────────────────────────────────────
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(side="left", fill="both", expand=True)

        # Canvas + scrollbar for long forms (doctor signup)
        canvas = tk.Canvas(main, bg=COLORS["bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        vsb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        vsb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=vsb.set)

        inner = tk.Frame(canvas, bg=COLORS["bg"])
        canvas_win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(canvas_win, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def _scroll(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

        # ── Card wrapper ─────────────────────────────────────────────
        card = tk.Frame(inner, bg=COLORS["surface"],
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(padx=60, pady=40, fill="x")

        # Header
        hdr = tk.Frame(card, bg=rc["bg"], padx=28, pady=22)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"{action_word}  —  {role_label}",
                 font=FONTS["heading"], bg=rc["bg"], fg=rc["fg"]).pack(anchor="w")
        tk.Label(hdr,
                 text={"admin":   "System administrator access",
                       "doctor":  "Register / access your doctor account",
                       "patient": "Register / access your patient account"}[self.role],
                 font=FONTS["small"], bg=rc["bg"], fg=rc["fg"]).pack(anchor="w")

        # Form body
        body = tk.Frame(card, bg=COLORS["surface"], padx=28, pady=24)
        body.pack(fill="x")

        self._build_credentials(body)
        if self.action == "signup":
            self._build_signup_fields(body)

        make_separator(body, bg=COLORS["border"]).pack(fill="x", pady=16)

        # Error label
        self._err_var = tk.StringVar()
        self._err_lbl = tk.Label(body, textvariable=self._err_var,
                                  font=FONTS["small"], bg=COLORS["red_light"],
                                  fg=COLORS["red_dark"], wraplength=460,
                                  padx=10, pady=6, justify="left")

        # Buttons
        btn_row = tk.Frame(body, bg=COLORS["surface"])
        btn_row.pack(fill="x")
        make_button(btn_row, "← Back", self.on_back, style="ghost").pack(side="left")
        make_button(btn_row, action_word, self._submit,
                    style="primary" if self.role == "patient"
                          else ("purple" if self.role == "admin" else "primary"),
                    width=18).pack(side="right")

    def _row(self, parent, label: str, widget_builder):
        """Create a label + widget row, return the widget."""
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill="x", pady=6)
        tk.Label(row, text=label, font=FONTS["label_b"], width=18, anchor="w",
                 bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(side="left")
        w = widget_builder(row)
        w.pack(side="left", fill="x", expand=True)
        return w

    def _build_credentials(self, parent):
        tk.Label(parent, text="Account Credentials",
                 font=FONTS["subhead"], bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 10))

        self._fields["username"] = self._row(
            parent, "Username",
            lambda p: make_entry(p, width=30))
        self._fields["password"] = self._row(
            parent, "Password",
            lambda p: make_entry(p, width=30, show="•"))
        if self.action == "signup":
            self._fields["confirm"] = self._row(
                parent, "Confirm Password",
                lambda p: make_entry(p, width=30, show="•"))

    def _build_signup_fields(self, parent):
        make_separator(parent, bg=COLORS["border"]).pack(fill="x", pady=12)
        tk.Label(parent, text="Profile Information",
                 font=FONTS["subhead"], bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(anchor="w", pady=(0, 10))

        if self.role == "admin":
            # Admin only needs credentials
            tk.Label(parent, text="Admins don't need extra profile info.",
                     font=FONTS["body"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).pack(anchor="w")
            return

        if self.role == "doctor":
            self._fields["name"] = self._row(
                parent, "Full Name",
                lambda p: make_entry(p, width=30))
            self._fields["specialty"] = self._row(
                parent, "Specialty",
                lambda p: make_combobox(p, SPECIALTIES, width=28))
            self._fields["phone"] = self._row(
                parent, "Phone",
                lambda p: make_entry(p, width=30))
            self._fields["schedule"] = self._row(
                parent, "Schedule",
                lambda p: make_combobox(p, SCHEDULE_DAYS, width=28))
            self._fields["city"] = self._row(
                parent, "City",
                lambda p: make_combobox(p, CITIES, width=28))

        elif self.role == "patient":
            self._fields["name"] = self._row(
                parent, "Full Name",
                lambda p: make_entry(p, width=30))
            self._fields["age"] = self._row(
                parent, "Age",
                lambda p: make_entry(p, width=10))
            self._fields["gender"] = self._row(
                parent, "Gender",
                lambda p: make_combobox(p, ["Male", "Female"], width=12))
            self._fields["phone"] = self._row(
                parent, "Phone Number",
                lambda p: make_entry(p, width=30))
            self._fields["address"] = self._row(
                parent, "Address",
                lambda p: make_entry(p, width=30))
            self._fields["city"] = self._row(
                parent, "City / Location",
                lambda p: make_combobox(p, CITIES, width=28))
            tk.Label(parent,
                     text="💡 Your city is used to suggest nearby doctors.",
                     font=FONTS["small"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------------------------ #
    #  HELPERS                                                             #
    # ------------------------------------------------------------------ #

    def _get(self, key: str) -> str:
        w = self._fields.get(key)
        if w is None:
            return ""
        if isinstance(w, ttk.Combobox):
            return w.get().strip()
        return w.get().strip()

    def _show_error(self, msg: str):
        self._err_var.set("⚠  " + msg)
        self._err_lbl.pack(fill="x", pady=(0, 10), before=self._err_lbl.master.winfo_children()[-1])

    def _clear_error(self):
        self._err_var.set("")
        self._err_lbl.pack_forget()

    # ------------------------------------------------------------------ #
    #  SUBMIT — Login or Register                                         #
    # ------------------------------------------------------------------ #

    def _submit(self):
        self._clear_error()
        if self.action == "login":
            self._do_login()
        else:
            self._do_signup()

    def _do_login(self):
        username = self._get("username")
        password = self._get("password")
        if not username or not password:
            self._show_error("Please enter your username and password.")
            return
        hashed = User.hash_password(password)
        user_data = self.db.get_user_by_credentials(username, hashed)
        if not user_data:
            self._show_error("Invalid username or password. Please try again.")
            return
        if user_data["role"] != self.role:
            self._show_error(f"This account is not a {self.role} account.")
            return

        user_obj = User(user_data["user_id"], user_data["username"], user_data["role"])
        profile  = self._load_profile(user_obj)
        self.on_success(user_obj, profile)

    def _do_signup(self):
        username = self._get("username")
        password = self._get("password")
        confirm  = self._get("confirm")

        err = User.validate_registration(username, password, confirm)
        if err:
            self._show_error(err)
            return
        if self.db.username_exists(username):
            self._show_error("Username already taken. Please choose another.")
            return

        hashed = User.hash_password(password)
        user_id = self.db.create_user(username, hashed, self.role)

        if self.role == "admin":
            user_obj = User(user_id, username, "admin")
            self.on_success(user_obj, {})
            return

        if self.role == "doctor":
            name     = self._get("name")
            spec     = self._get("specialty")
            phone    = self._get("phone")
            schedule = self._get("schedule")
            city     = self._get("city")
            err = Doctor.validate(name, spec, phone, schedule, city)
            if err:
                self._show_error(err)
                return
            doctor_id = self.db.create_doctor(user_id, name, spec, phone, schedule, city)
            user_obj  = User(user_id, username, "doctor")
            profile   = {"doctor_id": doctor_id, "name": name,
                         "specialty": spec, "phone": phone,
                         "schedule": schedule, "city": city}
            self.on_success(user_obj, profile)
            return

        if self.role == "patient":
            name    = self._get("name")
            age     = self._get("age")
            gender  = self._get("gender")
            phone   = self._get("phone")
            address = self._get("address")
            city    = self._get("city")
            err = Patient.validate(name, age, gender, phone, address, city)
            if err:
                self._show_error(err)
                return
            patient_id = self.db.create_patient(user_id, name, int(age), gender, phone, address, city)
            user_obj   = User(user_id, username, "patient")
            profile    = {"patient_id": patient_id, "name": name,
                          "age": age, "gender": gender, "phone": phone,
                          "address": address, "city": city}
            self.on_success(user_obj, profile)

    def _load_profile(self, user_obj: User) -> dict:
        """Load profile data from DB after successful login."""
        if user_obj.is_doctor():
            d = self.db.get_doctor_by_user_id(user_obj.user_id)
            return d or {}
        if user_obj.is_patient():
            p = self.db.get_patient_by_user_id(user_obj.user_id)
            return p or {}
        return {}
