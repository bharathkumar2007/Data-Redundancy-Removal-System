import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL was not found. "
        "Please check your .env file."
    )


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    """Create and return a PostgreSQL database connection."""

    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------

def create_tables():
    """Create the required PostgreSQL tables."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # Main records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    data_hash TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL DEFAULT 'Unique',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Duplicate / review logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_logs (
                    log_id BIGSERIAL PRIMARY KEY,
                    submitted_name TEXT NOT NULL,
                    submitted_email TEXT NOT NULL,
                    submitted_phone TEXT NOT NULL,
                    matched_record_id BIGINT,
                    similarity_score DOUBLE PRECISION,
                    decision TEXT NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        connection.commit()

    finally:
        connection.close()


# ---------------------------------------------------------
# GET ALL RECORDS
# ---------------------------------------------------------

def get_all_records():
    """Return all records from the cloud database."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    data_hash,
                    status,
                    created_at
                FROM records
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    finally:
        connection.close()


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

    try:
        with connection.cursor() as cursor:

            try:

                cursor.execute("""
                    INSERT INTO records (
                        name,
                        email,
                        phone,
                        data_hash,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    name,
                    email,
                    phone,
                    data_hash,
                    status
                ))

                result = cursor.fetchone()

                connection.commit()

                return True, result["id"]

            except psycopg2.IntegrityError:

                connection.rollback()

                return False, None

    finally:
        connection.close()


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

    try:
        with connection.cursor() as cursor:

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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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

    finally:
        connection.close()


# ---------------------------------------------------------
# GET DUPLICATE LOGS
# ---------------------------------------------------------

def get_duplicate_logs():
    """Return duplicate and review detection logs."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    log_id,
                    submitted_name,
                    submitted_email,
                    submitted_phone,
                    matched_record_id,
                    similarity_score,
                    decision,
                    reason,
                    created_at
                FROM duplicate_logs
                ORDER BY log_id DESC
            """)

            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    finally:
        connection.close()


# ---------------------------------------------------------
# GET TOTAL RECORD COUNT
# ---------------------------------------------------------

def get_record_count():
    """Return the total number of stored records."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*) AS count
                FROM records
            """)

            result = cursor.fetchone()

            return result["count"]

    finally:
        connection.close()


# ---------------------------------------------------------
# GET STATUS COUNTS
# ---------------------------------------------------------

def get_status_counts():
    """Return the number of records for each status."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT status, COUNT(*) AS count
                FROM records
                GROUP BY status
            """)

            rows = cursor.fetchall()

            counts = {
                "Unique": 0,
                "Review": 0,
                "Duplicate": 0
            }

            for row in rows:
                counts[row["status"]] = row["count"]

            return counts

    finally:
        connection.close()


# ---------------------------------------------------------
# DELETE ALL DATA
# ---------------------------------------------------------

def delete_all_data():
    """Delete all application records and logs."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "DELETE FROM duplicate_logs"
            )

            cursor.execute(
                "DELETE FROM records"
            )

        connection.commit()

    finally:
        connection.close()


# ---------------------------------------------------------
# TEST DATABASE CONNECTION
# ---------------------------------------------------------

if __name__ == "__main__":

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT version()
            """)

            result = cursor.fetchone()

            print("✅ Connected to Supabase PostgreSQL.")
            print("PostgreSQL version:")
            print(result["version"])

        connection.close()

        create_tables()

        print("✅ Database tables created successfully.")

    except Exception as error:

        print("❌ Database connection failed.")
        print("Error:", error)