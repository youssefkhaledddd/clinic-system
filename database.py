"""
database.py — Data Layer
Manages all SQLite operations: connection, table creation, CRUD for every table.
No business logic lives here — only raw database interactions.
"""

import sqlite3
import os
from models.user import User


DB_PATH = "clinic.db"


class Database:
    def __init__(self):
        self.path = DB_PATH

    def connect(self):
        """Return a new SQLite connection with foreign keys enabled."""
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row   # rows accessible as dicts
        return conn

    # ------------------------------------------------------------------ #
    #  INITIALIZATION                                                      #
    # ------------------------------------------------------------------ #

    def initialize(self):
        """Create all tables if they do not exist."""
        conn = self.connect()
        c = conn.cursor()

        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    UNIQUE NOT NULL,
                password  TEXT    NOT NULL,
                role      TEXT    NOT NULL CHECK(role IN ('admin','doctor','patient'))
            );

            CREATE TABLE IF NOT EXISTS patients (
                patient_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER UNIQUE,
                name        TEXT    NOT NULL,
                age         INTEGER NOT NULL,
                gender      TEXT    NOT NULL,
                phone       TEXT    NOT NULL,
                address     TEXT    NOT NULL,
                city        TEXT    NOT NULL DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER UNIQUE,
                name       TEXT NOT NULL,
                specialty  TEXT NOT NULL,
                phone      TEXT NOT NULL,
                schedule   TEXT NOT NULL,
                city       TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id      INTEGER NOT NULL,
                doctor_id       INTEGER NOT NULL,
                date            TEXT    NOT NULL,
                time            TEXT    NOT NULL,
                status          TEXT    NOT NULL DEFAULT 'Pending'
                                CHECK(status IN ('Pending','Confirmed','Completed','Cancelled','Rescheduled')),
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
            );

            CREATE TABLE IF NOT EXISTS medical_history (
                record_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id  INTEGER NOT NULL,
                doctor_id   INTEGER NOT NULL,
                date        TEXT    NOT NULL,
                diagnosis   TEXT    NOT NULL,
                notes       TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
            );
        """)

        conn.commit()
        conn.close()

    def seed_defaults(self):
        """Insert default admin + sample data only if DB is empty."""
        conn = self.connect()
        c = conn.cursor()

        # Check if admin already exists
        if c.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
            conn.close()
            return

        # Default Admin
        admin_pwd = User.hash_password("admin123")
        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                  ("admin", admin_pwd, "admin"))

        # Sample doctors
        doc_pwd = User.hash_password("doc123")
        doctors = [
            ("dr.ahmed", "Dr. Ahmed Hassan",  "Cardiology",   "01011223344", "Sun-Thu 09:00-17:00", "Alexandria"),
            ("dr.sara",  "Dr. Sara Khalil",   "Pediatrics",   "01099887766", "Mon-Wed 10:00-15:00", "Cairo"),
            ("dr.rami",  "Dr. Rami Nour",     "Orthopedics",  "01066554433", "Sat-Thu 08:00-14:00", "Alexandria"),
            ("dr.layla", "Dr. Layla Mansour", "Dermatology",  "01055443322", "Sun-Tue 11:00-16:00", "Giza"),
        ]
        for uname, name, spec, phone, sched, city in doctors:
            c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                      (uname, doc_pwd, "doctor"))
            uid = c.lastrowid
            c.execute("INSERT INTO doctors (user_id,name,specialty,phone,schedule,city) VALUES (?,?,?,?,?,?)",
                      (uid, name, spec, phone, sched, city))

        # Sample patients
        pat_pwd = User.hash_password("pat123")
        patients = [
            ("youssef",  "Youssef Khaled", 24, "Male",   "01012345678", "Sidi Gaber, Alexandria",     "Alexandria"),
            ("nadia",    "Nadia Farouk",   32, "Female", "01098765432", "Nasr City, Cairo",            "Cairo"),
            ("omar",     "Omar Tarek",     45, "Male",   "01155667788", "Dokki, Giza",                 "Giza"),
        ]
        for uname, name, age, gender, phone, addr, city in patients:
            c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                      (uname, pat_pwd, "patient"))
            uid = c.lastrowid
            c.execute("INSERT INTO patients (user_id,name,age,gender,phone,address,city) VALUES (?,?,?,?,?,?,?)",
                      (uid, name, age, gender, phone, addr, city))

        # Sample appointments
        c.execute("SELECT patient_id FROM patients WHERE name='Youssef Khaled'")
        p1 = c.fetchone()[0]
        c.execute("SELECT patient_id FROM patients WHERE name='Nadia Farouk'")
        p2 = c.fetchone()[0]
        c.execute("SELECT patient_id FROM patients WHERE name='Omar Tarek'")
        p3 = c.fetchone()[0]
        c.execute("SELECT doctor_id FROM doctors WHERE name='Dr. Ahmed Hassan'")
        d1 = c.fetchone()[0]
        c.execute("SELECT doctor_id FROM doctors WHERE name='Dr. Sara Khalil'")
        d2 = c.fetchone()[0]

        appts = [
            (p1, d1, "2026-04-25", "10:00", "Confirmed"),
            (p2, d2, "2026-04-26", "11:00", "Pending"),
            (p3, d1, "2026-04-19", "09:00", "Completed"),
        ]
        for pid, did, date, time, status in appts:
            c.execute("INSERT INTO appointments (patient_id,doctor_id,date,time,status) VALUES (?,?,?,?,?)",
                      (pid, did, date, time, status))

        # Sample medical history
        c.execute("INSERT INTO medical_history (patient_id,doctor_id,date,diagnosis,notes) VALUES (?,?,?,?,?)",
                  (p3, d1, "2026-04-19", "Hypertension Stage 1",
                   "Prescribed Amlodipine 5mg daily. Follow up in 2 weeks."))
        c.execute("INSERT INTO medical_history (patient_id,doctor_id,date,diagnosis,notes) VALUES (?,?,?,?,?)",
                  (p1, d1, "2026-03-10", "Mild Arrhythmia",
                   "ECG performed. Monitor for 1 month. Avoid caffeine."))

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------ #
    #  USER OPERATIONS                                                     #
    # ------------------------------------------------------------------ #

    def get_user_by_credentials(self, username, hashed_password):
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed_password)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def username_exists(self, username):
        conn = self.connect()
        row = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        return row is not None

    def create_user(self, username, hashed_password, role):
        """Insert a new user and return the new user_id."""
        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                  (username, hashed_password, role))
        uid = c.lastrowid
        conn.commit()
        conn.close()
        return uid

    # ------------------------------------------------------------------ #
    #  PATIENT OPERATIONS                                                  #
    # ------------------------------------------------------------------ #

    def create_patient(self, user_id, name, age, gender, phone, address, city):
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO patients (user_id,name,age,gender,phone,address,city) VALUES (?,?,?,?,?,?,?)",
            (user_id, name, age, gender, phone, address, city)
        )
        pid = c.lastrowid
        conn.commit()
        conn.close()
        return pid

    def get_patient_by_user_id(self, user_id):
        conn = self.connect()
        row = conn.execute("SELECT * FROM patients WHERE user_id=?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_patients(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def patient_name_exists(self, name):
        conn = self.connect()
        row = conn.execute("SELECT 1 FROM patients WHERE LOWER(name)=LOWER(?)", (name,)).fetchone()
        conn.close()
        return row is not None

    def delete_patient(self, patient_id):
        conn = self.connect()
        conn.execute("DELETE FROM appointments WHERE patient_id=?", (patient_id,))
        conn.execute("DELETE FROM medical_history WHERE patient_id=?", (patient_id,))
        conn.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------ #
    #  DOCTOR OPERATIONS                                                   #
    # ------------------------------------------------------------------ #

    def create_doctor(self, user_id, name, specialty, phone, schedule, city):
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO doctors (user_id,name,specialty,phone,schedule,city) VALUES (?,?,?,?,?,?)",
            (user_id, name, specialty, phone, schedule, city)
        )
        did = c.lastrowid
        conn.commit()
        conn.close()
        return did

    def get_doctor_by_user_id(self, user_id):
        conn = self.connect()
        row = conn.execute("SELECT * FROM doctors WHERE user_id=?", (user_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_doctors(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM doctors ORDER BY name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_doctors_by_city(self, city):
        conn = self.connect()
        rows = conn.execute(
            "SELECT * FROM doctors WHERE LOWER(city)=LOWER(?) ORDER BY name", (city,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_doctors_by_city_and_specialty(self, city, specialty):
        conn = self.connect()
        rows = conn.execute(
            "SELECT * FROM doctors WHERE LOWER(city)=LOWER(?) AND LOWER(specialty)=LOWER(?) ORDER BY name",
            (city, specialty)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_doctor(self, doctor_id):
        conn = self.connect()
        conn.execute("DELETE FROM appointments WHERE doctor_id=?", (doctor_id,))
        conn.execute("DELETE FROM doctors WHERE doctor_id=?", (doctor_id,))
        conn.commit()
        conn.close()

    def get_distinct_cities(self):
        conn = self.connect()
        rows = conn.execute("SELECT DISTINCT city FROM doctors WHERE city != '' ORDER BY city").fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_distinct_specialties(self):
        conn = self.connect()
        rows = conn.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty").fetchall()
        conn.close()
        return [r[0] for r in rows]

    # ------------------------------------------------------------------ #
    #  APPOINTMENT OPERATIONS                                              #
    # ------------------------------------------------------------------ #

    def create_appointment(self, patient_id, doctor_id, date, time):
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            "INSERT INTO appointments (patient_id,doctor_id,date,time,status) VALUES (?,?,?,?,'Pending')",
            (patient_id, doctor_id, date, time)
        )
        aid = c.lastrowid
        conn.commit()
        conn.close()
        return aid

    def is_slot_taken(self, doctor_id, date, time, exclude_id=None):
        """Check for double booking (FR5)."""
        conn = self.connect()
        if exclude_id:
            row = conn.execute(
                "SELECT 1 FROM appointments WHERE doctor_id=? AND date=? AND time=? AND status!='Cancelled' AND appointment_id!=?",
                (doctor_id, date, time, exclude_id)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM appointments WHERE doctor_id=? AND date=? AND time=? AND status!='Cancelled'",
                (doctor_id, date, time)
            ).fetchone()
        conn.close()
        return row is not None

    def get_booked_times(self, doctor_id, date):
        conn = self.connect()
        rows = conn.execute(
            "SELECT time FROM appointments WHERE doctor_id=? AND date=? AND status!='Cancelled'",
            (doctor_id, date)
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]

    def get_appointments_for_patient(self, patient_id):
        conn = self.connect()
        rows = conn.execute("""
            SELECT a.*, d.name as doctor_name, d.specialty
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = ?
            ORDER BY a.date DESC, a.time DESC
        """, (patient_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_appointments_for_doctor(self, doctor_id):
        conn = self.connect()
        rows = conn.execute("""
            SELECT a.*, p.name as patient_name, p.age, p.gender
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = ?
            ORDER BY a.date, a.time
        """, (doctor_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_appointments(self):
        conn = self.connect()
        rows = conn.execute("""
            SELECT a.*,
                   p.name as patient_name,
                   d.name as doctor_name,
                   d.specialty
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors  d ON a.doctor_id  = d.doctor_id
            ORDER BY a.date, a.time
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_appointment_status(self, appointment_id, status):
        conn = self.connect()
        conn.execute("UPDATE appointments SET status=? WHERE appointment_id=?",
                     (status, appointment_id))
        conn.commit()
        conn.close()

    def reschedule_appointment(self, appointment_id, new_date, new_time):
        conn = self.connect()
        conn.execute(
            "UPDATE appointments SET date=?, time=?, status='Rescheduled' WHERE appointment_id=?",
            (new_date, new_time, appointment_id)
        )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------ #
    #  MEDICAL HISTORY OPERATIONS                                          #
    # ------------------------------------------------------------------ #

    def add_medical_record(self, patient_id, doctor_id, date, diagnosis, notes=""):
        conn = self.connect()
        conn.execute(
            "INSERT INTO medical_history (patient_id,doctor_id,date,diagnosis,notes) VALUES (?,?,?,?,?)",
            (patient_id, doctor_id, date, diagnosis, notes)
        )
        conn.commit()
        conn.close()

    def get_history_for_patient(self, patient_id):
        conn = self.connect()
        rows = conn.execute("""
            SELECT mh.*, d.name as doctor_name, d.specialty
            FROM medical_history mh
            JOIN doctors d ON mh.doctor_id = d.doctor_id
            WHERE mh.patient_id = ?
            ORDER BY mh.date DESC
        """, (patient_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  STATS (for admin dashboard)                                        #
    # ------------------------------------------------------------------ #

    def get_stats(self):
        conn = self.connect()
        stats = {
            "patients":    conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
            "doctors":     conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
            "appointments":conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
            "confirmed":   conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Confirmed'").fetchone()[0],
            "pending":     conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Pending'").fetchone()[0],
            "completed":   conn.execute("SELECT COUNT(*) FROM appointments WHERE status='Completed'").fetchone()[0],
            "records":     conn.execute("SELECT COUNT(*) FROM medical_history").fetchone()[0],
        }
        conn.close()
        return stats
