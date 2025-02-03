import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Function to connect to the database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="digimini",
            database="AirlineReservatorySystem",
        )
        return connection
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None


# Fetch flights using FlightScheduleView from the database
def fetch_flight_schedule():
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM FlightScheduleView;"
            cursor.execute(query)
            flight_data = cursor.fetchall()
            cursor.close()
            connection.close()
            return flight_data
        except Error as e:
            st.error(f"Error fetching flight schedule: {e}")
            return None

# Function to fetch flights 
def fetch_flights(departure, arrival, date):
    connection = create_connection()
    if connection:
        try:
            query = """
            SELECT Flight_ID, Flight_No, Departure_City, Arrival_City, Departure_Time, Arrival_Time, Available_Seats
            FROM Flight
            WHERE Departure_City = %s AND Arrival_City = %s AND DATE(Departure_Time) = %s
            """
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (departure, arrival, date))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Error as e:
            st.error(f"Error fetching flights: {e}")
            return []

def generate_passenger_id(cursor):
    # Query the last Passenger_ID from the Passengers table
    cursor.execute("SELECT Passenger_ID FROM Passengers ORDER BY Passenger_ID DESC LIMIT 1")
    last_passenger_id = cursor.fetchone()
    
    if last_passenger_id:
        last_passenger_id = last_passenger_id[0]
        
        # Try to match the format 'PassXXX' or any similar format (like 's018')
        match = re.match(r'([a-zA-Z]+)(\d+)', last_passenger_id)
        
        if match:
            prefix = match.group(1)  # The non-numeric part (e.g., 'Pass', 's', etc.)
            numeric_part = int(match.group(2))  # The numeric part
            
            # Generate next Passenger_ID with incremented number
            next_passenger_id = f"{prefix}{numeric_part + 1:03d}"
        else:
            # If the format doesn't match, start from 'Pass001'
            next_passenger_id = "Pass001"
    else:
        # If no passengers exist, start from 'Pass001'
        next_passenger_id = "Pass001"
    
    return next_passenger_id

def add_passenger(passenger_id,first_name, last_name, passport_no, email, seat_no, class_type, departure, flight_id, country="India"):
    # Define a dictionary mapping cities to airport codes
    city_to_airport_code = {
        "Mumbai": "BOM",
        "Delhi": "DEL",
        "New York": "JFK",
        "London": "LHR",
        # Add other cities and airport codes here
    }

    # Fetch airport code based on departure city, default to "DEL" if not found
    airport_code = city_to_airport_code.get(departure, "DEL")

    connection = create_connection()
    if connection:
        try:
            # Validate inputs
            if not isinstance(first_name, str) or not first_name:
                st.error("First name must be a non-empty string.")
                return None
            if not isinstance(last_name, str) or not last_name:
                st.error("Last name must be a non-empty string.")
                return None
            if not isinstance(passport_no, str) or not passport_no:
                st.error("Passport number must be a non-empty string.")
                return None
            if not isinstance(email, str) or "@" not in email:
                st.error("Invalid email.")
                return None
            if not isinstance(seat_no, str) or not seat_no:
                st.error("Seat number must be a non-empty string.")
                return None
            if class_type not in ["Economy", "Business", "First Class"]:
                st.error("Invalid class type.")
                return None

            #Insert the new passenger into the database
            query = """
            INSERT INTO Passengers (passenger_id,First_Name, Last_Name, Passport_No, Email, Country, Last_Updated)
            VALUES (%s,%s, %s, %s, %s, %s, NOW())
            """
            cursor = connection.cursor()

            cursor.execute(query, (passenger_id,first_name, last_name, passport_no, email, country))
            

            
            # Insert into Booking table
            booking_query = """
            INSERT INTO Booking (Passenger_ID, flight_id, class_type, Seat_No, booking_date, booking_status, payment_status, Airport_Code)
            VALUES (%s, %s, %s, %s, NOW(), 'Confirmed', 'Paid', %s)
            """
            cursor.execute(booking_query, (passenger_id, flight_id, class_type, seat_no,airport_code))

            # Update available seats in Flights table
            query_update = "UPDATE Flight SET Available_Seats = Available_Seats - 1 WHERE flight_id = %s"
            cursor.execute(query_update, (flight_id,))

            connection.commit()
            cursor.close()
            connection.close()
            return passenger_id
        except Error as e:
            st.error(f"Error adding passenger: {e}")
            return None

