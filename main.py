"""
SwiftTravel - Bus Reservation System
=====================================
A console-based Python application demonstrating:
- Custom Doubly Linked List (core data structure for bookings & waiting list)
- MySQL database (persistent storage)
- OOP (Passenger, Booking classes)
- Exception handling, input validation
- Date-based early booking window (book up to 8 days in advance)
- Automatic waiting-list allocation when seats are freed
"""

import getpass
import os
from datetime import datetime, timedelta

import mysql.connector
from mysql.connector import Error

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
DATE_FORMAT = "%Y-%m-%d"
BOOKING_WINDOW_DAYS = 8   # passengers can book for today .. today + 7 (8 days total)

BUSES = {
    "P101": {"route": "Pune -> Mumbai", "departure": "08:00 AM", "arrival": "12:00 PM",
              "total_seats": 10, "fare": 250},
    "P102": {"route": "Pune -> Nashik", "departure": "09:30 AM", "arrival": "01:00 PM",
              "total_seats": 12, "fare": 450},
    "P103": {"route": "Pune -> Burhanpur", "departure": "08:00 AM", "arrival": "10:00 PM",
              "total_seats": 10, "fare": 750},
    "P104": {"route": "Pune -> Jalgoan", "departure": "09:30 AM", "arrival": "8:00 PM",
              "total_seats": 12, "fare": 650},
    "P105": {"route": "Pune -> Bhusawal", "departure": "08:00 AM", "arrival": "6:00 PM",
              "total_seats": 10, "fare": 550},
    "P106": {"route": "Pune -> surat", "departure": "05:30 AM", "arrival": "01:00 PM",
              "total_seats": 12, "fare": 750},          
}


