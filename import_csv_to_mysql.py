"""
One-time import of old CSV data into MySQL.

Usage (from the project folder):
    python import_csv_to_mysql.py                        # bookings.csv (+ waitlist.csv if present)
    python import_csv_to_mysql.py docs/sample_bookings.csv

It reuses the connection settings and table setup from main.py, so the database
and tables are created automatically if they do not exist yet.
Re-running is safe: rows with the same booking_id are updated, not duplicated.
Dates in YYYY-MM-DD or DD-MM-YYYY format are both accepted.
"""
import csv
import os
import sys
from datetime import datetime

from mysql.connector import Error

from main import init_db, get_connection, explain_db_error


def to_iso(text):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    raise ValueError(f"Unrecognised date: {text!r}")


def main():
    bookings_file = sys.argv[1] if len(sys.argv) > 1 else "bookings.csv"
    waitlist_file = "waitlist.csv"

    init_db()                      # asks for password, creates database + tables if missing
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        if os.path.exists(bookings_file):
            with open(bookings_file, newline="") as f:
                rows = [(r["booking_id"], r["name"], int(r["age"]), r["bus_id"],
                         to_iso(r["journey_date"]), int(r["seat_no"]),
                         float(r["fare"]), r["status"]) for r in csv.DictReader(f)]
            cur.executemany(
                """INSERT INTO bookings
                   (booking_id, name, age, bus_id, journey_date, seat_no, fare, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE name=VALUES(name), age=VALUES(age),
                     bus_id=VALUES(bus_id), journey_date=VALUES(journey_date),
                     seat_no=VALUES(seat_no), fare=VALUES(fare), status=VALUES(status)""",
                rows)
            print(f"Imported {len(rows)} bookings from {bookings_file}")
        else:
            print(f"{bookings_file} not found - skipped")

        if bookings_file == "bookings.csv" and os.path.exists(waitlist_file):
            with open(waitlist_file, newline="") as f:
                rows = [(r["name"], int(r["age"]), r["bus_id"], to_iso(r["journey_date"]))
                        for r in csv.DictReader(f)]
            cur.execute("DELETE FROM waiting_list")
            cur.executemany(
                "INSERT INTO waiting_list (name, age, bus_id, journey_date) VALUES (%s,%s,%s,%s)",
                rows)
            print(f"Imported {len(rows)} waiting-list entries from {waitlist_file}")

        conn.commit()
        cur.close()
    except Error as e:
        if conn:
            conn.rollback()
        explain_db_error(e)
        raise SystemExit(1)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()
