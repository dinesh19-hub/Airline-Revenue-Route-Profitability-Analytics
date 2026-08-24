# %% [markdown]
# # Phase 3: Data Ingestion and Cleaning
# This notebook connects to the MySQL database, extracts the integrated dataset, and prepares it for analysis.

# %%
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import warnings
warnings.filterwarnings('ignore')

# %%
# Load environment variables (from parent dir since notebook runs in /notebooks)
env_path = os.path.join(os.path.dirname(os.getcwd()), '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.getcwd(), '.env') # Fallback if run from root
load_dotenv(env_path)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'airline_analytics')

encoded_pwd = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
auth = f"{DB_USER}:{encoded_pwd}" if encoded_pwd else f"{DB_USER}"
conn_str = f"mysql+pymysql://{auth}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_str)

# %% [markdown]
# ### Extract Flights and Routes

# %%
query_flights = """
SELECT f.*, r.OriginAirport, r.DestAirport, r.DistanceMiles
FROM Flights f
JOIN Routes r ON f.RouteID = r.RouteID
WHERE f.FlightStatus = 'Completed'
"""
df_flights = pd.read_sql(query_flights, con=engine)
df_flights.head()

# %% [markdown]
# ### Extract Bookings and Customers

# %%
query_bookings = """
SELECT b.*, c.Age, c.Gender, c.LoyaltyTier, c.PassengerType
FROM Bookings b
JOIN Customers c ON b.CustomerID = c.CustomerID
WHERE b.IsCancelled = False
"""
df_bookings = pd.read_sql(query_bookings, con=engine)
df_bookings.head()

# %% [markdown]
# ### Save Processed Data
# Saving to pickle for fast loading in subsequent notebooks.

# %%
# Ensure processed directory exists
base_dir = os.path.dirname(os.getcwd()) if os.path.basename(os.getcwd()) == 'notebooks' else os.getcwd()
processed_dir = os.path.join(base_dir, 'data', 'processed')
os.makedirs(processed_dir, exist_ok=True)

# Save for downstream notebooks
df_flights.to_pickle(os.path.join(processed_dir, 'flights_clean.pkl'))
df_bookings.to_pickle(os.path.join(processed_dir, 'bookings_clean.pkl'))
print("Data extracted and saved successfully.")