# Function to book a flight
def book_flight(flight_id, passenger_id, class_type, seat_no, payment_status="Paid", booking_status="Confirmed"):
    connection = create_connection()
    if connection:
        try:
            # Validate flight availability
            query_check = "SELECT Available_Seats FROM Flight WHERE flight_id = %s"
            cursor = connection.cursor()
            cursor.execute(query_check, (flight_id,))
            result = cursor.fetchone()
            if not result or result[0] <= 0:
                st.error("No available seats for this flight.")
                return
            
            # Insert booking into Booking table
            query = """
            INSERT INTO Booking (flight_id, Passenger_ID, booking_Date, class_type, Seat_No, payment_status, booking_status, Airport_Code)
            VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)
            """
            # Assuming a dummy airport code for simplicity
            # airport_code = "XYZ123"
            #cursor.execute(query, (flight_id, passenger_id, class_type, seat_no, payment_status, booking_status))
            
            # Update available seats in Flights table
            query_update = "UPDATE Flight SET Available_Seats = Available_Seats - 1 WHERE flight_id = %s"
            cursor.execute(query_update, (flight_id,))
            
            connection.commit()
            cursor.close()
            connection.close()
            #st.success("Booking successful!")
        except Error as e:
            st.error(f"Error booking flight: {e}")

# Function to fetch bookings using stored procedure
def fetch_my_bookings(passenger_id):
    connection = create_connection()
    if connection:
        try:
            query = "CALL MYBooking(%s)"
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (passenger_id,))
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Error as e:
            st.error(f"Error fetching bookings: {e}")
            return []
        
def fetch_booking_ID(passenger_id):
    """
    Fetches booking IDs for a given passenger_id.
    """
    connection = create_connection()
    if connection:
        try:
            query = "SELECT Booking_ID FROM Booking WHERE Passenger_ID = %s"
            cursor = connection.cursor()
            cursor.execute(query, (passenger_id,))
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            return [row[0] for row in result]  # Extract Booking_IDs
        except Error as e:
            st.error(f"Error fetching bookings: {e}")
            return []

def cancel_booking(booking_id):
    connection = create_connection()
    if connection:
        try:
            query = "CALL CancelBooking(%s)"
            cursor = connection.cursor()
            cursor.execute(query, (int(booking_id),))  # Ensure booking_id is passed as an integer
            connection.commit()
            cursor.close()
            connection.close()
            st.success(f"Booking  has been cancelled successfully.")
        except Error as e:
            st.error(f"Error canceling booking: {e}")

# Function to fetch the last Passenger_ID from the database
def fetch_last_passenger_id():
    connection = create_connection()  # Create a new connection
    if connection:
        cursor = connection.cursor()  # Get a cursor object
        cursor.execute("SELECT Passenger_ID FROM passengers ORDER BY Passenger_ID DESC LIMIT 1")
        result = cursor.fetchone()  # Fetch the last record
        cursor.close()  # Close the cursor
        connection.close()  # Close the connection

        if result:
            return result[0]  # Return the last Passenger_ID
        else:
            return None  # If no results found, return None
    return None  # If the connection fails, return None

# Function to generate a new Passenger ID
def get_new_passenger_id():
    last_passenger_id = fetch_last_passenger_id()
    if last_passenger_id:
        last_number = int(last_passenger_id[4:])  # Extract the numeric part (e.g., Pass001 -> 1)
        new_passenger_id = f"Pass{last_number + 1:03d}"  # Increment the number part (e.g., Pass002)
    else:
        # If no previous passenger IDs exist, start from Pass001
        new_passenger_id = "Pass001"
    return new_passenger_id


# Initialize session state
if "selected_flight" not in st.session_state:
    st.session_state.selected_flight = None

if "flights" not in st.session_state:
    st.session_state.flights = []


##### Streamlit app #####
st.title("✈️ Airline Reservation System")
st.sidebar.title("Navigation")
options = {
    "Home": "Home",
    "Search Flights": "Search Flights",
    "Book Flight": "Book Flight",
    "My Bookings": "My Bookings",
}
selection = st.sidebar.radio("Choose a section:", options.keys(), format_func=lambda x: options[x])
# Footer
st.sidebar.markdown("---")
st.sidebar.caption("© 2024 Airline Reservation System")


# Home Page
if selection == "Home":
    #st.header("🏠 Home - Available Flights")
    st.header("Home - Available Flights")
    flights = fetch_flight_schedule()
    if flights:
        st.write("### Current Flights")
        df = pd.DataFrame(flights)
        st.table(df)
    else:
        st.warning("No flights available.")


