"""
views/doctor_screen.py — Doctor Dashboard Views
  DoctorDashboard    — profile card + today's appointments
  DoctorAppointments — full appointment list with filters
  DiagnoseView       — select confirmed appointment, enter diagnosis
"""

import tkinter as tk
from datetime import date as today_date
from views.theme import (
    COLORS, FONTS, STATUS_COLORS,
    make_button, make_entry, make_scrollable, make_separator, show_error
)
from views.admin_screen import make_table, stat_card


class DoctorDashboard(tk.Frame):
    def __init__(self, master, db, user, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self.profile = profile
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        doc = self.profile
        name     = doc.get("name", "Doctor")
        spec     = doc.get("specialty", "")
        phone    = doc.get("phone", "")
        sched    = doc.get("schedule", "")
        city     = doc.get("city", "")
        did      = doc.get("doctor_id")

        # Profile header card
        pcard = tk.Frame(inner, bg=COLORS["teal"],
                         highlightbackground=COLORS["teal_dark"], highlightthickness=1)
        pcard.pack(fill="x", pady=(0, 16))
        ph = tk.Frame(pcard, bg=COLORS["teal"], padx=20, pady=18)
        ph.pack(fill="x")

        initials = "".join(p[0].upper() for p in name.split()[:2])
        av = tk.Label(ph, text=initials, font=("Georgia", 20, "bold"),
                      bg=COLORS["teal_dark"], fg=COLORS["white"],
                      width=4, height=2, relief="flat")
        av.pack(side="left", padx=(0, 16))

        info = tk.Frame(ph, bg=COLORS["teal"])
        info.pack(side="left")
        tk.Label(info, text=name, font=FONTS["heading"],
                 bg=COLORS["teal"], fg=COLORS["white"]).pack(anchor="w")
        tk.Label(info, text=f"🩺 {spec}   |   📞 {phone}   |   📍 {city}",
                 font=FONTS["body"], bg=COLORS["teal"], fg="#9FE1CB").pack(anchor="w")
        tk.Label(info, text=f"🕐 {sched}",
                 font=FONTS["body"], bg=COLORS["teal"], fg="#9FE1CB").pack(anchor="w")

        if did:
            appts = self.db.get_appointments_for_doctor(did)
            today = str(today_date.today())
            today_appts = [a for a in appts if a["date"] == today and a["status"] != "Cancelled"]
            confirmed   = [a for a in appts if a["status"] == "Confirmed"]
            completed   = [a for a in appts if a["status"] == "Completed"]
            pending     = [a for a in appts if a["status"] == "Pending"]

            # Stats
            srow = tk.Frame(inner, bg=COLORS["bg"])
            srow.pack(fill="x", pady=(0, 16))
            stat_card(srow, "Today",     len(today_appts), COLORS["teal"])
            stat_card(srow, "Confirmed", len(confirmed),   COLORS["blue"])
            stat_card(srow, "Completed", len(completed),   COLORS["green"])
            stat_card(srow, "Pending",   len(pending),     COLORS["amber"])

            # Today's list
            section = tk.Frame(inner, bg=COLORS["surface"],
                               highlightbackground=COLORS["border"], highlightthickness=1)
            section.pack(fill="x")
            hdr = tk.Frame(section, bg=COLORS["teal_light"], padx=14, pady=10)
            hdr.pack(fill="x")
            tk.Label(hdr, text=f"Today's Appointments — {today}",
                     font=FONTS["subhead"], bg=COLORS["teal_light"],
                     fg=COLORS["teal_dark"]).pack(anchor="w")

            body = tk.Frame(section, bg=COLORS["surface"], padx=14, pady=10)
            body.pack(fill="x")
            if not today_appts:
                tk.Label(body, text="No appointments today.",
                         font=FONTS["body"], bg=COLORS["surface"],
                         fg=COLORS["text_muted"]).pack()
            else:
                cols = ["Time", "Patient", "Age", "Gender", "Status"]
                rows = [(a["time"], a["patient_name"], a.get("age", ""),
                         a.get("gender", ""), a["status"]) for a in today_appts]
                tbl, _ = make_table(body, cols, rows, [70, 200, 50, 80, 110])
                tbl.pack(fill="x")


class DoctorAppointments(tk.Frame):
    def __init__(self, master, db, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self.profile = profile
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        tk.Label(inner, text="My Schedule", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 14))

        did = self.profile.get("doctor_id")
        appts = self.db.get_appointments_for_doctor(did) if did else []

        cols = ["ID", "Patient", "Age", "Date", "Time", "Status"]
        rows = [(a["appointment_id"], a["patient_name"], a.get("age", ""),
                 a["date"], a["time"], a["status"]) for a in appts]

        frame = tk.Frame(inner, bg=COLORS["surface"],
                         highlightbackground=COLORS["border"], highlightthickness=1)
        frame.pack(fill="both", expand=True)
        tbl, _ = make_table(frame, cols, rows, [50, 200, 50, 110, 70, 110])
        tbl.pack(fill="both", expand=True)


class DiagnoseView(tk.Frame):
    def __init__(self, master, db, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self.profile = profile
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        tk.Label(inner, text="Add Diagnosis", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(inner, text="Select a confirmed appointment and enter diagnosis details.",
                 font=FONTS["body"], bg=COLORS["bg"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 16))

        self._alert_var = tk.StringVar()
        tk.Label(inner, textvariable=self._alert_var, font=FONTS["small"],
                 bg=COLORS["green_light"], fg=COLORS["green_dark"],
                 padx=10, pady=5, anchor="w").pack(fill="x", pady=(0, 10))

        did = self.profile.get("doctor_id")
        appts = [a for a in self.db.get_appointments_for_doctor(did)
                 if a["status"] == "Confirmed"] if did else []

        if not appts:
            tk.Label(inner, text="No confirmed appointments awaiting diagnosis.",
                     font=FONTS["body"], bg=COLORS["bg"],
                     fg=COLORS["text_muted"]).pack(anchor="w")
            return

        # List confirmed appointments as clickable cards
        for a in appts:
            card = tk.Frame(inner, bg=COLORS["surface"],
                            highlightbackground=COLORS["border"], highlightthickness=1,
                            padx=16, pady=12, cursor="hand2")
            card.pack(fill="x", pady=5)

            row = tk.Frame(card, bg=COLORS["surface"])
            row.pack(fill="x")
            tk.Label(row, text=f"🧑 {a['patient_name']}",
                     font=FONTS["body_b"], bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left")
            tk.Label(row, text=f"  📅 {a['date']}  🕐 {a['time']}",
                     font=FONTS["body"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).pack(side="left", padx=10)
            make_button(row, "+ Add Diagnosis",
                        lambda a=a: self._open_diagnosis(a),
                        style="primary").pack(side="right")

    def _open_diagnosis(self, appt: dict):
        win = tk.Toplevel(self)
        win.title(f"Diagnosis — {appt['patient_name']}")
        win.geometry("500x400")
        win.configure(bg=COLORS["bg"])
        win.grab_set()

        card = tk.Frame(win, bg=COLORS["surface"], padx=24, pady=20)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(card, text=f"Patient: {appt['patient_name']}",
                 font=FONTS["subhead"], bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(card, text=f"Date: {appt['date']}   Time: {appt['time']}",
                 font=FONTS["body"], bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 16))

        def row(lbl, w_fn):
            r = tk.Frame(card, bg=COLORS["surface"])
            r.pack(fill="x", pady=6)
            tk.Label(r, text=lbl, font=FONTS["label_b"],
                     bg=COLORS["surface"], fg=COLORS["text_muted"],
                     anchor="w").pack(fill="x")
            w = w_fn(r); w.pack(fill="x")
            return w

        diag_e = row("Diagnosis *", lambda p: make_entry(p, width=50))
        notes_e = row("Treatment Notes", lambda p: tk.Text(p, font=FONTS["body"],
                                                            width=50, height=5,
                                                            bg=COLORS["white"],
                                                            fg=COLORS["text"],
                                                            relief="flat",
                                                            highlightbackground=COLORS["border"],
                                                            highlightthickness=1))

        err_var = tk.StringVar()
        err_lbl = tk.Label(card, textvariable=err_var, font=FONTS["small"],
                           bg=COLORS["red_light"], fg=COLORS["red_dark"], padx=6, pady=3)

        def submit():
            from models.medical_record import MedicalRecord
            diag  = diag_e.get().strip()
            notes = notes_e.get("1.0", "end").strip()
            err = MedicalRecord.validate(diag)
            if err:
                err_var.set(err); err_lbl.pack(fill="x", pady=4); return
            self.db.add_medical_record(appt["patient_id"], appt["doctor_id"],
                                       appt["date"], diag, notes)
            self.db.update_appointment_status(appt["appointment_id"], "Completed")
            win.destroy()
            self._alert_var.set(f"Diagnosis saved for {appt['patient_name']}!")
            self._build_refresh()

        make_separator(card, bg=COLORS["border"]).pack(fill="x", pady=10)
        btn_row = tk.Frame(card, bg=COLORS["surface"])
        btn_row.pack(fill="x")
        make_button(btn_row, "Cancel", win.destroy, style="secondary").pack(side="left")
        make_button(btn_row, "Save Diagnosis", submit, style="success").pack(side="right")

    def _build_refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
