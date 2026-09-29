-- Optional: main.py runs init_db() and creates all of this automatically.
-- Use this file only if you prefer to set up the database by hand:
--     mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS swifttravel;
USE swifttravel;

CREATE TABLE IF NOT EXISTS bookings (
    booking_id   VARCHAR(10)  PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    age          INT          NOT NULL,
    bus_id       VARCHAR(10)  NOT NULL,
    journey_date DATE         NOT NULL,
    seat_no      INT          NOT NULL,
    fare         DECIMAL(8,2) NOT NULL,
    status       VARCHAR(15)  NOT NULL
);

-- AUTO_INCREMENT id keeps the FIFO order of the waiting list
CREATE TABLE IF NOT EXISTS waiting_list (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    age          INT          NOT NULL,
    bus_id       VARCHAR(10)  NOT NULL,
    journey_date DATE         NOT NULL
);