# Search Flights Page
elif selection == "Search Flights":
    st.write("")  # Blank lines for spacing
    #st.write("###  Search Flights")
    st.markdown("<h1 style='text-align: center; font-size: 36px; font-weight: 300;'>Search Flights</h1>", unsafe_allow_html=True)
    st.write("")  # Blank lines for spacing

    # Dropdown options for cities
    cities = ["Mumbai", "Delhi", "Chennai","Bangalore","Kolkata"]
    # Input fields for search criteria
    col1, col2, col3 = st.columns(3)

    with col1:
        departure = st.selectbox("Departure City", options=cities, key="departure_city")
    with col2:
        arrival = st.selectbox("Arrival City", options=cities, key="arrival_city")
    with col3:
        date = st.date_input("Travel Date")

    # Fetch and display available flights
    if st.button("Search Flights"):
        if departure == arrival:
            st.warning("Departure and Arrival cities cannot be the same.")
        else:
            st.session_state.flights = fetch_flights(departure, arrival, str(date))
            st.session_state.selected_flight = None  # Reset selected flight

    # Display search results if flights exist
    if st.session_state.get("flights"):
        st.write("### Available Flights")
        df = pd.DataFrame(st.session_state.flights)

        # Sort and display flights
        sort_by = st.selectbox("Sort by", ["Departure Time", "Available Seats"], key="sort_by")
        if sort_by == "Departure Time":
            df = df.sort_values(by="Departure_Time")
        elif sort_by == "Available Seats":
            df = df.sort_values(by="Available_Seats", ascending=False)

        st.dataframe(df, use_container_width=True, height=400)

        # Flight selection and booking
        for flight in st.session_state.flights:
            st.write(f"Flight ID: {flight['Flight_ID']} | {flight['Departure_City']} -> {flight['Arrival_City']} | Departure: {flight['Departure_Time']} | Seats Available: {flight['Available_Seats']}")
            if st.button(f"Book Flight {flight['Flight_ID']}", key=f"book_{flight['Flight_ID']}"):
                st.session_state.selected_flight = flight['Flight_ID']

    # Booking form for the selected flight
    if st.session_state.get("selected_flight"):
        st.write(f"### Booking Details for Flight ID: {st.session_state.selected_flight}")

        # # Booking form
        # with st.form("booking_form"):
        #     passenger_id = st.text_input("Passenger ID", key="passenger_id")
        #     first_name = st.text_input("First Name", key="first_name")
        #     last_name = st.text_input("Last Name", key="last_name")
        #     passport_no = st.text_input("Passport Number", key="passport_no")
        #     email = st.text_input("Email", key="email")
        #     seat_no = st.text_input("Seat Number", key="seat_no")
        #     class_type = st.selectbox("Class Type", ["Economy", "Business", "First Class"], key="class_type")
        #     submit_button = st.form_submit_button("Confirm Booking")

        #     if submit_button:
        #         # Ensure all fields are filled
        #         if first_name and last_name and passport_no and email and seat_no and class_type:
        #             # Add passenger and book flight
        #             passenger_added = add_passenger(
        #                 passenger_id, first_name, last_name, passport_no, email, seat_no, class_type, departure, st.session_state.selected_flight
        #             )
        #             if passenger_added:
        #                 success = book_flight(st.session_state.selected_flight, passenger_id, class_type, seat_no)
        #                 if success:
        #                     st.success("Booking Confirmed!")
        #                     st.session_state.selected_flight = None  # Reset after successful booking
        #                 else:
        #                     st.error("Failed to book the flight. Please try again.")
        #             else:
        #                 st.error("Failed to add passenger details. Please try again.")
        #         else:
        #             st.warning("Please fill in all the details.")
        # After selecting a flight, prompt user for booking details
        if st.session_state.selected_flight:
            st.write("#### Passenger Information")
            
            # Generate a new Passenger ID
            new_passenger_id = get_new_passenger_id()  # Generate new Passenger ID
            st.write(f"Your Passenger ID: {new_passenger_id}")  # Display the generated Passenger ID
            
            # Other booking details
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            passport_no = st.text_input("Passport Number")
            email = st.text_input("Email")
            seat_no = st.text_input("Seat Number")
            class_type = st.selectbox("Class Type", ["Economy", "Business", "First Class"])
            
            if st.button("Confirm Booking"):
                if first_name and last_name and passport_no and email and seat_no and class_type:
                    # Add passenger to the database
                    passenger_id = add_passenger(new_passenger_id, first_name, last_name, passport_no, email, seat_no, class_type, departure, st.session_state.selected_flight)
                    if passenger_id:
                        # Book the flight for the passenger
                        book_flight(st.session_state.selected_flight, passenger_id, class_type, seat_no)
                        st.success(f"Booking successful! Your Passenger ID is {new_passenger_id}")
                    else:
                        st.error("Failed to add passenger details. Please try again.")
                else:
                    st.warning("Please fill in all the details.")

