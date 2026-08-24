import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
os.makedirs(DATA_DIR, exist_ok=True)

# 1. Generate Airports
airports_data = [
    ('JFK', 'New York', 'USA', 'North America', True),
    ('LAX', 'Los Angeles', 'USA', 'North America', True),
    ('ORD', 'Chicago', 'USA', 'North America', True),
    ('ATL', 'Atlanta', 'USA', 'North America', True),
    ('DFW', 'Dallas', 'USA', 'North America', True),
    ('SFO', 'San Francisco', 'USA', 'North America', False),
    ('MIA', 'Miami', 'USA', 'North America', False),
    ('SEA', 'Seattle', 'USA', 'North America', False),
    ('BOS', 'Boston', 'USA', 'North America', False),
    ('DEN', 'Denver', 'USA', 'North America', False)
]
df_airports = pd.DataFrame(airports_data, columns=['AirportCode', 'City', 'Country', 'Region', 'HubStatus'])
df_airports.to_csv(os.path.join(DATA_DIR, 'Airports.csv'), index=False)
print("Airports generated.")

# 2. Generate Routes
routes_data = [
    ('R001', 'JFK', 'LAX', 2475, 15000),
    ('R002', 'LAX', 'JFK', 2475, 15000),
    ('R003', 'ORD', 'SFO', 1846, 12000),
    ('R004', 'SFO', 'ORD', 1846, 12000),
    ('R005', 'ATL', 'MIA', 594, 5000),
    ('R006', 'MIA', 'ATL', 594, 5000),
    ('R007', 'DFW', 'DEN', 641, 5500),
    ('R008', 'DEN', 'DFW', 641, 5500),
    ('R009', 'JFK', 'BOS', 187, 3000),
    ('R010', 'BOS', 'JFK', 187, 3000),
]
df_routes = pd.DataFrame(routes_data, columns=['RouteID', 'OriginAirport', 'DestAirport', 'DistanceMiles', 'BaseOperatingCost'])
df_routes.to_csv(os.path.join(DATA_DIR, 'Routes.csv'), index=False)
print("Routes generated.")

# 3. Generate Customers
num_customers = 50000
customer_ids = [f'C{str(i).zfill(5)}' for i in range(1, num_customers + 1)]
ages = np.random.normal(loc=40, scale=15, size=num_customers).clip(18, 90).astype(int)
genders = np.random.choice(['M', 'F', 'Other'], size=num_customers, p=[0.48, 0.48, 0.04])
loyalty_tiers = np.random.choice(['None', 'Silver', 'Gold', 'Platinum'], size=num_customers, p=[0.60, 0.20, 0.15, 0.05])
passenger_types = np.random.choice(['Business', 'Leisure'], size=num_customers, p=[0.35, 0.65])

df_customers = pd.DataFrame({
    'CustomerID': customer_ids,
    'Age': ages,
    'Gender': genders,
    'LoyaltyTier': loyalty_tiers,
    'PassengerType': passenger_types
})
df_customers.to_csv(os.path.join(DATA_DIR, 'Customers.csv'), index=False)
print("Customers generated.")

# 4. Generate Flights
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
flights_data = []

flight_id_counter = 1
for current_date in pd.date_range(start=start_date, end=end_date):
    for _, route in df_routes.iterrows():
        # 1 or 2 flights per route per day
        num_flights_today = random.choice([1, 2])
        for _ in range(num_flights_today):
            flight_id = f'F{str(flight_id_counter).zfill(6)}'
            
            # Determine departure time (random hour between 6 AM and 10 PM)
            dep_hour = random.randint(6, 22)
            dep_minute = random.choice([0, 15, 30, 45])
            dep_datetime = current_date.replace(hour=dep_hour, minute=dep_minute)
            
            aircraft = random.choice(['Boeing 737', 'Airbus A320'])
            capacity = 160 if aircraft == 'Boeing 737' else 180
            
            status = np.random.choice(['Completed', 'Delayed', 'Cancelled'], p=[0.93, 0.05, 0.02])
            
            # Costs based on distance + randomness
            dist = route['DistanceMiles']
            fuel_cost = round((dist * 5.5) * random.uniform(0.9, 1.1), 2)
            crew_cost = round((dist * 2.0) * random.uniform(0.95, 1.05), 2)
            airport_cost = round(random.uniform(1500, 3000), 2)
            other_cost = round(random.uniform(500, 1500), 2)
            
            flights_data.append({
                'FlightID': flight_id,
                'RouteID': route['RouteID'],
                'DepartureDateTime': dep_datetime,
                'AircraftType': aircraft,
                'TotalCapacity': capacity,
                'FlightStatus': status,
                'FuelCost': fuel_cost,
                'CrewCost': crew_cost,
                'AirportCost': airport_cost,
                'OtherOperatingCost': other_cost
            })
            flight_id_counter += 1

