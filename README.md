
# 🚌 Bus Booking System – Python & MySQL

## 📌 Project Overview

The **Bus Booking System** is a console-based Python application developed to manage bus reservations, passenger bookings, seat allocation, cancellations, and waiting-list management.

The project combines **Python programming, Object-Oriented Programming (OOP), Data Structures, and MySQL database management** to create a practical bus reservation system.

The application allows users to view available buses, check seats, make bookings, cancel tickets, view booking details, and manage passengers through a waiting list.

---

## 🎯 Project Objective

The main objective of this project is to develop a reliable bus reservation system that handles common booking operations while demonstrating practical Python programming and database concepts.

The system is designed to handle:

* Bus and route information
* Passenger details
* Seat availability
* Ticket booking
* Booking cancellation
* Waiting-list management
* Fare calculation
* Booking dates
* Persistent database storage
* Input validation and error handling

---

## 🚍 Key Features

### 🚌 Bus Management

* View available buses
* View bus routes
* Display departure and arrival times
* Display total seats and ticket fares
* Support multiple bus routes

### 🎫 Ticket Booking

* Enter passenger name and age
* Select bus and journey date
* Select available seat
* Generate a unique booking ID
* Calculate and store ticket fare
* Confirm passenger booking

### 💺 Seat Management

* Display available seats
* Prevent booking of already occupied seats
* Release seats when a booking is cancelled
* Automatically allocate released seats to waiting passengers

### ❌ Ticket Cancellation

* Search booking using booking ID
* Cancel confirmed bookings
* Update booking status
* Release the booked seat

### ⏳ Waiting List

* Add passengers when seats are unavailable
* Maintain waiting-list order using a **FIFO approach**
* Automatically allocate available seats when cancellations occur
* Remove passengers from the waiting list after successful allocation

### 📅 Date-Based Booking

* Supports booking for the current day and upcoming days
* Booking window is limited to **8 days**
* Journey dates are stored and managed through MySQL

### 🗄️ MySQL Database

The project uses **MySQL** for persistent data storage.

Two main tables are used:

```text
bookings
waiting_list
```

The database stores passenger information, bus ID, journey date, seat number, fare, booking ID, and booking status.

---

## 🧑‍💻 Technologies Used

| Technology                 | Purpose                             |
| -------------------------- | ----------------------------------- |
| **Python**                 | Application development             |
| **MySQL**                  | Database and persistent storage     |
| **mysql-connector-python** | Python–MySQL connectivity           |
| **OOP**                    | Passenger and Booking models        |
| **Doubly Linked List**     | Booking and waiting-list management |
| **CSV**                    | Data import                         |
| **Exception Handling**     | Error and input management          |

---

## 🏗️ Python Concepts Implemented

This project demonstrates practical implementation of:

* Variables and Data Types
* Conditional Statements
* Loops
* Functions
* Lists and Dictionaries
* String Handling
* File Handling
* Exception Handling
* Classes and Objects
* Constructors
* Instance Variables
* Methods
* Static Methods
* Custom Data Structures
* MySQL Database Connectivity

---

## 🔗 Doubly Linked List

One of the main data structures implemented in this project is a **custom Doubly Linked List**.

The linked list is used to manage:

```text
Bookings
Waiting List
```

The implementation supports operations such as:

* Append
* Remove
* Search
* Find multiple records
* Ordered traversal
* Length calculation

The waiting list follows a **FIFO (First In, First Out)** approach so that passengers are processed according to their waiting order.

---

## 🏛️ Object-Oriented Programming

The application uses OOP to represent passengers and bookings.

### Passenger Class

```python
class Passenger:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

### Booking Class

```python
class Booking:
    def __init__(self, booking_id, passenger, bus_id,
                 journey_date, seat_no, fare, status):
        self.booking_id = booking_id
        self.passenger = passenger
        self.bus_id = bus_id
        self.journey_date = journey_date
        self.seat_no = seat_no
        self.fare = fare
        self.status = status
```

This structure makes the application easier to organize and maintain.

---

## 🚌 Available Bus Routes

The current project includes multiple bus routes:

| Bus ID | Route            | Departure | Arrival  | Seats | Fare |
| ------ | ---------------- | --------- | -------- | ----: | ---: |
| P101   | Pune → Mumbai    | 08:00 AM  | 12:00 PM |    10 | ₹250 |
| P102   | Pune → Nashik    | 09:30 AM  | 01:00 PM |    12 | ₹450 |
| P103   | Pune → Burhanpur | 08:00 AM  | 10:00 PM |    10 | ₹750 |
| P104   | Pune → Jalgaon   | 09:30 AM  | 08:00 PM |    12 | ₹650 |
| P105   | Pune → Bhusawal  | 08:00 AM  | 06:00 PM |    10 | ₹550 |
| P106   | Pune → Surat     | 05:30 AM  | 01:00 PM |    12 | ₹750 |

---

## 🗃️ MySQL Database Design

The application automatically creates the required database and tables if they do not already exist.

### Database

```text
swifttravel
```

### Bookings Table

```text
booking_id
name
age
bus_id
journey_date
seat_no
fare
status
```

### Waiting List Table

```text
id
name
age
bus_id
journey_date
```

The `schema.sql` file is also included for users who prefer to create the database manually.

---

## 🔄 Booking Workflow

```text
Start Application
       ↓
