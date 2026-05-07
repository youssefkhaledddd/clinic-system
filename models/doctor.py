"""
models/doctor.py — Doctor Model
Handles doctor registration, validation, and schedule management.
"""

SPECIALTIES = [
    "Cardiology",
    "Pediatrics",
    "Orthopedics",
    "Dermatology",
    "Neurology",
    "Oncology",
    "Ophthalmology",
    "Psychiatry",
    "General Practice",
    "ENT",
    "Gynecology",
    "Urology",
    "Radiology",
    "Anesthesiology",
]

SCHEDULE_DAYS = [
    "Sun-Thu 08:00-14:00",
    "Sun-Thu 09:00-17:00",
    "Sun-Thu 14:00-20:00",
    "Mon-Wed 09:00-13:00",
    "Mon-Wed 10:00-15:00",
    "Sat-Thu 08:00-14:00",
    "Daily 08:00-20:00",
]

# Available time slots for booking
ALL_SLOTS = [
    "08:00", "09:00", "10:00", "11:00",
    "12:00", "13:00", "14:00", "15:00",
    "16:00", "17:00", "18:00", "19:00",
]


class Doctor:
    """Represents a registered doctor."""

    def __init__(self, doctor_id, user_id, name, specialty, phone, schedule, city):
        self.doctor_id = doctor_id
        self.user_id   = user_id
        self.name      = name
        self.specialty = specialty
        self.phone     = phone
        self.schedule  = schedule
        self.city      = city

    @staticmethod
    def validate(name: str, specialty: str, phone: str, schedule: str, city: str) -> str | None:
        """
        Validate doctor registration fields.
        Returns an error message string, or None if valid.
        """
        if not all([name, specialty, phone, schedule, city]):
            return "All fields are required."
        if len(name.strip()) < 5:
            return "Doctor name must be at least 5 characters."
        if not phone.strip().isdigit() or len(phone.strip()) < 10:
            return "Phone must be at least 10 digits."
        return None

    def get_initials(self) -> str:
        parts = self.name.replace("Dr.", "").strip().split()
        return "".join(p[0].upper() for p in parts[:2]) if parts else "DR"

    def get_available_slots(self, booked_times: list) -> list:
        """Return list of time slots not yet booked for this doctor."""
        return [s for s in ALL_SLOTS if s not in booked_times]

    def __repr__(self):
        return f"<Doctor id={self.doctor_id} name={self.name!r} specialty={self.specialty!r}>"
