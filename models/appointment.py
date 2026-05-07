"""
models/appointment.py — Appointment Model
Booking logic, double-booking prevention (FR5), and state-machine transitions.

State Machine:
  Pending --> Confirmed   : when admin confirms
  Confirmed --> Completed : when doctor adds diagnosis
  Confirmed --> Cancelled : patient or admin cancels
  Pending   --> Cancelled : patient or admin cancels
  Confirmed --> Rescheduled --> Confirmed : admin reschedules
"""

from datetime import date as DateObj, datetime


VALID_STATUSES = ("Pending", "Confirmed", "Completed", "Cancelled", "Rescheduled")

# Allowed status transitions (state-machine enforcement)
TRANSITIONS = {
    "Pending":     ("Confirmed", "Cancelled"),
    "Confirmed":   ("Completed", "Cancelled", "Rescheduled"),
    "Rescheduled": ("Confirmed", "Cancelled"),
    "Completed":   (),
    "Cancelled":   (),
}


class Appointment:
    """Represents a single clinic appointment."""

    def __init__(self, appointment_id, patient_id, doctor_id,
                 date, time, status="Pending",
                 patient_name="", doctor_name="", specialty="",
                 patient_age=None, patient_gender=""):
        self.appointment_id = appointment_id
        self.patient_id     = patient_id
        self.doctor_id      = doctor_id
        self.date           = date        # str "YYYY-MM-DD"
        self.time           = time        # str "HH:MM"
        self.status         = status
        # denormalised display fields (filled by JOIN queries)
        self.patient_name   = patient_name
        self.doctor_name    = doctor_name
        self.specialty      = specialty
        self.patient_age    = patient_age
        self.patient_gender = patient_gender

    # ------------------------------------------------------------------ #
    #  VALIDATION                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_booking(doctor_id, date_str: str, time_str: str) -> str | None:
        """
        Validate a booking request (date in future, doctor selected, slot chosen).
        Returns error string or None.
        """
        if not doctor_id:
            return "Please select a doctor."
        if not date_str:
            return "Please select a date."
        if not time_str:
            return "Please select a time slot."
        try:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if appt_date < DateObj.today():
                return "Appointment date must be today or in the future."
        except ValueError:
            return "Invalid date format."
        return None

    # ------------------------------------------------------------------ #
    #  STATE MACHINE                                                      #
    # ------------------------------------------------------------------ #

    def can_transition_to(self, new_status: str) -> bool:
        """Check if this appointment can move to new_status."""
        return new_status in TRANSITIONS.get(self.status, ())

    def is_active(self) -> bool:
        return self.status in ("Pending", "Confirmed", "Rescheduled")

    def is_cancellable(self) -> bool:
        return self.status in ("Pending", "Confirmed", "Rescheduled")

    def status_color(self) -> str:
        """Return a color hex string matching current status."""
        return {
            "Pending":     "#BA7517",
            "Confirmed":   "#1D9E75",
            "Completed":   "#639922",
            "Cancelled":   "#E24B4A",
            "Rescheduled": "#378ADD",
        }.get(self.status, "#888780")

    def status_bg(self) -> str:
        return {
            "Pending":     "#FAEEDA",
            "Confirmed":   "#E1F5EE",
            "Completed":   "#EAF3DE",
            "Cancelled":   "#FCEBEB",
            "Rescheduled": "#E6F1FB",
        }.get(self.status, "#F1EFE8")

    @classmethod
    def from_dict(cls, d: dict) -> "Appointment":
        return cls(
            appointment_id = d["appointment_id"],
            patient_id     = d["patient_id"],
            doctor_id      = d["doctor_id"],
            date           = d["date"],
            time           = d["time"],
            status         = d["status"],
            patient_name   = d.get("patient_name", ""),
            doctor_name    = d.get("doctor_name", ""),
            specialty      = d.get("specialty", ""),
            patient_age    = d.get("age"),
            patient_gender = d.get("gender", ""),
        )

    def __repr__(self):
        return (f"<Appointment id={self.appointment_id} "
                f"{self.date}@{self.time} status={self.status}>")