Connect to MySQL
       ↓
Load Booking Data
       ↓
Display Main Menu
       ↓
Select Operation
       ↓
 ┌───────────────────────┐
 │ View Buses            │
 │ View Seats            │
 │ Book Ticket           │
 │ Cancel Ticket         │
 │ View Booking          │
 │ Search Booking        │
 │ Manage Waiting List   │
 └───────────────────────┘
       ↓
Update Data
       ↓
Save Changes to MySQL
```

---

## 🔄 Waiting List Workflow

When all seats are occupied:

```text
Passenger Requests Booking
          ↓
No Seat Available
          ↓
Add Passenger to Waiting List
          ↓
Passenger Waits in FIFO Order
          ↓
Existing Passenger Cancels
          ↓
Seat Becomes Available
          ↓
First Waiting Passenger Gets Seat
          ↓
Booking Confirmed
```

This helps maintain an organized and fair waiting-list process.

---

## 📥 CSV to MySQL Import

The project also contains:

```text
import_csv_to_mysql.py
```

This script allows existing CSV booking data to be imported into MySQL.

Example:

```bash
python import_csv_to_mysql.py
```

A custom CSV file can also be provided:

```bash
python import_csv_to_mysql.py docs/sample_bookings.csv
```

The import process supports date formats such as:

```text
YYYY-MM-DD
DD-MM-YYYY
```

---

## 📂 Project Structure

```text
BUS Booking System/
│
├── main.py
├── bookings.csv
├── requirements.txt
├── schema.sql
├── import_csv_to_mysql.py
│
└── docs/
    ├── sample_bookings.csv
    ├── PROBLEM_STATEMENT.pdf
    ├── Reselt.pdf
    └── screenshots/
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/PraptiSolanke2004/Python-Bus-Booking-system.git
```

### 2. Open the Project

```bash
cd Python-Bus-Booking-system
```

### 3. Install Required Python Package

```bash
pip install -r requirements.txt
```

The project requires:

```text
mysql-connector-python
```

### 4. Start MySQL

Make sure your MySQL server is running.

### 5. Run the Application

```bash
python main.py
```

The application can create the required database and tables automatically.

---

## 🔐 Database Configuration

The project uses the following MySQL configuration:

```text
Host: localhost
User: root
Database: swifttravel
```

The MySQL password can be provided when the application starts or through the environment variable:

```text
DB_PASSWORD
```

Other supported environment variables include:

```text
DB_HOST
DB_USER
DB_NAME
DB_PASSWORD
```

---

## 📊 Sample Booking Data

The project includes sample booking records containing:

* Booking ID
* Passenger name
* Passenger age
* Bus ID
* Journey date
* Seat number
* Fare
* Booking status

Example statuses include:

```text
CONFIRMED
CANCELLED
```

---

## 🛡️ Exception Handling & Validation

The application includes error handling for common MySQL and user-input problems.

Examples include:

* Invalid MySQL username/password
* MySQL server unavailable
* Database unavailable
* Invalid input
* Invalid booking information
* Invalid seat selection

The system provides user-friendly error messages and prevents unexpected application crashes.

---

## 🎓 Learning Outcomes

Through this project, I strengthened my practical knowledge of:

* **Python Programming**
* **Object-Oriented Programming**
* **Data Structures**
* **Doubly Linked Lists**
* **MySQL Database Management**
* **Python–MySQL Connectivity**
* **CRUD Operations**
* **Exception Handling**
* **Input Validation**
* **CSV Data Import**
* **Problem Solving**
* **Real-world Application Development**

---

## 🚀 Future Enhancements

Possible future improvements include:

* GUI-based interface
* Web-based booking system
* Online payment integration
* Admin dashboard
* User authentication
* Email/SMS booking confirmation
* Advanced bus and route management
* Online seat map
* Reports and analytics dashboard

---

## 👩‍💻 Author

**Prapti Solanke**

B.Tech Computer Engineering Student

**Interests:** Python | Data Analytics | Data Science | Machine Learning | Software Development

This version is **specifically aligned with the code and files in your uploaded ZIP**, including the MySQL database, `DoublyLinkedList`, `Passenger`/`Booking` classes, waiting list, CSV import, and 8-day booking window.