df_flights = pd.DataFrame(flights_data)
df_flights.to_csv(os.path.join(DATA_DIR, 'Flights.csv'), index=False)
print(f"Flights generated: {len(df_flights)}")

# 5. Generate Bookings
bookings_data = []
booking_id_counter = 1

# Pre-filter customers for faster sampling
business_customers = df_customers[df_customers['PassengerType'] == 'Business']['CustomerID'].values
leisure_customers = df_customers[df_customers['PassengerType'] == 'Leisure']['CustomerID'].values
business_customers_set = set(business_customers)

for idx, flight in df_flights.iterrows():
    if idx % 500 == 0:
        print(f"Generating bookings for flight {idx}/{len(df_flights)}...")
    # Base load factor around 70-95%
    base_lf = random.uniform(0.7, 0.95)
    
    # Seasonality (summer and december are higher)
    month = flight['DepartureDateTime'].month
    if month in [6, 7, 8, 12]:
        base_lf = min(0.98, base_lf + 0.1)
        
    num_pax = int(flight['TotalCapacity'] * base_lf)
    
    flight_is_cancelled = flight['FlightStatus'] == 'Cancelled'
    dist = df_routes[df_routes['RouteID'] == flight['RouteID']]['DistanceMiles'].values[0]
    base_price = max(100, dist * 0.15)
    
    # Pick customers (mix of business and leisure)
    biz_count = int(num_pax * 0.35)
    lei_count = num_pax - biz_count
    
    pax_biz = np.random.choice(business_customers, biz_count, replace=False)
    pax_lei = np.random.choice(leisure_customers, lei_count, replace=False)
    
    flight_customers = list(pax_biz) + list(pax_lei)
    random.shuffle(flight_customers)
    
    for customer_id in flight_customers:
        booking_id = f'B{str(booking_id_counter).zfill(7)}'
        
        is_business_pax = (customer_id in business_customers_set)
        
        # Booking curve logic
        if is_business_pax:
            # Business books 0-14 days in advance
            days_advance = random.randint(0, 14)
            cabin = np.random.choice(['Economy', 'Business', 'First'], p=[0.4, 0.5, 0.1])
        else:
            # Leisure books 14-90 days in advance
            days_advance = random.randint(14, 90)
            cabin = np.random.choice(['Economy', 'Business', 'First'], p=[0.9, 0.08, 0.02])
            
        booking_dt = flight['DepartureDateTime'] - timedelta(days=days_advance)
        # Randomize time of booking
        booking_dt = booking_dt.replace(hour=random.randint(0,23), minute=random.randint(0,59))
        
        # Ensure booking date is strictly before departure
        if booking_dt >= flight['DepartureDateTime']:
            booking_dt = flight['DepartureDateTime'] - timedelta(hours=random.randint(1, 12), minutes=random.randint(0, 59))
        
        # Price multiplier based on time
        time_multiplier = 1.0
        if days_advance <= 3:
            time_multiplier = 1.8
        elif days_advance <= 14:
            time_multiplier = 1.4
        elif days_advance <= 30:
            time_multiplier = 1.1
            
        cabin_multiplier = 1.0
        if cabin == 'Business': cabin_multiplier = 2.5
        if cabin == 'First': cabin_multiplier = 4.0
        
        ticket_price = round(base_price * time_multiplier * cabin_multiplier * random.uniform(0.9, 1.1), 2)
        
        # Ancillary Revenue
        ancillary = 0
        if cabin == 'Economy':
            # Economy pax might pay for bags/meals
            ancillary = round(np.random.choice([0, 35, 70, 105], p=[0.4, 0.3, 0.2, 0.1]), 2)
            
        # Cancellations
        if flight_is_cancelled:
            is_cancelled = True
        else:
            # Random individual cancellation
            is_cancelled = np.random.choice([True, False], p=[0.03, 0.97])
            
        bookings_data.append({
            'BookingID': booking_id,
            'FlightID': flight['FlightID'],
            'CustomerID': customer_id,
            'BookingDateTime': booking_dt,
            'CabinClass': cabin,
            'TicketPrice': ticket_price,
            'AncillaryRevenue': ancillary,
            'IsCancelled': is_cancelled
        })
        booking_id_counter += 1

df_bookings = pd.DataFrame(bookings_data)
df_bookings.to_csv(os.path.join(DATA_DIR, 'Bookings.csv'), index=False)
print(f"Bookings generated: {len(df_bookings)}")
