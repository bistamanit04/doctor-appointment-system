import sqlite3
from config import DATABASE
import hashlib


def get_connection():
    return sqlite3.connect(DATABASE)



def hash_password(password):

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        b"doctor_appointment_salt",
        100000
    ).hex()
    

def create_admin(name, email, password):

    connection = get_connection()
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        INSERT INTO admin (name, email, password)
        VALUES (?, ?, ?)
    """, (
        name,
        email,
        hashed_password
    ))

    connection.commit()
    connection.close()



def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # Patient table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            date_of_birth TEXT,
            gender TEXT,
            address TEXT,
            password TEXT NOT NULL
        )
    """)

    # Doctor table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Time Slot table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_slot (
            slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,

            FOREIGN KEY (doctor_id)
            REFERENCES doctor(doctor_id)
        )
    """)

    # Appointment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            slot_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',

            FOREIGN KEY (patient_id)
            REFERENCES patient(patient_id),

            FOREIGN KEY (doctor_id)
            REFERENCES doctor(doctor_id),

            FOREIGN KEY (slot_id)
            REFERENCES time_slot(slot_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_bio(
            bio_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER UNIQUE NOT NULL,
            profile_image TEXT,
            nmc_no TEXT UNIQUE NOT NULL,
            experience INTEGER DEFAULT 0,
            qualification TEXT,
            location TEXT,
            about TEXT,
            consultation_fee REAL DEFAULT 0,
            FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
            )
    """)
    
    # Admin table
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS admin (
         admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         email TEXT NOT NULL UNIQUE,
         password TEXT NOT NULL
         )
    """)




    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()