# ------------------------------------------------------------------
# DOUBLY LINKED LIST (core data structure)
# ------------------------------------------------------------------
class Node:
    """A single node of the doubly linked list."""
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoublyLinkedList:
    """
    Generic doubly linked list used to store both bookings and
    waiting-list entries. Supports append, removal, search and
    ordered traversal (needed for FIFO waiting-list processing).
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append(self, data):
        node = Node(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.length += 1
        return node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None
        self.length -= 1

    def remove_where(self, predicate):
        """Remove and return the first node whose data matches predicate."""
        current = self.head
        while current:
            if predicate(current.data):
                self.remove(current)
                return current.data
            current = current.next
        return None

    def find_node(self, predicate):
        current = self.head
        while current:
            if predicate(current.data):
                return current
            current = current.next
        return None

    def find_all(self, predicate):
        result = []
        current = self.head
        while current:
            if predicate(current.data):
                result.append(current.data)
            current = current.next
        return result

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __len__(self):
        return self.length


# ------------------------------------------------------------------
# OOP MODELS
# ------------------------------------------------------------------
class Passenger:
    def __init__(self, name, age):
        self.name = name.strip().title()
        self.age = age

    def __str__(self):
        return f"{self.name} (Age {self.age})"


class Booking:
    def __init__(self, booking_id, passenger, bus_id, journey_date, seat_no, fare, status="CONFIRMED"):
        self.booking_id = booking_id
        self.passenger = passenger
        self.bus_id = bus_id
        self.journey_date = journey_date   # string "YYYY-MM-DD"
        self.seat_no = seat_no
        self.fare = fare
        self.status = status

    def to_row(self):
        return [self.booking_id, self.passenger.name, self.passenger.age,
                self.bus_id, self.journey_date, self.seat_no, f"{self.fare:.2f}", self.status]

    @staticmethod
    def from_row(row):
        booking_id, name, age, bus_id, journey_date, seat_no, fare, status = row
        passenger = Passenger(name, int(age))
        return Booking(booking_id, passenger, bus_id, journey_date, int(seat_no), float(fare), status)

    def display(self):
        route = BUSES.get(self.bus_id, {}).get("route", "Unknown route")
        print("=" * 42)
        print(" BOOKING DETAILS")
        print("=" * 42)
        print(f"Booking ID : {self.booking_id}")
        print(f"Passenger  : {self.passenger.name}")
        print(f"Journey    : {self.bus_id}")
        print(f"Route      : {route}")
        print(f"Date       : {self.journey_date}")
        print(f"Seat       : {self.seat_no:02d}")
        print(f"Fare       : Rs.{self.fare:.2f}")
        print(f"Status     : {self.status}")
        print("=" * 42)


# ------------------------------------------------------------------
# GLOBAL STATE
# ------------------------------------------------------------------
bookings = DoublyLinkedList()   # holds Booking objects (all statuses)
waiting_list = DoublyLinkedList()  # holds dicts: {name, age, bus_id, journey_date}


# ------------------------------------------------------------------
# MYSQL CONFIG
# ------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    # None = you will be asked for the password when the program starts.
    # (Or set the DB_PASSWORD environment variable, or type it here.)
    "password": os.getenv("DB_PASSWORD","20042004"),
    "database": os.getenv("DB_NAME", "swifttravel"),
}


def explain_db_error(e):
    """Print a MySQL error together with a plain-language hint on how to fix it."""
    code = getattr(e, "errno", None)
    text = str(e).lower()
    print(f"\nMySQL error: {e}")
    if code == 1045:
        print("Hint: wrong MySQL username or password.")
    elif code == 2003:
        print("Hint: cannot reach MySQL. Start the MySQL service "
              "(Win+R -> services.msc -> MySQL80 -> Start).")
    elif code == 1049:
        print("Hint: the database does not exist. Restart the program so it can create it.")
    elif code in (1021, 1114, 3675, 28) or "disk is full" in text or "no space" in text:
        print("Hint: the disk that holds MySQL's data folder is FULL. Free up space on that "
              "drive (Recycle Bin, Disk Cleanup, MySQL binlog files), restart the MySQL "
              "service, then run this program again.")


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Ask for the password if needed, then create the database and tables if missing."""
    if DB_CONFIG["password"] is None:
        DB_CONFIG["password"] = getpass.getpass(
            f"MySQL password for user '{DB_CONFIG['user']}' (press Enter if none): ")
    conn = None
    try:
        # connect WITHOUT a database first, so the database itself can be created
        cfg = {k: v for k, v in DB_CONFIG.items() if k != "database"}
        conn = mysql.connector.connect(**cfg)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
        conn.commit()
        cur.close()
        conn.close()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id   VARCHAR(10) PRIMARY KEY,
                name         VARCHAR(100) NOT NULL,
                age          INT NOT NULL,
                bus_id       VARCHAR(10) NOT NULL,
                journey_date DATE NOT NULL,
                seat_no      INT NOT NULL,
                fare         DECIMAL(8,2) NOT NULL,
                status       VARCHAR(15) NOT NULL
            )
        """)
        # AUTO_INCREMENT id keeps the FIFO order of the waiting list
        cur.execute("""
            CREATE TABLE IF NOT EXISTS waiting_list (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                name         VARCHAR(100) NOT NULL,
                age          INT NOT NULL,
                bus_id       VARCHAR(10) NOT NULL,
                journey_date DATE NOT NULL
            )
        """)
        conn.commit()
        cur.close()
    except Error as e:
        explain_db_error(e)
        raise SystemExit(1)
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


# ------------------------------------------------------------------
# FILE HANDLING  ->  now MySQL
# ------------------------------------------------------------------
def load_data():
    """Load bookings and waiting list from MySQL into the linked lists."""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT booking_id, name, age, bus_id, journey_date, seat_no, fare, status
            FROM bookings
            ORDER BY CAST(SUBSTRING(booking_id, 3) AS UNSIGNED)
        """)
        for (booking_id, name, age, bus_id, jdate, seat_no, fare, status) in cur.fetchall():
            passenger = Passenger(name, int(age))
            bookings.append(Booking(booking_id, passenger, bus_id, str(jdate),
                                    int(seat_no), float(fare), status))

        cur.execute("SELECT name, age, bus_id, journey_date FROM waiting_list ORDER BY id")
        for (name, age, bus_id, jdate) in cur.fetchall():
            waiting_list.append({"name": name, "age": int(age),
                                 "bus_id": bus_id, "journey_date": str(jdate)})

        cur.close()
        conn.close()
    except Error as e:
        explain_db_error(e)
        print("Exiting so your saved data is not overwritten.")
        raise SystemExit(1)


