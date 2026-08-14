import sqlite3
from pathlib import Path


# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------

DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "database.db"


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    """Create and return a connection to the SQLite database."""

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------

def create_tables():
    """Create the required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Main table for verified/unique records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            data_hash TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'Unique',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for duplicate and review detections
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS duplicate_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            submitted_name TEXT NOT NULL,
            submitted_email TEXT NOT NULL,
            submitted_phone TEXT NOT NULL,
            matched_record_id INTEGER,
            similarity_score REAL,
            decision TEXT NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# GET ALL RECORDS
# ---------------------------------------------------------

def get_all_records():
    """Return all records from the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM records
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ---------------------------------------------------------
# INSERT RECORD
# ---------------------------------------------------------

def insert_record(
    name,
    email,
    phone,
    data_hash,
    status="Unique"
):
    """Insert a verified unique record."""

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO records (
                name,
                email,
                phone,
                data_hash,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            data_hash,
            status
        ))

        connection.commit()

        record_id = cursor.lastrowid

        connection.close()

        return True, record_id

    except sqlite3.IntegrityError:

        connection.close()

        return False, None


# ---------------------------------------------------------
# ADD DUPLICATE LOG
# ---------------------------------------------------------

def add_duplicate_log(
    submitted_name,
    submitted_email,
    submitted_phone,
    matched_record_id,
    similarity_score,
    decision,
    reason
):
    """Store duplicate or review information."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO duplicate_logs (
            submitted_name,
            submitted_email,
            submitted_phone,
            matched_record_id,
            similarity_score,
            decision,
            reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        submitted_name,
        submitted_email,
        submitted_phone,
        matched_record_id,
        similarity_score,
        decision,
        reason
    ))

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# GET DUPLICATE LOGS
# ---------------------------------------------------------

def get_duplicate_logs():
    """Return duplicate/review detection logs."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM duplicate_logs
        ORDER BY log_id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ---------------------------------------------------------
# GET TOTAL RECORD COUNT
# ---------------------------------------------------------

def get_record_count():
    """Return the total number of stored records."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM records
    """)

    result = cursor.fetchone()

    connection.close()

    return result["count"]


# ---------------------------------------------------------
# GET STATUS COUNTS
# ---------------------------------------------------------

def get_status_counts():
    """Return the number of records for each status."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT status, COUNT(*) AS count
        FROM records
        GROUP BY status
    """)

    rows = cursor.fetchall()

    connection.close()

    counts = {
        "Unique": 0,
        "Review": 0,
        "Duplicate": 0
    }

    for row in rows:
        counts[row["status"]] = row["count"]

    return counts


# ---------------------------------------------------------
# DELETE ALL DATA
# ---------------------------------------------------------

def delete_all_data():
    """Delete all application data."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM records")
    cursor.execute("DELETE FROM duplicate_logs")

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# TEST DATABASE
# ---------------------------------------------------------

if __name__ == "__main__":

    create_tables()

    print("Database and tables created successfully.")

    print(
        f"Database location: {DATABASE_PATH}"
    )