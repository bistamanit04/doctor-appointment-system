import os

# ==========================================
# Project Information
# ==========================================

APP_NAME = "Doctor Appointment System"
DEBUG = True


# ==========================================
# Server Configuration
# ==========================================

HOST = "localhost"
PORT = 8000


# ==========================================
# Project Directories
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

STATIC_DIR = os.path.join(BASE_DIR, "static")


# ==========================================
# Database Configuration
# ==========================================

DATABASE = os.path.join(BASE_DIR, "doctor.db")