def save_data():
    """Persist current bookings and waiting list to MySQL (in one transaction)."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM bookings")
        cur.executemany(
            """INSERT INTO bookings
               (booking_id, name, age, bus_id, journey_date, seat_no, fare, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            [(b.booking_id, b.passenger.name, b.passenger.age, b.bus_id,
              b.journey_date, b.seat_no, round(b.fare, 2), b.status)
             for b in bookings],
        )

        cur.execute("DELETE FROM waiting_list")
        cur.executemany(
            """INSERT INTO waiting_list (name, age, bus_id, journey_date)
               VALUES (%s, %s, %s, %s)""",
            [(w["name"], w["age"], w["bus_id"], w["journey_date"]) for w in waiting_list],
        )

        conn.commit()      # both tables saved together, or neither
        cur.close()
    except Error as e:
        if conn:
            conn.rollback()
        print("Could not save your data - nothing was changed in the database.")
        explain_db_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def generate_booking_id():
    max_num = 1000
    for b in bookings:
        try:
            num = int(b.booking_id.replace("ST", ""))
            max_num = max(max_num, num)
        except ValueError:
            continue
    return f"ST{max_num + 1}"


def calculate_fare(base_fare, age):
    """Apply age-based discount rules."""
    if age < 12:
        return base_fare * 0.5
    elif age >= 60:
        return base_fare * 0.7
    return base_fare * 1.0


def get_booked_seats(bus_id, journey_date):
    """Seats already CONFIRMED for a given bus on a given date."""
    matches = bookings.find_all(
        lambda b: b.bus_id == bus_id and b.journey_date == journey_date and b.status == "CONFIRMED"
    )
    return {b.seat_no for b in matches}


def get_available_seats(bus_id, journey_date):
    total = BUSES[bus_id]["total_seats"]
    booked = get_booked_seats(bus_id, journey_date)
    return sorted(set(range(1, total + 1)) - booked)


def valid_date_choices():
    """Return the list of allowed date strings for the booking window."""
    today = datetime.now().date()
    return [(today + timedelta(days=i)).strftime(DATE_FORMAT) for i in range(BOOKING_WINDOW_DAYS)]


def prompt_journey_date():
    """
    Ask the user for a travel date, enforcing the early-booking window:
    only today through (today + BOOKING_WINDOW_DAYS - 1) are allowed.
    Returns a valid date string, or None if the user cancels.
    """
    allowed = valid_date_choices()
    print(f"\nAvailable booking window (next {BOOKING_WINDOW_DAYS} days):")
    for i, d in enumerate(allowed, start=1):
        weekday = datetime.strptime(d, DATE_FORMAT).strftime("%a")
        print(f"  {i}. {d} ({weekday})")

    while True:
        choice = input(f"Enter date (YYYY-MM-DD) or option number [1-{len(allowed)}], 'c' to cancel: ").strip()
        if choice.lower() == "c":
            return None
        # allow picking by menu number
        if choice.isdigit() and 1 <= int(choice) <= len(allowed):
            return allowed[int(choice) - 1]
        # allow typing the date directly
        try:
            parsed = datetime.strptime(choice, DATE_FORMAT).date()
        except ValueError:
            print("Invalid format. Use YYYY-MM-DD or pick a listed option number.")
            continue
        date_str = parsed.strftime(DATE_FORMAT)
        if date_str not in allowed:
            print(f"Bookings are only open for the next {BOOKING_WINDOW_DAYS} days "
                  f"({allowed[0]} to {allowed[-1]}). Please choose a date in that range.")
            continue
        return date_str


def prompt_int(prompt_text, min_value=None, max_value=None):
    """Repeatedly prompt until a valid integer (within optional bounds) is given, or 'c' cancels."""
    while True:
        raw = input(prompt_text).strip()
        if raw.lower() == "c":
            return None
        try:
            value = int(raw)
        except ValueError:
            print("Invalid input. Age/seat must be a number. Please try again.")
            continue
        if min_value is not None and value < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return value


