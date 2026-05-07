# Smart Clinic Management System
**Alexandria National University — Faculty of Computer & Information**
**Course: Software Engineering — Final Project**

---

## Team Members
1. Youssef Khaled Mohamed
2. Moataz Karim Massoud
3. Youssef Mohamed El Sayed
4. Sherif Mahmoud Abd El-Raouf
5. Mohamed Ahmed Nagah
---

## How to Run

```bash
cd clinic_system
python main.py
```

**Requirements:** Python 3.x (Tkinter is built in — no pip installs needed)

---

## Project File Structure

```
clinic_system/
│
├── main.py                         ← Entry point. Boots DB and opens the welcome screen.
├── database.py                     ← DATA LAYER. All SQL (CREATE, INSERT, SELECT, UPDATE, DELETE).
├── clinic.db                       ← Auto-created SQLite database on first run.
│
├── models/
│   ├── __init__.py                 ← Makes 'models' a Python package.
│   ├── user.py                     ← User class: SHA-256 hashing, login validation, RBAC.
│   ├── patient.py                  ← Patient class: fields, validation, city list.
│   ├── doctor.py                   ← Doctor class: specialties, schedules, slot logic.
│   ├── appointment.py              ← Appointment class: booking validation, state machine.
│   └── medical_record.py           ← MedicalRecord class: diagnosis + notes.
│
└── views/
    ├── __init__.py                 ← Makes 'views' a Python package.
    ├── theme.py                    ← Shared colors, fonts, and widget factory functions.
    ├── welcome_screen.py           ← FIRST SCREEN. Sign Up / Log In chooser + role selector.
    ├── auth_screen.py              ← Login & registration forms (role-specific fields).
    ├── dashboard_router.py         ← Top nav bar + routes to the right dashboard per role.
    ├── admin_screen.py             ← Admin: dashboard, patients, doctors, appointments.
    ├── doctor_screen.py            ← Doctor: dashboard, schedule, add diagnosis.
    └── patient_screen.py           ← Patient: dashboard, book appointment, history.
```

---

## Architecture: 3-Layer Design

| Layer | Files | Responsibility |
|-------|-------|----------------|
| **Presentation** | `views/` | All Tkinter windows and widgets |
| **Logic** | `models/` | Business rules: validation, state machine, hashing |
| **Data** | `database.py` + `clinic.db` | All SQL queries. No SQL anywhere else. |

---

## Security Features Implemented

| Feature | Where | How |
|---------|-------|-----|
| **Password Hashing** | `models/user.py` | SHA-256 via `hashlib.sha256()`. Plain text never stored. |
| **Role-Based Access Control** | `views/dashboard_router.py` | Each role sees only their permitted nav items and screens. |
| **Input Validation** | `models/patient.py`, `models/doctor.py`, `models/user.py` | All fields validated before any DB write. Clear error messages shown. |
| **Double-Booking Prevention (FR5)** | `database.py → is_slot_taken()` | Queries DB before saving any new appointment. |

---

## Demo Accounts (seeded on first run)

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `dr.ahmed` | `doc123` |
| Doctor | `dr.sara` | `doc123` |
| Patient | `youssef` | `pat123` |
| Patient | `nadia` | `pat123` |

---

## Functional Requirements Coverage

| ID | Feature | File |
|----|---------|------|
| FR1 | User Login | `views/auth_screen.py`, `models/user.py` |
| FR2 | Patient Registration | `views/auth_screen.py`, `models/patient.py` |
| FR3 | Doctor Registration | `views/auth_screen.py`, `models/doctor.py` |
| FR4 | Appointment Booking | `views/patient_screen.py → BookAppointment` |
| FR5 | Prevent Double Booking | `database.py → is_slot_taken()` |
| FR6 | Doctor Dashboard | `views/doctor_screen.py → DoctorDashboard` |
| FR7 | Add Diagnosis | `views/doctor_screen.py → DiagnoseView` |
| FR8 | View Medical History | `views/patient_screen.py → MyHistory` |
| FR9 | Cancel / Reschedule | `views/patient_screen.py`, `views/admin_screen.py` |
| FR10 | View Available Slots | `views/patient_screen.py → BookAppointment._check_slots()` |

---

## Database Tables

| Table | Primary Key | Foreign Keys |
|-------|-------------|--------------|
| `users` | `user_id` | — |
| `patients` | `patient_id` | `user_id → users` |
| `doctors` | `doctor_id` | `user_id → users` |
| `appointments` | `appointment_id` | `patient_id → patients`, `doctor_id → doctors` |
| `medical_history` | `record_id` | `patient_id → patients`, `doctor_id → doctors` |

---

## Appointment State Machine

```
Pending ──────→ Confirmed ──────→ Completed
   │                │
   └──→ Cancelled   └──→ Cancelled
                    │
                    └──→ Rescheduled ──→ Confirmed
```
Implemented in `models/appointment.py → TRANSITIONS` dictionary.
