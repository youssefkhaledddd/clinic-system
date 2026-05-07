"""
models/user.py — User Model
Handles authentication logic, password hashing (SHA-256), and role-based routing.
Security: passwords are NEVER stored as plain text.
"""

import hashlib


class User:
    """Represents an authenticated system user."""

    ROLES = ("admin", "doctor", "patient")

    def __init__(self, user_id, username, role):
        self.user_id  = user_id
        self.username = username
        self.role     = role          # 'admin' | 'doctor' | 'patient'

    # ------------------------------------------------------------------ #
    #  SECURITY — Password Hashing (FR: passwords stored as SHA-256)      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def hash_password(plain_text: str) -> str:
        """
        Hash a plain-text password using SHA-256.
        Plain text is NEVER stored — only the hex digest is saved to DB.
        """
        return hashlib.sha256(plain_text.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(plain_text: str, stored_hash: str) -> bool:
        """Compare a plain-text attempt against a stored SHA-256 hash."""
        return User.hash_password(plain_text) == stored_hash

    # ------------------------------------------------------------------ #
    #  ROLE-BASED ACCESS CONTROL                                          #
    # ------------------------------------------------------------------ #

    def is_admin(self)   -> bool: return self.role == "admin"
    def is_doctor(self)  -> bool: return self.role == "doctor"
    def is_patient(self) -> bool: return self.role == "patient"

    @staticmethod
    def validate_registration(username: str, password: str, confirm: str) -> str | None:
        """
        Validate registration input.
        Returns an error string, or None if everything is valid.
        """
        if not username or not password or not confirm:
            return "All fields are required."
        if len(username) < 3:
            return "Username must be at least 3 characters."
        if len(password) < 6:
            return "Password must be at least 6 characters."
        if password != confirm:
            return "Passwords do not match."
        if " " in username:
            return "Username must not contain spaces."
        return None

    def __repr__(self):
        return f"<User id={self.user_id} username={self.username!r} role={self.role}>"
