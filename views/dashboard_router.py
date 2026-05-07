"""
views/dashboard_router.py — Dashboard Router
After login/signup, this routes each user to the correct dashboard:
  admin   → AdminDashboard
  doctor  → DoctorDashboard
  patient → PatientDashboard
Also provides the persistent top navigation bar.
"""

import tkinter as tk
from views.theme import COLORS, FONTS, ROLE_COLORS, make_button


class DashboardRouter(tk.Frame):
    """
    Hosts the top nav bar and swaps the content area between views.
    Acts as the app shell once the user is authenticated.
    """

    NAV_ITEMS = {
        "admin":   [("dashboard", "Dashboard"), ("patients", "Patients"),
                    ("doctors", "Doctors"), ("appointments", "Appointments")],
        "doctor":  [("dashboard", "Dashboard"), ("appointments", "My Schedule"),
                    ("diagnose", "Add Diagnosis")],
        "patient": [("dashboard", "Dashboard"), ("book", "Book Appointment"),
                    ("my_appointments", "My Appointments"), ("history", "Medical History")],
    }

    def __init__(self, master, db, user_obj, profile: dict):
        super().__init__(master, bg=COLORS["bg"])
        self.db       = db
        self.user     = user_obj
        self.profile  = profile
        self._current = "dashboard"
        self._nav_btns = {}
        self._build()

    def _build(self):
        self._build_topbar()
        self._content = tk.Frame(self, bg=COLORS["bg"])
        self._content.pack(fill="both", expand=True)
        self._show("dashboard")

    def _build_topbar(self):
        rc = ROLE_COLORS[self.user.role]
        bar = tk.Frame(self, bg=COLORS["surface"],
                       highlightbackground=COLORS["border"], highlightthickness=1,
                       height=56)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Brand
        brand = tk.Frame(bar, bg=COLORS["surface"])
        brand.pack(side="left", padx=16)
        tk.Label(brand, text="🏥", font=("Helvetica", 20), bg=COLORS["surface"]).pack(side="left")
        tk.Label(brand, text=" Smart Clinic", font=FONTS["subhead"],
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left")

        # Separator
        tk.Frame(bar, bg=COLORS["border"], width=1).pack(side="left", fill="y", padx=8)

        # Nav buttons
        nav_frame = tk.Frame(bar, bg=COLORS["surface"])
        nav_frame.pack(side="left")
        for key, label in self.NAV_ITEMS[self.user.role]:
            btn = tk.Button(
                nav_frame, text=label, font=FONTS["small_b"],
                bg=COLORS["surface"], fg=COLORS["text_muted"],
                relief="flat", bd=0, cursor="hand2",
                padx=14, pady=16,
                activebackground=rc["bg"], activeforeground=rc["fg"],
                command=lambda k=key: self._show(k)
            )
            btn.pack(side="left")
            self._nav_btns[key] = btn

        # Right: user info + logout
        right = tk.Frame(bar, bg=COLORS["surface"])
        right.pack(side="right", padx=16)

        name = self.profile.get("name", self.user.username)
        initials = "".join(p[0].upper() for p in name.split()[:2]) if name else "U"

        av = tk.Label(right, text=initials, font=FONTS["small_b"],
                      bg=rc["accent"], fg=COLORS["white"],
                      width=3, height=1, relief="flat")
        av.pack(side="left", padx=(0, 8))

        info = tk.Frame(right, bg=COLORS["surface"])
        info.pack(side="left", padx=(0, 16))
        tk.Label(info, text=name, font=FONTS["small_b"],
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        role_badge = tk.Label(info, text=self.user.role.upper(),
                              font=("Helvetica", 8, "bold"),
                              bg=rc["bg"], fg=rc["fg"], padx=6, pady=1)
        role_badge.pack(anchor="w")

        make_button(right, "Logout", self._logout, style="ghost").pack(side="left")

    def _show(self, key: str):
        self._current = key
        # Update nav button styles
        rc = ROLE_COLORS[self.user.role]
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.config(bg=rc["bg"], fg=rc["fg"])
            else:
                btn.config(bg=COLORS["surface"], fg=COLORS["text_muted"])

        # Clear content
        for w in self._content.winfo_children():
            w.destroy()

        # Route to correct view
        view = self._make_view(key)
        if view:
            view.pack(fill="both", expand=True)

    def _make_view(self, key: str):
        role = self.user.role
        if role == "admin":
            from views.admin_screen import AdminDashboard, PatientsView, DoctorsView, AppointmentsView
            mapping = {
                "dashboard":    lambda: AdminDashboard(self._content, self.db, self.user, self.profile),
                "patients":     lambda: PatientsView(self._content, self.db),
                "doctors":      lambda: DoctorsView(self._content, self.db),
                "appointments": lambda: AppointmentsView(self._content, self.db),
            }
        elif role == "doctor":
            from views.doctor_screen import DoctorDashboard, DoctorAppointments, DiagnoseView
            mapping = {
                "dashboard":    lambda: DoctorDashboard(self._content, self.db, self.user, self.profile),
                "appointments": lambda: DoctorAppointments(self._content, self.db, self.profile),
                "diagnose":     lambda: DiagnoseView(self._content, self.db, self.profile),
            }
        elif role == "patient":
            from views.patient_screen import PatientDashboard, BookAppointment, MyAppointments, MyHistory
            mapping = {
                "dashboard":       lambda: PatientDashboard(self._content, self.db, self.user, self.profile),
                "book":            lambda: BookAppointment(self._content, self.db, self.profile),
                "my_appointments": lambda: MyAppointments(self._content, self.db, self.profile),
                "history":         lambda: MyHistory(self._content, self.db, self.profile),
            }
        else:
            return None
        factory = mapping.get(key)
        return factory() if factory else None

    def _logout(self):
        from views.welcome_screen import WelcomeScreen
        for w in self.master.winfo_children():
            w.destroy()
        WelcomeScreen(self.master, self.db).pack(fill="both", expand=True)