# My Bookings Section
elif selection == "My Bookings":
    st.write("")  # This creates a blank line
    st.write("")  # This creates a blank line
    st.markdown("<h1 style='text-align: center; font-size: 36px; font-weight: 300;'>📋 My Bookings</h1>", unsafe_allow_html=True)

    # Input Passenger ID
    passenger_id = st.text_input("Enter your Passenger ID")

    # Save passenger_id in session state
    if passenger_id and "passenger_id" not in st.session_state:
        st.session_state["passenger_id"] = passenger_id

    if st.session_state.get("passenger_id"):
        # Step 1: Fetch bookings for the passenger
        bookings = fetch_my_bookings(st.session_state["passenger_id"])

        if bookings:
            st.write("### Your Booked Tickets")
            df = pd.DataFrame(bookings)

            # Display dataframe
            st.dataframe(
                df,
                use_container_width=True,  # Adjust width
                height=600  # Increase table height
            )

            # Step 2: Fetch Booking IDs
            booking_ids = fetch_booking_ID(st.session_state["passenger_id"])

            if booking_ids:
                st.write("### Cancel Your Booking")
                
                # Save booking_ids in session state
                if "booking_ids" not in st.session_state:
                    st.session_state["booking_ids"] = booking_ids

                # Step 3: Display cancel booking buttons for each booking ID
                for booking_id in st.session_state["booking_ids"]:
                    if st.button(f"Cancel Booking"):
                        cancel_booking(booking_id)  # Call the cancel booking function
                        st.session_state.selected_booking_id = booking_id  # Save the cancelled booking ID to session state
            else:
                st.warning("No bookings found for the given Passenger ID.")
        else:
            st.warning("No bookings found.")
    else:
        st.warning("Please enter your Passenger ID.")

# Book Flight Page
elif selection == "Book Flight":
    st.write("")  # This creates a blank line
    st.write("")  # This creates a blank line
    #st.write("✈️ Book a Flight")
    st.markdown("<h1 style='text-align: center; font-size: 36px; font-weight: 300;'>Book a Flight</h1>", unsafe_allow_html=True)
    st.write("")  # Blank lines for spacing
    
    # Dropdown options for cities
    cities = ["Mumbai", "Delhi", "Chennai","Bangalore","Kolkata"]

    # Input fields for search criteria
    col1, col2, col3 = st.columns(3)

    with col1:
        departure = st.selectbox("Departure City", options=cities, key="departure_city")
    with col2:
        arrival = st.selectbox("Arrival City", options=cities, key="arrival_city")
    with col3:
        date = st.date_input("Travel Date")

    if st.button("Search Flights"):
        st.session_state.flights = fetch_flights(departure, arrival, str(date))
        st.session_state.selected_flight = None  # Reset selected flight

    if st.session_state.flights:
        st.write("### Available Flights")
        df = pd.DataFrame(st.session_state.flights)
        st.dataframe(
            df,
            use_container_width=True,  # Adjust width
            height=600  # Increase table height
        )

        # Select a flight to book
        selected_flight = st.radio(
            "Select a flight to book:",
            options=[f['Flight_ID'] for f in st.session_state.flights],
            format_func=lambda x: f"Flight {x}"
        )
        st.session_state.selected_flight = selected_flight

    # After selecting a flight, prompt user for booking details
    if st.session_state.selected_flight:
        st.write("#### Passenger Information")
        
        # Generate a new Passenger ID
        new_passenger_id = get_new_passenger_id()  # Generate new Passenger ID
        st.write(f"Your Passenger ID: {new_passenger_id}")  # Display the generated Passenger ID
        
        # Other booking details
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        passport_no = st.text_input("Passport Number")
        email = st.text_input("Email")
        seat_no = st.text_input("Seat Number")
        class_type = st.selectbox("Class Type", ["Economy", "Business", "First Class"])
        
        if st.button("Confirm Booking"):
            if first_name and last_name and passport_no and email and seat_no and class_type:
                # Add passenger to the database
                passenger_id = add_passenger(new_passenger_id, first_name, last_name, passport_no, email, seat_no, class_type, departure, st.session_state.selected_flight)
                if passenger_id:
                    # Book the flight for the passenger
                    book_flight(st.session_state.selected_flight, passenger_id, class_type, seat_no)
                    st.success(f"Booking successful! Your Passenger ID is {new_passenger_id}")
                else:
                    st.error("Failed to add passenger details. Please try again.")
            else:
                st.warning("Please fill in all the details.")



