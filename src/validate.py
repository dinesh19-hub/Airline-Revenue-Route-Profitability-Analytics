import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')

def run_validations():
    print("Loading data...")
    df_airports = pd.read_csv(os.path.join(DATA_DIR, 'Airports.csv'))
    df_routes = pd.read_csv(os.path.join(DATA_DIR, 'Routes.csv'))
    df_flights = pd.read_csv(os.path.join(DATA_DIR, 'Flights.csv'))
    df_customers = pd.read_csv(os.path.join(DATA_DIR, 'Customers.csv'))
    df_bookings = pd.read_csv(os.path.join(DATA_DIR, 'Bookings.csv'))

    df_flights['DepartureDateTime'] = pd.to_datetime(df_flights['DepartureDateTime'])
    df_bookings['BookingDateTime'] = pd.to_datetime(df_bookings['BookingDateTime'])

    results = []

    # 1. Referential integrity
    valid_fks = True
    if not df_bookings['FlightID'].isin(df_flights['FlightID']).all(): valid_fks = False
    if not df_bookings['CustomerID'].isin(df_customers['CustomerID']).all(): valid_fks = False
    if not df_flights['RouteID'].isin(df_routes['RouteID']).all(): valid_fks = False
    results.append(f"1. Referential Integrity: {'PASS' if valid_fks else 'FAIL'}")

    # 2. Booking dates before departure
    df_merged = df_bookings.merge(df_flights[['FlightID', 'DepartureDateTime']], on='FlightID')
    date_check = (df_merged['BookingDateTime'] < df_merged['DepartureDateTime']).all()
    results.append(f"2. Booking Dates < Departure: {'PASS' if date_check else 'FAIL'}")

    # 3. Valid cabin classes
    valid_cabins = df_bookings['CabinClass'].isin(['Economy', 'Business', 'First']).all()
    results.append(f"3. Valid Cabin Classes: {'PASS' if valid_cabins else 'FAIL'}")

    # 4. Capacity constraints (check non-cancelled bookings against capacity)
    active_bookings = df_bookings[~df_bookings['IsCancelled']].groupby('FlightID').size().reset_index(name='PassengerCount')
    cap_check_df = active_bookings.merge(df_flights[['FlightID', 'TotalCapacity']], on='FlightID')
    cap_check = (cap_check_df['PassengerCount'] <= cap_check_df['TotalCapacity']).all()
    results.append(f"4. Capacity Constraints: {'PASS' if cap_check else 'FAIL'}")

    # 5. Cancellation consistency
    cancelled_flights = df_flights[df_flights['FlightStatus'] == 'Cancelled']['FlightID']
    bookings_on_cancelled_flights = df_bookings[df_bookings['FlightID'].isin(cancelled_flights)]
    cancel_check = True
    if len(bookings_on_cancelled_flights) > 0 and not bookings_on_cancelled_flights['IsCancelled'].all():
        cancel_check = False
    results.append(f"5. Cancellation Consistency: {'PASS' if cancel_check else 'FAIL'}")

    # 6. Realistic price distributions
    price_check = True
    if df_bookings['TicketPrice'].min() <= 0: price_check = False
    avg_econ = df_bookings[df_bookings['CabinClass'] == 'Economy']['TicketPrice'].mean()
    avg_biz = df_bookings[df_bookings['CabinClass'] == 'Business']['TicketPrice'].mean()
    if avg_biz <= avg_econ: price_check = False
    results.append(f"6. Realistic Price Distributions: {'PASS' if price_check else 'FAIL'} (Avg Econ: ${avg_econ:.2f}, Avg Biz: ${avg_biz:.2f})")

    # Output results
    print("\n--- Validation Results ---")
    for r in results:
        print(r)
    
    print("\nData Summary:")
    print(f"Total Bookings: {len(df_bookings):,}")
    print(f"Total Flights: {len(df_flights):,}")
    active_rev = df_bookings[~df_bookings['IsCancelled']]['TicketPrice'].sum()
    print(f"Total Revenue (Non-cancelled): ${active_rev:,.2f}")

if __name__ == '__main__':
    run_validations()
