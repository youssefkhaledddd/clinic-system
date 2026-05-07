"""
models/patient.py — Patient Model
Handles patient registration, validation, and medical-history retrieval.
"""

CITIES = [
    "Alexandria",
    "Cairo",
    "Giza",
    "Luxor",
    "Aswan",
    "Mansoura",
    "Tanta",
    "Ismailia",
    "Suez",
    "Port Said",
]


class Patient:
    """Represents a registered patient."""

    def __init__(self, patient_id, user_id, name, age, gender, phone, address, city):
        self.patient_id = patient_id
        self.user_id    = user_id
        self.name       = name
        self.age        = age
        self.gender     = gender
        self.phone      = phone
        self.address    = address
        self.city       = city

    @staticmethod
    def validate(name: str, age: str, gender: str, phone: str, address: str, city: str) -> str | None:
        """
        Validate patient registration fields.
        Returns an error message string, or None if all fields are valid.
        """
        if not all([name, age, gender, phone, address, city]):
            return "All fields are required."
        if len(name.strip()) < 3:
            return "Full name must be at least 3 characters."
        try:
            age_int = int(age)
            if not (0 < age_int < 150):
                return "Please enter a valid age (1–149)."
        except ValueError:
            return "Age must be a number."
        if not phone.strip().isdigit() or len(phone.strip()) < 10:
            return "Phone must be at least 10 digits."
        if gender not in ("Male", "Female"):
            return "Please select a gender."
        if city not in CITIES:
            return "Please select a valid city."
        return None

    def get_initials(self) -> str:
        parts = self.name.split()
        return "".join(p[0].upper() for p in parts[:2]) if parts else "P"

    def __repr__(self):
        return f"<Patient id={self.patient_id} name={self.name!r} city={self.city!r}>"
