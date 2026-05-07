"""
views/patient_screen.py — Patient Dashboard Views
  PatientDashboard  — profile card + upcoming appointments
  BookAppointment   — city filter → doctor list → date → slot → confirm
  MyAppointments    — table of all appointments with cancel option
  MyHistory         — medical records timeline
"""

import tkinter as tk
from tkinter import ttk
from datetime import date as today_date
from views.theme import (
    COLORS, FONTS, STATUS_COLORS,
    make_button, make_entry, make_combobox, make_scrollable,
    make_separator, show_error, show_confirm
)
from views.admin_screen import make_table, stat_card
from models.doctor import ALL_SLOTS
from models.patient import CITIES


class PatientDashboard(tk.Frame):
    def __init__(self, master, db, user, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self.profile = profile
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        p = self.profile
        name    = p.get("name", "Patient")
        age     = p.get("age", "")
        gender  = p.get("gender", "")
        phone   = p.get("phone", "")
        city    = p.get("city", "")
        pid     = p.get("patient_id")

        # Profile header
        pcard = tk.Frame(inner, bg=COLORS["blue"],
                         highlightbackground=COLORS["blue_dark"], highlightthickness=1)
        pcard.pack(fill="x", pady=(0, 16))
        ph = tk.Frame(pcard, bg=COLORS["blue"], padx=20, pady=18)
        ph.pack(fill="x")

        initials = "".join(n[0].upper() for n in name.split()[:2])
        av = tk.Label(ph, text=initials, font=("Georgia", 20, "bold"),
                      bg=COLORS["blue_dark"], fg=COLORS["white"],
                      width=4, height=2, relief="flat")
        av.pack(side="left", padx=(0, 16))

        info = tk.Frame(ph, bg=COLORS["blue"])
        info.pack(side="left")
        tk.Label(info, text=name, font=FONTS["heading"],
                 bg=COLORS["blue"], fg=COLORS["white"]).pack(anchor="w")
        tk.Label(info, text=f"🎂 Age: {age}   |   {gender}   |   📞 {phone}   |   📍 {city}",
                 font=FONTS["body"], bg=COLORS["blue"], fg="#B5D4F4").pack(anchor="w")

        if pid:
            appts   = self.db.get_appointments_for_patient(pid)
            history = self.db.get_history_for_patient(pid)
            upcoming = [a for a in appts if a["status"] in ("Confirmed", "Pending")]
            completed = [a for a in appts if a["status"] == "Completed"]

            # Stats
            srow = tk.Frame(inner, bg=COLORS["bg"])
            srow.pack(fill="x", pady=(0, 16))
            stat_card(srow, "Upcoming",  len(upcoming),  COLORS["blue"])
            stat_card(srow, "Completed", len(completed), COLORS["green"])
            stat_card(srow, "Records",   len(history),   COLORS["purple"])

            # Upcoming appointments
            section = tk.Frame(inner, bg=COLORS["surface"],
                               highlightbackground=COLORS["border"], highlightthickness=1)
            section.pack(fill="x")
            hdr = tk.Frame(section, bg=COLORS["blue_light"], padx=14, pady=10)
            hdr.pack(fill="x")
            tk.Label(hdr, text="Upcoming Appointments",
                     font=FONTS["subhead"], bg=COLORS["blue_light"],
                     fg=COLORS["blue_dark"]).pack(anchor="w")

            body = tk.Frame(section, bg=COLORS["surface"], padx=14, pady=10)
            body.pack(fill="x")
            if not upcoming:
                tk.Label(body, text="No upcoming appointments. Click 'Book Appointment' to schedule one.",
                         font=FONTS["body"], bg=COLORS["surface"],
                         fg=COLORS["text_muted"]).pack()
            else:
                cols = ["Doctor", "Specialty", "Date", "Time", "Status"]
                rows = [(a["doctor_name"], a.get("specialty", ""),
                         a["date"], a["time"], a["status"]) for a in upcoming]
                tbl, _ = make_table(body, cols, rows, [180, 130, 100, 70, 110])
                tbl.pack(fill="x")


# ================================================================== #
#  BOOK APPOINTMENT (with city → doctor filter)                       #
# ================================================================== #

class BookAppointment(tk.Frame):
    def __init__(self, master, db, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db       = db
        self.profile  = profile
        self._doctors = []          # currently shown doctor list
        self._selected_doctor = None
        self._selected_slot   = None
        self._slot_btns       = {}
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        tk.Label(inner, text="Book an Appointment", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(inner, text="Filter by city and specialty to find your doctor, then pick a slot.",
                 font=FONTS["body"], bg=COLORS["bg"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 16))

        self._alert_var = tk.StringVar()
        self._alert_lbl = tk.Label(inner, textvariable=self._alert_var, font=FONTS["small"],
                                    bg=COLORS["green_light"], fg=COLORS["green_dark"],
                                    padx=10, pady=5, anchor="w")
        self._alert_lbl.pack(fill="x")

        # ── Step 1: Filter ───────────────────────────────────────────
        step1 = self._section(inner, "Step 1 — Find a Doctor", COLORS["teal_light"], COLORS["teal_dark"])

        filter_row = tk.Frame(step1, bg=COLORS["surface"])
        filter_row.pack(fill="x", pady=8)

        # City filter — default to patient's city
        patient_city = self.profile.get("city", "")
        cities = ["All Cities"] + CITIES
        tk.Label(filter_row, text="City:", font=FONTS["label_b"],
                 bg=COLORS["surface"], fg=COLORS["text_muted"], width=10, anchor="w").pack(side="left")
        self._city_cb = make_combobox(filter_row, cities, width=18)
        if patient_city in cities:
            self._city_cb.set(patient_city)
        else:
            self._city_cb.set("All Cities")
        self._city_cb.pack(side="left", padx=(0, 16))

        # Specialty filter
        specs = ["All Specialties"] + self.db.get_distinct_specialties()
        tk.Label(filter_row, text="Specialty:", font=FONTS["label_b"],
                 bg=COLORS["surface"], fg=COLORS["text_muted"], width=12, anchor="w").pack(side="left")
        self._spec_cb = make_combobox(filter_row, specs, width=20)
        self._spec_cb.set("All Specialties")
        self._spec_cb.pack(side="left", padx=(0, 16))

        make_button(filter_row, "Search Doctors", self._search_doctors, style="primary").pack(side="left")

        # Doctor results list
        self._doctor_list_frame = tk.Frame(step1, bg=COLORS["surface"])
        self._doctor_list_frame.pack(fill="x", pady=8)

        # ── Step 2: Date & Slot ──────────────────────────────────────
        self._step2_frame = tk.Frame(inner, bg=COLORS["bg"])

        # ── Step 3: Confirm ─────────────────────────────────────────
        self._step3_frame = tk.Frame(inner, bg=COLORS["bg"])

        # Auto-search with patient's city on load
        self._search_doctors()

    def _section(self, parent, title, bg_h, fg_h):
        sec = tk.Frame(parent, bg=COLORS["surface"],
                       highlightbackground=COLORS["border"], highlightthickness=1)
        sec.pack(fill="x", pady=(0, 12))
        hdr = tk.Frame(sec, bg=bg_h, padx=14, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=FONTS["subhead"], bg=bg_h, fg=fg_h).pack(anchor="w")
        body = tk.Frame(sec, bg=COLORS["surface"], padx=14, pady=10)
        body.pack(fill="x")
        return body

    def _search_doctors(self):
        for w in self._doctor_list_frame.winfo_children():
            w.destroy()
        for w in self._step2_frame.winfo_children():
            w.destroy()
        for w in self._step3_frame.winfo_children():
            w.destroy()
        self._step2_frame.pack_forget()
        self._step3_frame.pack_forget()
        self._selected_doctor = None
        self._selected_slot   = None

        city = self._city_cb.get()
        spec = self._spec_cb.get()

        all_docs = self.db.get_all_doctors()
        if city != "All Cities":
            all_docs = [d for d in all_docs if d.get("city", "").lower() == city.lower()]
        if spec != "All Specialties":
            all_docs = [d for d in all_docs if d.get("specialty", "").lower() == spec.lower()]
        self._doctors = all_docs

        if not all_docs:
            tk.Label(self._doctor_list_frame,
                     text="No doctors found for this filter. Try 'All Cities' or 'All Specialties'.",
                     font=FONTS["body"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).pack(anchor="w")
            return

        tk.Label(self._doctor_list_frame, text=f"{len(all_docs)} doctor(s) found — click to select:",
                 font=FONTS["small_b"], bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

        for doc in all_docs:
            dcard = tk.Frame(self._doctor_list_frame, bg=COLORS["bg"],
                             highlightbackground=COLORS["border"], highlightthickness=1,
                             padx=12, pady=8, cursor="hand2")
            dcard.pack(fill="x", pady=3)
            row = tk.Frame(dcard, bg=COLORS["bg"])
            row.pack(fill="x")
            badge = tk.Label(row, text=doc["specialty"], font=FONTS["small_b"],
                             bg=COLORS["teal_light"], fg=COLORS["teal_dark"], padx=8, pady=2)
            badge.pack(side="left", padx=(0, 10))
            tk.Label(row, text=doc["name"], font=FONTS["body_b"],
                     bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
            tk.Label(row, text=f"📍 {doc['city']}  🕐 {doc['schedule']}",
                     font=FONTS["small"], bg=COLORS["bg"],
                     fg=COLORS["text_muted"]).pack(side="left", padx=10)
            select_btn = make_button(row, "Select →",
                                     lambda d=doc, c=dcard: self._select_doctor(d, c),
                                     style="ghost")
            select_btn.pack(side="right")
            for w in [dcard, row, badge]:
                w.bind("<Button-1>", lambda e, d=doc, c=dcard: self._select_doctor(d, c))

    def _select_doctor(self, doc: dict, card_widget=None):
        self._selected_doctor = doc
        self._selected_slot   = None

        # Reset all doctor cards visually
        for w in self._doctor_list_frame.winfo_children():
            if isinstance(w, tk.Frame):
                w.config(highlightbackground=COLORS["border"],
                         highlightthickness=1, bg=COLORS["bg"])
        if card_widget:
            card_widget.config(highlightbackground=COLORS["teal"],
                               highlightthickness=2, bg=COLORS["teal_light"])

        # Build Step 2
        for w in self._step2_frame.winfo_children():
            w.destroy()
        for w in self._step3_frame.winfo_children():
            w.destroy()

        self._step2_frame.pack(fill="x", pady=(0, 12))
        self._step3_frame.pack_forget()

        s2 = self._section(self._step2_frame,
                           f"Step 2 — Pick a Date for {doc['name']}",
                           COLORS["blue_light"], COLORS["blue_dark"])

        date_row = tk.Frame(s2, bg=COLORS["surface"])
        date_row.pack(fill="x", pady=6)
        tk.Label(date_row, text="Date:", font=FONTS["label_b"],
                 bg=COLORS["surface"], fg=COLORS["text_muted"], width=8, anchor="w").pack(side="left")
        self._date_e = make_entry(date_row, width=14)
        self._date_e.insert(0, str(today_date.today()))
        self._date_e.pack(side="left", padx=(0, 12))
        make_button(date_row, "Check Slots →", self._check_slots, style="info").pack(side="left")

        self._slots_frame = tk.Frame(s2, bg=COLORS["surface"])
        self._slots_frame.pack(fill="x", pady=8)

    def _check_slots(self):
        if not self._selected_doctor:
            return
        date_str = self._date_e.get().strip()
        if not date_str:
            self._alert_var.set("⚠ Please enter a date.")
            self._alert_lbl.config(bg=COLORS["red_light"], fg=COLORS["red_dark"])
            return

        booked = self.db.get_booked_times(self._selected_doctor["doctor_id"], date_str)
        available = [s for s in ALL_SLOTS if s not in booked]

        for w in self._slots_frame.winfo_children():
            w.destroy()
        self._slot_btns.clear()
        self._selected_slot = None

        tk.Label(self._slots_frame,
                 text=f"Available slots on {date_str}   ({len(available)} free / {len(ALL_SLOTS)} total):",
                 font=FONTS["small_b"], bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(0, 6))

        btn_grid = tk.Frame(self._slots_frame, bg=COLORS["surface"])
        btn_grid.pack(anchor="w")

        for slot in ALL_SLOTS:
            is_free = slot not in booked
            btn = tk.Button(
                btn_grid, text=slot,
                font=FONTS["small_b"],
                bg=COLORS["teal_light"] if is_free else COLORS["gray_light"],
                fg=COLORS["teal_dark"] if is_free else COLORS["gray"],
                relief="flat", bd=0, padx=10, pady=6,
                cursor="hand2" if is_free else "arrow",
                state="normal" if is_free else "disabled",
                highlightbackground=COLORS["teal"] if is_free else COLORS["border"],
                highlightthickness=1,
            )
            if is_free:
                btn.config(command=lambda s=slot, b=btn: self._select_slot(s, b))
            btn.pack(side="left", padx=3, pady=2)
            self._slot_btns[slot] = btn

    def _select_slot(self, slot: str, btn_widget):
        self._selected_slot = slot
        for s, b in self._slot_btns.items():
            if s == slot:
                b.config(bg=COLORS["teal"], fg=COLORS["white"])
            elif s not in self.db.get_booked_times(self._selected_doctor["doctor_id"],
                                                    self._date_e.get().strip()):
                b.config(bg=COLORS["teal_light"], fg=COLORS["teal_dark"])

        # Show step 3
        for w in self._step3_frame.winfo_children():
            w.destroy()
        self._step3_frame.pack(fill="x")

        s3 = self._section(self._step3_frame, "Step 3 — Confirm Booking",
                           COLORS["green_light"], COLORS["green_dark"])
        doc  = self._selected_doctor
        date = self._date_e.get().strip()
        tk.Label(s3, text=f"Doctor:  {doc['name']}  ({doc['specialty']})",
                 font=FONTS["body_b"], bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(s3, text=f"Date:    {date}   at   {slot}",
                 font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=2)
        tk.Label(s3, text="Status will be: Pending  (Admin will confirm)",
                 font=FONTS["small"], bg=COLORS["surface"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 10))
        make_button(s3, "✓ Confirm Booking", self._confirm_booking, style="success").pack(anchor="w")

    def _confirm_booking(self):
        from models.appointment import Appointment
        pid  = self.profile.get("patient_id")
        doc  = self._selected_doctor
        date = self._date_e.get().strip()
        slot = self._selected_slot

        if not pid or not doc or not date or not slot:
            self._alert_var.set("⚠ Please complete all steps.")
            self._alert_lbl.config(bg=COLORS["red_light"], fg=COLORS["red_dark"])
            return

        err = Appointment.validate_booking(doc["doctor_id"], date, slot)
        if err:
            self._alert_var.set("⚠ " + err)
            self._alert_lbl.config(bg=COLORS["red_light"], fg=COLORS["red_dark"])
            return

        if self.db.is_slot_taken(doc["doctor_id"], date, slot):
            self._alert_var.set("⚠ That slot was just taken. Please choose another.")
            self._alert_lbl.config(bg=COLORS["red_light"], fg=COLORS["red_dark"])
            return

        self.db.create_appointment(pid, doc["doctor_id"], date, slot)
        self._alert_var.set(f"✓ Appointment booked with {doc['name']} on {date} at {slot}. Status: Pending.")
        self._alert_lbl.config(bg=COLORS["green_light"], fg=COLORS["green_dark"])

        # Reset
        self._selected_slot   = None
        self._selected_doctor = None
        for w in self._step2_frame.winfo_children():
            w.destroy()
        for w in self._step3_frame.winfo_children():
            w.destroy()
        self._step2_frame.pack_forget()
        self._step3_frame.pack_forget()


# ================================================================== #
#  MY APPOINTMENTS                                                    #
# ================================================================== #

class MyAppointments(tk.Frame):
    def __init__(self, master, db, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self.profile = profile
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        tk.Label(inner, text="My Appointments", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 14))

        self._alert_var = tk.StringVar()
        tk.Label(inner, textvariable=self._alert_var, font=FONTS["small"],
                 bg=COLORS["amber_light"], fg=COLORS["amber_dark"],
                 padx=10, pady=5, anchor="w").pack(fill="x", pady=(0, 10))

        self._table_frame = tk.Frame(inner, bg=COLORS["surface"],
                                      highlightbackground=COLORS["border"], highlightthickness=1)
        self._table_frame.pack(fill="both", expand=True)

        tk.Label(inner, text="Select a Pending or Confirmed appointment in the table to cancel it.",
                 font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_muted"]).pack(anchor="w", pady=6)

        self._cancel_btn = make_button(inner, "✗ Cancel Selected Appointment",
                                       self._cancel_selected, style="danger")
        self._cancel_btn.pack(anchor="w")
        self._cancel_btn.config(state="disabled")

        self._selected_id     = None
        self._selected_status = None
        self._refresh()

    def _refresh(self):
        for w in self._table_frame.winfo_children():
            w.destroy()
        pid   = self.profile.get("patient_id")
        appts = self.db.get_appointments_for_patient(pid) if pid else []

        cols = ["ID", "Doctor", "Specialty", "Date", "Time", "Status"]
        rows = [(a["appointment_id"], a["doctor_name"], a.get("specialty", ""),
                 a["date"], a["time"], a["status"]) for a in appts]
        tbl, tree = make_table(self._table_frame, cols, rows,
                                [40, 180, 130, 100, 70, 110])
        tbl.pack(fill="both", expand=True)

        def on_select(t):
            sel = t.selection()
            if not sel: return
            vals = t.item(sel[0], "values")
            self._selected_id     = int(vals[0])
            self._selected_status = vals[5]
            if self._selected_status in ("Pending", "Confirmed"):
                self._cancel_btn.config(state="normal")
            else:
                self._cancel_btn.config(state="disabled")

        tree.bind("<<TreeviewSelect>>", lambda e: on_select(tree))

    def _cancel_selected(self):
        if not self._selected_id:
            return
        if show_confirm(self, "Cancel this appointment?"):
            self.db.update_appointment_status(self._selected_id, "Cancelled")
            self._alert_var.set(f"Appointment #{self._selected_id} cancelled.")
            self._cancel_btn.config(state="disabled")
            self._refresh()


# ================================================================== #
#  MY MEDICAL HISTORY                                                 #
# ================================================================== #

class MyHistory(tk.Frame):
    def __init__(self, master, db, profile):
        super().__init__(master, bg=COLORS["bg"])
        self.db = db
        self.profile = profile
        self._build()

    def _build(self):
        outer, _, inner = make_scrollable(self)
        outer.pack(fill="both", expand=True)
        inner.config(padx=20, pady=20)

        tk.Label(inner, text="My Medical History", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(inner, text="Complete record of all visits, diagnoses, and treatment notes.",
                 font=FONTS["body"], bg=COLORS["bg"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 16))

        pid     = self.profile.get("patient_id")
        records = self.db.get_history_for_patient(pid) if pid else []

        if not records:
            tk.Label(inner, text="No medical records found.",
                     font=FONTS["body"], bg=COLORS["bg"],
                     fg=COLORS["text_muted"]).pack(anchor="w")
            return

        for rec in records:
            card = tk.Frame(inner, bg=COLORS["surface"],
                            highlightbackground=COLORS["teal"], highlightthickness=2)
            card.pack(fill="x", pady=6)

            # Left accent strip
            accent = tk.Frame(card, bg=COLORS["teal"], width=5)
            accent.pack(side="left", fill="y")

            body = tk.Frame(card, bg=COLORS["surface"], padx=14, pady=12)
            body.pack(side="left", fill="x", expand=True)

            # Date + doctor row
            top_row = tk.Frame(body, bg=COLORS["surface"])
            top_row.pack(fill="x")
            tk.Label(top_row, text=rec["date"], font=FONTS["small_b"],
                     bg=COLORS["teal_light"], fg=COLORS["teal_dark"],
                     padx=8, pady=3).pack(side="left")
            tk.Label(top_row, text=f"  🩺 {rec['doctor_name']}",
                     font=FONTS["body_b"], bg=COLORS["surface"],
                     fg=COLORS["text"]).pack(side="left", padx=8)
            tk.Label(top_row,
                     text=rec.get("specialty", ""),
                     font=FONTS["small"], bg=COLORS["surface"],
                     fg=COLORS["text_muted"]).pack(side="left")

            # Diagnosis
            tk.Label(body, text=f"Diagnosis:  {rec['diagnosis']}",
                     font=FONTS["body_b"], bg=COLORS["surface"],
                     fg=COLORS["text"], anchor="w").pack(fill="x", pady=(8, 2))

            # Notes
            if rec.get("notes"):
                tk.Label(body, text=f"Notes:  {rec['notes']}",
                         font=FONTS["body"], bg=COLORS["surface"],
                         fg=COLORS["text_muted"], wraplength=700,
                         justify="left", anchor="w").pack(fill="x")
