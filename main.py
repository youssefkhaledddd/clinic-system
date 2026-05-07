"""
Smart Clinic Management System
Alexandria National University — Software Engineering Final Project

main.py — Application Entry Point
Initializes the database, seeds default data, and launches the app.
"""

import tkinter as tk
from database import Database
from views.welcome_screen import WelcomeScreen


def main():
    # Initialize database (creates clinic.db and all tables if not exist)
    db = Database()
    db.initialize()
    db.seed_defaults()

    # Create root Tkinter window
    root = tk.Tk()
    root.title("Smart Clinic Management System")
    root.geometry("1000x680")
    root.minsize(900, 620)
    root.configure(bg="#F0F4F8")

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1000 // 2)
    y = (root.winfo_screenheight() // 2) - (680 // 2)
    root.geometry(f"1000x680+{x}+{y}")

    # Launch welcome screen (Sign Up / Log In chooser)
    app = WelcomeScreen(root, db)
    app.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
