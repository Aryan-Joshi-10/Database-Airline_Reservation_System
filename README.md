# Airline Reservatory System

## 📌 Project Overview
The **Airline Reservation System** is a database management project designed to facilitate flight scheduling, ticket booking, and cancellation. Built using **Streamlit (Python)** as the frontend and **MySQL** as the backend, this project demonstrates how to manage airline data efficiently. It is our first hands-on experience with **SQL queries, stored procedures, triggers, and views**, which play a crucial role in handling and optimizing database operations.

## ✈️ Features
- **View Flight Schedules**: Users can browse available flights with departure and arrival details.
- **Search & Book Tickets**: Users can search for flights based on their preferences and book tickets.
- **Cancel Tickets**: Provides an option to cancel booked tickets.
- **User-Friendly Interface**: Developed using **Streamlit** for an interactive and seamless experience.

## 🛠️ Technologies Used
- **Frontend**: Streamlit (Python)
- **Backend**: MySQL
- **Database Connector**: MySQL Connector for Python
- **SQL Features**: Queries, Stored Procedures, Triggers, Views

## 🗂️ Database Schema
Our database consists of the following six tables:
1. **Flights**: Stores flight details such as flight_ID, departure, and arrival.
2. **Bookings**: Records all ticket reservations.
3. **Passengers**: Maintains passenger details.
4. **Airline**: Information about different airlines.
5. **Airport**: Stores data of various airports.
6. **Aircraft**: Contains aircraft specifications.

## 🚀 How to Run the Project
### Prerequisites
- Install **Python 3.x**
- Install required libraries:
  ```bash
  pip install streamlit mysql-connector-python
  ```
- Set up a **MySQL database** and import the required schema.

### Running the Application
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/airline-reservation-system.git
   ```
2. Navigate to the project folder:
   ```bash
   cd airline-reservation-system
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## 📷 Screenshots
*(Add screenshots of the Streamlit UI showing the booking process, flight schedules, etc.)*


## 🤝 Contributors
- **Aryan Joshi**
- **Mithil Jatkar**
- **Akshat Gandhi**

## 📜 License
This project is licensed under the MIT License.

---
Feel free to contribute, suggest improvements, or raise issues. Happy coding! 🚀


