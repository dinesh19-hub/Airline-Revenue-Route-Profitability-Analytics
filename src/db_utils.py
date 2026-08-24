import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'airline_analytics')

from urllib.parse import quote_plus

def get_engine(include_db=True):
    # PyMySQL connection string
    # If password is empty, don't include the colon
    encoded_pwd = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    auth = f"{DB_USER}:{encoded_pwd}" if encoded_pwd else f"{DB_USER}"
    conn_str = f"mysql+pymysql://{auth}@{DB_HOST}:{DB_PORT}"
    if include_db:
        conn_str += f"/{DB_NAME}"
    return create_engine(conn_str)

def initialize_database():
    print("Connecting to MySQL...")
    engine_no_db = get_engine(include_db=False)
    with engine_no_db.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"))
        print(f"Database {DB_NAME} ensured.")
        
    engine = get_engine()
    
    # Read schema.sql
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Split by semicolon and execute
    with engine.begin() as conn:
        # Drop existing tables in reverse order to respect FKs
        tables_to_drop = ['Bookings', 'Flights', 'Routes', 'Airports', 'Customers']
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for table in tables_to_drop:
            conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            
        for statement in schema_sql.split(';'):
            if statement.strip():
                conn.execute(text(statement.strip()))
        print("Schema initialized.")

def load_data():
    engine = get_engine()
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
    
    # Load in correct order to respect Foreign Keys
    tables = [
        ('Airports.csv', 'Airports'),
        ('Routes.csv', 'Routes'),
        ('Customers.csv', 'Customers'),
        ('Flights.csv', 'Flights'),
        ('Bookings.csv', 'Bookings')
    ]
    
    for file_name, table_name in tables:
        file_path = os.path.join(data_dir, file_name)
        print(f"Loading {file_name} into {table_name}...")
        df = pd.read_csv(file_path)
        
        # Insert using chunksize
        df.to_sql(table_name, con=engine, if_exists='append', index=False, chunksize=10000)
        print(f"Finished loading {len(df):,} rows into {table_name}.")

if __name__ == '__main__':
    initialize_database()
    load_data()
