"""
models/medical_record.py — MedicalRecord Model
Represents a single medical history entry (visit record).
"""


class MedicalRecord:
    """Represents one patient visit / diagnosis record."""

    def __init__(self, record_id, patient_id, doctor_id,
                 date, diagnosis, notes="",
                 doctor_name="", specialty=""):
        self.record_id   = record_id
        self.patient_id  = patient_id
        self.doctor_id   = doctor_id
        self.date        = date
        self.diagnosis   = diagnosis
        self.notes       = notes
        self.doctor_name = doctor_name
        self.specialty   = specialty

    @staticmethod
    def validate(diagnosis: str) -> str | None:
        """Validate medical record input. Returns error or None."""
        if not diagnosis or not diagnosis.strip():
            return "Diagnosis field is required."
        if len(diagnosis.strip()) < 4:
            return "Please enter a more descriptive diagnosis."
        return None

    @classmethod
    def from_dict(cls, d: dict) -> "MedicalRecord":
        return cls(
            record_id   = d["record_id"],
            patient_id  = d["patient_id"],
            doctor_id   = d["doctor_id"],
            date        = d["date"],
            diagnosis   = d["diagnosis"],
            notes       = d.get("notes", ""),
            doctor_name = d.get("doctor_name", ""),
            specialty   = d.get("specialty", ""),
        )

    def __repr__(self):
        return (f"<MedicalRecord id={self.record_id} "
                f"patient={self.patient_id} date={self.date}>")
