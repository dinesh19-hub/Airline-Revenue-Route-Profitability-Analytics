import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import warnings
warnings.filterwarnings('ignore')

def export_powerbi_data():
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'airline_analytics')

    encoded_pwd = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    auth = f"{DB_USER}:{encoded_pwd}" if encoded_pwd else f"{DB_USER}"
    conn_str = f"mysql+pymysql://{auth}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_str)
    
    print("Exporting data for Power BI...")
    
    # We will create two main tables for Power BI (Star Schema)
    # 1. Fact Bookings (grain: passenger booking)
    # 2. Fact Flights (grain: individual flight)
    
    query_fact_flights = """
    SELECT 
        f.FlightID,
        f.RouteID,
        r.OriginAirport,
        r.DestAirport,
        r.DistanceMiles,
        f.DepartureDateTime,
        DATE(f.DepartureDateTime) AS DepartureDate,
        f.AircraftType,
        f.TotalCapacity,
        f.FlightStatus,
        f.FuelCost,
        f.CrewCost,
        f.AirportCost,
        f.OtherOperatingCost,
        (f.FuelCost + f.CrewCost + f.AirportCost + f.OtherOperatingCost) AS TotalOperatingCost
    FROM Flights f
    JOIN Routes r ON f.RouteID = r.RouteID
    WHERE f.FlightStatus = 'Completed'
    """
    
    query_fact_bookings = """
    SELECT 
        b.BookingID,
        b.FlightID,
        b.CustomerID,
        c.Age,
        c.Gender,
        c.LoyaltyTier,
        c.PassengerType,
        b.BookingDateTime,
        DATE(b.BookingDateTime) AS BookingDate,
        b.CabinClass,
        b.TicketPrice,
        b.AncillaryRevenue,
        (b.TicketPrice + b.AncillaryRevenue) AS TotalRevenue,
        b.IsCancelled
    FROM Bookings b
    JOIN Customers c ON b.CustomerID = c.CustomerID
    WHERE b.IsCancelled = False
    """
    
    df_fact_flights = pd.read_sql(query_fact_flights, con=engine)
    df_fact_bookings = pd.read_sql(query_fact_bookings, con=engine)
    
    # Calculate DaysToDeparture directly in the DataFrame
    df_fact_bookings = df_fact_bookings.merge(df_fact_flights[['FlightID', 'DepartureDateTime']], on='FlightID', how='inner')
    df_fact_bookings['DaysToDeparture'] = (df_fact_bookings['DepartureDateTime'] - df_fact_bookings['BookingDateTime']).dt.days
    df_fact_bookings = df_fact_bookings.drop(columns=['DepartureDateTime'])

    processed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    df_fact_flights.to_csv(os.path.join(processed_dir, 'Fact_Flights.csv'), index=False)
    df_fact_bookings.to_csv(os.path.join(processed_dir, 'Fact_Bookings.csv'), index=False)
    
    print("Export Complete! Files saved to data/processed/:")
    print("- Fact_Flights.csv")
    print("- Fact_Bookings.csv")

if __name__ == '__main__':
    export_powerbi_data()
