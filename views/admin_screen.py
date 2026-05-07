"""
views/admin_screen.py — Admin Dashboard Views
  AdminDashboard  — stats overview + today's schedule
  PatientsView    — list, search, register, delete patients
  DoctorsView     — list, search, add, delete doctors
  AppointmentsView— view all, confirm, cancel, reschedule
"""

import tkinter as tk
from tkinter import ttk
from datetime import date as today_date
from views.theme import (
    COLORS, FONTS, STATUS_COLORS,
    make_frame, make_label, make_button, make_entry,
    make_combobox, make_separator, make_scrollable,
    show_error, show_success, show_confirm
)
from models.doctor import SPECIALTIES, SCHEDULE_DAYS
from models.patient import CITIES
from models.user import User


# ------------------------------------------------------------------ #
#  HELPERS                                                             #
# ------------------------------------------------------------------ #

def stat_card(parent, label, value, color):
    card = tk.Frame(parent, bg=COLORS["surface"],
                    highlightbackground=color, highlightthickness=2)
    card.pack(side="left", padx=6, fill="y")
    tk.Label(card, text=str(value), font=("Georgia", 26, "bold"),
             bg=COLORS["surface"], fg=color, width=6).pack(pady=(14, 2))
    tk.Label(card, text=label, font=FONTS["small"],
             bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(pady=(0, 14), padx=16)


def make_table(parent, columns: list, rows: list, col_widths=None, row_actions=None):
    """
    Build a ttk.Treeview table.
    columns: list of header strings
    rows: list of tuples matching columns
    row_actions: callable(tree, row_data) called when a row is selected — optional
    """
    frame = tk.Frame(parent, bg=COLORS["surface"])

    style = ttk.Style()
    style.configure("Clinic.Treeview",
                     background=COLORS["surface"],
                     foreground=COLORS["text"],
                     rowheight=32,
                     fieldbackground=COLORS["surface"],
                     font=FONTS["body"])
    style.configure("Clinic.Treeview.Heading",
                     background=COLORS["gray_light"],
                     foreground=COLORS["gray_dark"],
                     font=FONTS["small_b"])
    style.map("Clinic.Treeview", background=[("selected", COLORS["teal_light"])],
              foreground=[("selected", COLORS["teal_dark"])])

    tree = ttk.Treeview(frame, columns=columns, show="headings",
                         style="Clinic.Treeview", selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    for i, col in enumerate(columns):
        w = col_widths[i] if col_widths else 120
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="w")

    for row in rows:
        tree.insert("", "end", values=row)

    if row_actions:
        tree.bind("<<TreeviewSelect>>", lambda e: row_actions(tree))

    return frame, tree


# ================================================================== #
#  ADMIN DASHBOARD                                                    #
# ================================================================== #

class AdminDashboard(tk.Frame):
    def __init__(self, master, db, user, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        stats = self.db.get_stats()

        # Title
        tk.Label(inner, text="Admin Dashboard", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(inner, text="System overview and today's activity",
                 font=FONTS["body"], bg=COLORS["bg"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 16))

        # Stat cards row
        row = tk.Frame(inner, bg=COLORS["bg"])
        row.pack(fill="x", pady=(0, 20))
        stat_card(row, "Patients",    stats["patients"],     COLORS["blue"])
        stat_card(row, "Doctors",     stats["doctors"],      COLORS["teal"])
        stat_card(row, "Confirmed",   stats["confirmed"],    COLORS["green"])
        stat_card(row, "Pending",     stats["pending"],      COLORS["amber"])
        stat_card(row, "Completed",   stats["completed"],    COLORS["purple"])
        stat_card(row, "Records",     stats["records"],      COLORS["coral"])

        # Today's appointments
        today = str(today_date.today())
        appts = [a for a in self.db.get_all_appointments() if a["date"] == today]

        section = tk.Frame(inner, bg=COLORS["surface"],
                           highlightbackground=COLORS["border"], highlightthickness=1)
        section.pack(fill="x")
        hdr = tk.Frame(section, bg=COLORS["teal_light"], padx=14, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Today's Schedule  ({today})",
                 font=FONTS["subhead"], bg=COLORS["teal_light"],
                 fg=COLORS["teal_dark"]).pack(anchor="w")

        body = tk.Frame(section, bg=COLORS["surface"], padx=14, pady=10)
        body.pack(fill="x")
        if not appts:
            tk.Label(body, text="No appointments scheduled today.",
                     font=FONTS["body"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).pack()
        else:
            cols = ["Time", "Patient", "Doctor", "Specialty", "Status"]
            rows_data = [(a["time"], a["patient_name"], a["doctor_name"],
                          a["specialty"], a["status"]) for a in appts]
            tbl, _ = make_table(body, cols, rows_data, [70, 180, 180, 140, 100])
            tbl.pack(fill="x")


# ================================================================== #
#  PATIENTS VIEW                                                      #
# ================================================================== #

class PatientsView(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        # Header
        hrow = tk.Frame(inner, bg=COLORS["bg"])
        hrow.pack(fill="x", pady=(0, 14))
        tk.Label(hrow, text="Patient Management", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        make_button(hrow, "+ Register Patient", self._open_add, style="primary").pack(side="right")

        self._alert_var = tk.StringVar()
        alert = tk.Label(inner, textvariable=self._alert_var, font=FONTS["small"],
                         bg=COLORS["green_light"], fg=COLORS["green_dark"],
                         padx=10, pady=6, anchor="w")

        # Table frame
        self._table_frame = tk.Frame(inner, bg=COLORS["surface"],
                                      highlightbackground=COLORS["border"], highlightthickness=1)
        self._table_frame.pack(fill="both", expand=True)
        self._refresh_table()

    def _refresh_table(self):
        for w in self._table_frame.winfo_children():
            w.destroy()
        patients = self.db.get_all_patients()
        cols = ["ID", "Name", "Age", "Gender", "Phone", "City", "Address", "Action"]
        rows = [(p["patient_id"], p["name"], p["age"], p["gender"],
                 p["phone"], p["city"], p["address"], "Delete") for p in patients]
        tbl, tree = make_table(self._table_frame, cols, rows,
                                [40, 180, 50, 70, 120, 110, 180, 70])
        tbl.pack(fill="both", expand=True)

        def on_select(t):
            sel = t.selection()
            if not sel:
                return
            vals = t.item(sel[0], "values")
            if vals[-1] == "Delete":
                pid = int(vals[0])
                if show_confirm(self, f"Delete patient '{vals[1]}'? This will also remove their appointments and history."):
                    self.db.delete_patient(pid)
                    self._refresh_table()
                    self._alert_var.set(f"Patient '{vals[1]}' deleted.")

        tree.bind("<<TreeviewSelect>>", lambda e: on_select(tree))

    def _open_add(self):
        win = tk.Toplevel(self)
        win.title("Register New Patient")
        win.geometry("520x560")
        win.configure(bg=COLORS["bg"])
        win.grab_set()

        card = tk.Frame(win, bg=COLORS["surface"], padx=28, pady=24)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(card, text="Register New Patient", font=FONTS["heading"],
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 16))

        fields = {}
        def row(lbl, w_fn):
            r = tk.Frame(card, bg=COLORS["surface"])
            r.pack(fill="x", pady=5)
            tk.Label(r, text=lbl, font=FONTS["label_b"], width=16, anchor="w",
                     bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(side="left")
            w = w_fn(r)
            w.pack(side="left", fill="x", expand=True)
            return w

        fields["username"] = row("Username",    lambda p: make_entry(p))
        fields["password"] = row("Password",    lambda p: make_entry(p, show="•"))
        fields["name"]     = row("Full Name",   lambda p: make_entry(p))
        fields["age"]      = row("Age",         lambda p: make_entry(p, width=8))
        fields["gender"]   = row("Gender",      lambda p: make_combobox(p, ["Male", "Female"], 12))
        fields["phone"]    = row("Phone",       lambda p: make_entry(p))
        fields["address"]  = row("Address",     lambda p: make_entry(p))
        fields["city"]     = row("City",        lambda p: make_combobox(p, CITIES, 22))

        err_var = tk.StringVar()
        err_lbl = tk.Label(card, textvariable=err_var, font=FONTS["small"],
                           bg=COLORS["red_light"], fg=COLORS["red_dark"], padx=8, pady=4)

        def submit():
            from models.patient import Patient
            vals = {k: (w.get().strip() if not isinstance(w, ttk.Combobox) else w.get().strip())
                    for k, w in fields.items()}
            err = User.validate_registration(vals["username"], vals["password"], vals["password"])
            if err:
                err_var.set(err); err_lbl.pack(fill="x", pady=4); return
            if self.db.username_exists(vals["username"]):
                err_var.set("Username already taken."); err_lbl.pack(fill="x", pady=4); return
            err2 = Patient.validate(vals["name"], vals["age"], vals["gender"],
                                    vals["phone"], vals["address"], vals["city"])
            if err2:
                err_var.set(err2); err_lbl.pack(fill="x", pady=4); return
            uid = self.db.create_user(vals["username"], User.hash_password(vals["password"]), "patient")
            self.db.create_patient(uid, vals["name"], int(vals["age"]),
                                   vals["gender"], vals["phone"], vals["address"], vals["city"])
            win.destroy()
            self._refresh_table()

        make_separator(card, bg=COLORS["border"]).pack(fill="x", pady=10)
        btn_row = tk.Frame(card, bg=COLORS["surface"])
        btn_row.pack(fill="x")
        make_button(btn_row, "Cancel", win.destroy, style="secondary").pack(side="left")
        make_button(btn_row, "Register", submit, style="primary").pack(side="right")


# ================================================================== #
#  DOCTORS VIEW                                                       #
# ================================================================== #

class DoctorsView(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        hrow = tk.Frame(inner, bg=COLORS["bg"])
        hrow.pack(fill="x", pady=(0, 14))
        tk.Label(hrow, text="Doctor Management", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        make_button(hrow, "+ Add Doctor", self._open_add, style="primary").pack(side="right")

        self._table_frame = tk.Frame(inner, bg=COLORS["surface"],
                                      highlightbackground=COLORS["border"], highlightthickness=1)
        self._table_frame.pack(fill="both", expand=True)
        self._refresh_table()

    def _refresh_table(self):
        for w in self._table_frame.winfo_children():
            w.destroy()
        doctors = self.db.get_all_doctors()
        cols = ["ID", "Name", "Specialty", "Phone", "City", "Schedule", "Action"]
        rows = [(d["doctor_id"], d["name"], d["specialty"], d["phone"],
                 d["city"], d["schedule"], "Delete") for d in doctors]
        tbl, tree = make_table(self._table_frame, cols, rows,
                                [40, 180, 130, 110, 100, 170, 70])
        tbl.pack(fill="both", expand=True)

        def on_select(t):
            sel = t.selection()
            if not sel: return
            vals = t.item(sel[0], "values")
            if vals[-1] == "Delete":
                did = int(vals[0])
                if show_confirm(self, f"Delete Dr. '{vals[1]}'?"):
                    self.db.delete_doctor(did)
                    self._refresh_table()

        tree.bind("<<TreeviewSelect>>", lambda e: on_select(tree))

    def _open_add(self):
        win = tk.Toplevel(self)
        win.title("Add New Doctor")
        win.geometry("520x520")
        win.configure(bg=COLORS["bg"])
        win.grab_set()

        card = tk.Frame(win, bg=COLORS["surface"], padx=28, pady=24)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(card, text="Add New Doctor", font=FONTS["heading"],
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 16))

        fields = {}
        def row(lbl, w_fn):
            r = tk.Frame(card, bg=COLORS["surface"])
            r.pack(fill="x", pady=5)
            tk.Label(r, text=lbl, font=FONTS["label_b"], width=16, anchor="w",
                     bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(side="left")
            w = w_fn(r)
            w.pack(side="left", fill="x", expand=True)
            return w

        fields["username"]  = row("Username",   lambda p: make_entry(p))
        fields["password"]  = row("Password",   lambda p: make_entry(p, show="•"))
        fields["name"]      = row("Full Name",  lambda p: make_entry(p))
        fields["specialty"] = row("Specialty",  lambda p: make_combobox(p, SPECIALTIES))
        fields["phone"]     = row("Phone",      lambda p: make_entry(p))
        fields["schedule"]  = row("Schedule",   lambda p: make_combobox(p, SCHEDULE_DAYS))
        fields["city"]      = row("City",       lambda p: make_combobox(p, CITIES))

        err_var = tk.StringVar()
        err_lbl = tk.Label(card, textvariable=err_var, font=FONTS["small"],
                           bg=COLORS["red_light"], fg=COLORS["red_dark"], padx=8, pady=4)

        def submit():
            from models.doctor import Doctor
            vals = {k: w.get().strip() for k, w in fields.items()}
            err = User.validate_registration(vals["username"], vals["password"], vals["password"])
            if err:
                err_var.set(err); err_lbl.pack(fill="x", pady=4); return
            if self.db.username_exists(vals["username"]):
                err_var.set("Username taken."); err_lbl.pack(fill="x", pady=4); return
            err2 = Doctor.validate(vals["name"], vals["specialty"], vals["phone"], vals["schedule"], vals["city"])
            if err2:
                err_var.set(err2); err_lbl.pack(fill="x", pady=4); return
            uid = self.db.create_user(vals["username"], User.hash_password(vals["password"]), "doctor")
            self.db.create_doctor(uid, vals["name"], vals["specialty"],
                                  vals["phone"], vals["schedule"], vals["city"])
            win.destroy()
            self._refresh_table()

        make_separator(card, bg=COLORS["border"]).pack(fill="x", pady=10)
        btn_row = tk.Frame(card, bg=COLORS["surface"])
        btn_row.pack(fill="x")
        make_button(btn_row, "Cancel", win.destroy, style="secondary").pack(side="left")
        make_button(btn_row, "Add Doctor", submit, style="primary").pack(side="right")


# ================================================================== #
#  APPOINTMENTS VIEW (Admin)                                          #
# ================================================================== #

class AppointmentsView(tk.Frame):
    def __init__(self, master, db):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self._filter = tk.StringVar(value="All")
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        hrow = tk.Frame(inner, bg=COLORS["bg"])
        hrow.pack(fill="x", pady=(0, 14))
        tk.Label(hrow, text="Appointment Management", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")

        # Filter
        filter_row = tk.Frame(inner, bg=COLORS["bg"])
        filter_row.pack(fill="x", pady=(0, 10))
        tk.Label(filter_row, text="Filter:", font=FONTS["label_b"],
                 bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(side="left", padx=(0, 8))
        for status in ["All", "Pending", "Confirmed", "Completed", "Cancelled", "Rescheduled"]:
            rb = tk.Radiobutton(filter_row, text=status, variable=self._filter,
                                value=status, command=self._refresh,
                                font=FONTS["small"], bg=COLORS["bg"],
                                fg=COLORS["text"], activebackground=COLORS["bg"],
                                selectcolor=COLORS["teal_light"])
            rb.pack(side="left", padx=4)

        self._alert_var = tk.StringVar()
        tk.Label(inner, textvariable=self._alert_var, font=FONTS["small"],
                 bg=COLORS["green_light"], fg=COLORS["green_dark"],
                 padx=10, pady=5, anchor="w").pack(fill="x")

        self._table_frame = tk.Frame(inner, bg=COLORS["surface"],
                                      highlightbackground=COLORS["border"], highlightthickness=1)
        self._table_frame.pack(fill="both", expand=True)

        # Action buttons
        self._btn_row = tk.Frame(inner, bg=COLORS["bg"])
        self._btn_row.pack(fill="x", pady=10)

        self._selected_id = None
        self._refresh()

    def _refresh(self):
        for w in self._table_frame.winfo_children():
            w.destroy()
        for w in self._btn_row.winfo_children():
            w.destroy()
        self._selected_id = None

        all_appts = self.db.get_all_appointments()
        f = self._filter.get()
        appts = all_appts if f == "All" else [a for a in all_appts if a["status"] == f]

        cols = ["ID", "Patient", "Doctor", "Specialty", "Date", "Time", "Status"]
        rows = [(a["appointment_id"], a["patient_name"], a["doctor_name"],
                 a["specialty"], a["date"], a["time"], a["status"]) for a in appts]
        tbl, tree = make_table(self._table_frame, cols, rows,
                                [40, 160, 160, 120, 100, 70, 110])
        tbl.pack(fill="both", expand=True)

        def on_select(t):
            sel = t.selection()
            if not sel: return
            vals = t.item(sel[0], "values")
            self._selected_id = int(vals[0])
            self._selected_status = vals[6]
            self._update_buttons()

        tree.bind("<<TreeviewSelect>>", lambda e: on_select(tree))

    def _update_buttons(self):
        for w in self._btn_row.winfo_children():
            w.destroy()
        s = self._selected_status
        if s == "Pending":
            make_button(self._btn_row, "✓ Confirm", lambda: self._change("Confirmed"), style="success").pack(side="left", padx=4)
        if s in ("Pending", "Confirmed", "Rescheduled"):
            make_button(self._btn_row, "✗ Cancel", lambda: self._change("Cancelled"), style="danger").pack(side="left", padx=4)
        if s in ("Confirmed", "Rescheduled"):
            make_button(self._btn_row, "↺ Reschedule", self._reschedule, style="info").pack(side="left", padx=4)

    def _change(self, new_status: str):
        if not self._selected_id: return
        self.db.update_appointment_status(self._selected_id, new_status)
        self._alert_var.set(f"Appointment #{self._selected_id} → {new_status}")
        self._refresh()

    def _reschedule(self):
        if not self._selected_id: return
        win = tk.Toplevel(self)
        win.title("Reschedule Appointment")
        win.geometry("380x240")
        win.configure(bg=COLORS["bg"])
        win.grab_set()

        card = tk.Frame(win, bg=COLORS["surface"], padx=24, pady=20)
        card.pack(fill="both", expand=True, padx=16, pady=16)
        tk.Label(card, text="Reschedule Appointment", font=FONTS["subhead"],
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 12))

        def row(lbl, w_fn):
            r = tk.Frame(card, bg=COLORS["surface"])
            r.pack(fill="x", pady=5)
            tk.Label(r, text=lbl, font=FONTS["label_b"], width=12, anchor="w",
                     bg=COLORS["surface"], fg=COLORS["text_muted"]).pack(side="left")
            w = w_fn(r); w.pack(side="left", fill="x", expand=True)
            return w

        date_e = row("New Date", lambda p: make_entry(p, width=14))
        date_e.insert(0, str(today_date.today()))
        from models.doctor import ALL_SLOTS
        time_cb = row("New Time", lambda p: make_combobox(p, ALL_SLOTS, 12))

        err_var = tk.StringVar()
        err_lbl = tk.Label(card, textvariable=err_var, font=FONTS["small"],
                           bg=COLORS["red_light"], fg=COLORS["red_dark"], padx=6, pady=3)

        def submit():
            nd = date_e.get().strip()
            nt = time_cb.get().strip()
            if not nd or not nt:
                err_var.set("Both fields required."); err_lbl.pack(); return
            appt = self.db.get_all_appointments()
            appt = next((a for a in appt if a["appointment_id"] == self._selected_id), None)
            if appt and self.db.is_slot_taken(appt["doctor_id"], nd, nt, self._selected_id):
                err_var.set("That slot is already booked."); err_lbl.pack(); return
            self.db.reschedule_appointment(self._selected_id, nd, nt)
            win.destroy()
            self._alert_var.set(f"Appointment #{self._selected_id} rescheduled to {nd} at {nt}.")
            self._refresh()

        make_separator(card, bg=COLORS["border"]).pack(fill="x", pady=8)
        btn_row = tk.Frame(card, bg=COLORS["surface"])
        btn_row.pack(fill="x")
        make_button(btn_row, "Cancel", win.destroy, style="secondary").pack(side="left")
        make_button(btn_row, "Save", submit, style="primary").pack(side="right")