def prompt_bus_id():
    while True:
        bus_id = input("Enter journey ID (or 'c' to cancel): ").strip().upper()
        if bus_id == "C":
            return None
        if bus_id in BUSES:
            return bus_id
        print("Invalid journey ID. Please choose from the bus list (e.g. P101).")


# ------------------------------------------------------------------
# CORE FEATURES
# ------------------------------------------------------------------
def display_menu():
    print("\n=====================================")
    print(" SWIFTTRAVEL - BUS RESERVATION SYSTEM")
    print("=====================================")
    print("1. View Buses")
    print("2. View Available Seats")
    print("3. Book Ticket")
    print("4. Cancel Ticket")
    print("5. View Booking")
    print("6. Search Passenger / Booking")
    print("7. Exit")


def view_buses():
    print("\n" + "-" * 65)
    print(f"{'ID':<6}{'ROUTE':<18}{'TIME':<12}{'FARE':<10}{'TOTAL SEATS':<12}")
    print("-" * 65)
    for bus_id, info in BUSES.items():
        print(f"{bus_id:<6}{info['route']:<18}{info['departure']:<12}"
              f"Rs.{info['fare']:<8}{info['total_seats']:<12}")
    print("-" * 65)
    print("Note: seat availability depends on the travel date - use option 2 to check a specific day.")


def view_seats():
    bus_id = prompt_bus_id()
    if bus_id is None:
        return
    journey_date = prompt_journey_date()
    if journey_date is None:
        return

    total = BUSES[bus_id]["total_seats"]
    available = set(get_available_seats(bus_id, journey_date))
    booked = set(range(1, total + 1)) - available

    print(f"\nBUS {bus_id} - {BUSES[bus_id]['route']} on {journey_date}")
    for row_start in range(1, total + 1, 2):
        row_seats = [row_start, row_start + 1] if row_start + 1 <= total else [row_start]
        line = "  ".join(f"[{s:02d}]" for s in row_seats)
        print(" " + line)
    print("Available:", " ".join(f"{s:02d}" for s in sorted(available)) or "None")
    print("Booked   :", " ".join(f"{s:02d}" for s in sorted(booked)) or "None")

    waiting_here = waiting_list.find_all(lambda w: w["bus_id"] == bus_id and w["journey_date"] == journey_date)
    if waiting_here:
        print(f"Waiting list for this journey/date: {len(waiting_here)} passenger(s)")


def book_ticket():
    print("\n--- Book Ticket ---")
    try:
        name = input("Enter passenger name (or 'c' to cancel): ").strip()
        if name.lower() == "c" or not name:
            print("Booking cancelled." if name.lower() == "c" else "Name cannot be empty. Booking cancelled.")
            return

        age = prompt_int("Enter age: ", min_value=1, max_value=120)
        if age is None:
            print("Booking cancelled.")
            return

        bus_id = prompt_bus_id()
        if bus_id is None:
            print("Booking cancelled.")
            return

        journey_date = prompt_journey_date()
        if journey_date is None:
            print("Booking cancelled.")
            return

        available = get_available_seats(bus_id, journey_date)
        if not available:
            print(f"\nSorry, BUS {bus_id} is fully booked on {journey_date}.")
            join = input("Would you like to join the waiting list? (yes/no): ").strip().lower()
            if join == "yes":
                waiting_list.append({"name": name.title(), "age": age, "bus_id": bus_id, "journey_date": journey_date})
                save_data()
                print("Added to the waiting list. You'll be auto-booked if a seat opens up.")
            return

        print(f"Available seats on {journey_date}: {', '.join(f'{s:02d}' for s in available)}")
        seat_no = prompt_int("Select seat: ", min_value=1, max_value=BUSES[bus_id]["total_seats"])
        if seat_no is None:
            print("Booking cancelled.")
            return
        if seat_no not in available:
            print("That seat is already booked or invalid. Please try again.")
            return

        print("Processing booking...")
        base_fare = BUSES[bus_id]["fare"]
        fare = calculate_fare(base_fare, age)
        passenger = Passenger(name, age)
        booking_id = generate_booking_id()
        booking = Booking(booking_id, passenger, bus_id, journey_date, seat_no, fare)
        bookings.append(booking)
        save_data()

        print("\nBooking successful!")
        booking.display()

    except Exception as e:
        print(f"Unexpected error while booking: {e}")


def process_waiting_list(bus_id, journey_date):
    """
    Final-challenge behaviour: whenever seats free up on a bus/date,
    pull passengers from the FRONT of the waiting list (FIFO), assign
    freed seats in order, create bookings, and remove them from the
    waiting list - without disturbing the order of anyone left behind.
    """
    freed = get_available_seats(bus_id, journey_date)
    if not freed:
        return

    assigned_any = False
    for seat in freed:
        entry = waiting_list.remove_where(
            lambda w, b=bus_id, d=journey_date: w["bus_id"] == b and w["journey_date"] == d
        )
        if entry is None:
            break  # no more waiting passengers for this journey/date
        base_fare = BUSES[bus_id]["fare"]
        fare = calculate_fare(base_fare, entry["age"])
        passenger = Passenger(entry["name"], entry["age"])
        booking_id = generate_booking_id()
        new_booking = Booking(booking_id, passenger, bus_id, journey_date, seat, fare)
        bookings.append(new_booking)
        assigned_any = True
        print(f"Waiting list: seat {seat:02d} on {bus_id} ({journey_date}) auto-assigned to {entry['name']} "
              f"(Booking ID: {booking_id}).")

    if assigned_any:
        save_data()


def cancel_ticket():
    print("\n--- Cancel Ticket ---")
    booking_id = input("Enter Booking ID (or 'c' to cancel): ").strip().upper()
    if booking_id == "C":
        return

    node = bookings.find_node(lambda b: b.booking_id == booking_id)
    if node is None:
        print("Booking not found.")
        return

    booking = node.data
    if booking.status == "CANCELLED":
        print("This booking has already been cancelled.")
        return

    print(f"Booking found.\nPassenger: {booking.passenger.name}\n"
          f"Journey: {booking.bus_id} on {booking.journey_date}\nSeat: {booking.seat_no:02d}")
    confirm = input("Cancel booking? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancellation aborted.")
        return

    booking.status = "CANCELLED"
    save_data()
    print(f"Booking cancelled successfully.\nSeat {booking.seat_no:02d} is now available.")

    # Final-challenge behaviour: immediately try to fill the freed seat
    # from the waiting list for this exact bus/date.
    process_waiting_list(booking.bus_id, booking.journey_date)


def view_booking():
    print("\n--- View Booking ---")
    booking_id = input("Enter Booking ID: ").strip().upper()
    booking = bookings.find_node(lambda b: b.booking_id == booking_id)
    if booking is None:
        print("Booking not found.")
        return
    booking.data.display()


def search_passenger():
    print("\n--- Search Passenger / Booking ---")
    query = input("Enter passenger name or Booking ID: ").strip()
    if not query:
        print("Search term cannot be empty.")
        return
    query_lower = query.lower()

    results = bookings.find_all(
        lambda b: query_lower in b.passenger.name.lower() or query_lower == b.booking_id.lower()
    )
    if not results:
        print("No matching bookings found.")
        return

    print(f"\nSearch Results ({len(results)} found)")
    print("-" * 45)
    for b in results:
        print(f"Booking ID : {b.booking_id}")
        print(f"Passenger  : {b.passenger.name}")
        print(f"Journey    : {b.bus_id}  Date: {b.journey_date}")
        print(f"Seat       : {b.seat_no:02d}")
        print(f"Status     : {b.status}")
        print("-" * 45)


# ------------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------------
def main():
    init_db()
    load_data()
    print("Welcome to SwiftTravel Bus Reservation System!")
    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_buses()
        elif choice == "2":
            view_seats()
        elif choice == "3":
            book_ticket()
        elif choice == "4":
            cancel_ticket()
        elif choice == "5":
            view_booking()
        elif choice == "6":
            search_passenger()
        elif choice == "7":
            save_data()
            print("Thank you for using SwiftTravel. Safe travels!")
            break
        else:
            print("Invalid choice. Please select an option between 1 and 7.")


if __name__ == "__main__":
    main()
