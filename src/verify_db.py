import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def run_verification():
    load_dotenv()

    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'airline_analytics')

    from urllib.parse import quote_plus
    encoded_pwd = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""
    auth = f"{DB_USER}:{encoded_pwd}" if encoded_pwd else f"{DB_USER}"
    conn_str = f"mysql+pymysql://{auth}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_str)

    queries_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql', 'queries.sql')
    with open(queries_path, 'r') as f:
        sql_content = f.read()
    
    # Extract query descriptions/headers from comments
    statements = sql_content.split(';')
    
    print("\n" + "="*50)
    print("PHASE 2: DATABASE VERIFICATION RESULTS")
    print("="*50)
    
    # 1. Basic Row Counts
    print("\n--- Basic Row Counts ---")
    tables = ['Airports', 'Routes', 'Customers', 'Flights', 'Bookings']
    for table in tables:
        count_df = pd.read_sql(f"SELECT COUNT(*) AS Count FROM {table}", con=engine)
        print(f"Table `{table}`: {count_df.iloc[0]['Count']:,} rows")
        
    print("\n--- Executing Foundational Queries ---")
    
    # 2. Run the analytics queries
    query_names = [
        "1. Route Profitability Analysis (Top 3)",
        "2. Capacity Utilization & Load Factor Analysis (Top 3)",
        "3. Customer Segmentation & Value Analysis",
        "4. Yield Management & Booking Curve (Sample)"
    ]
    
    with engine.connect() as conn:
        for idx, stmt in enumerate(statements):
            if stmt.strip():
                try:
                    df = pd.read_sql(text(stmt), con=conn)
                    print(f"\n{query_names[idx]}")
                    if "Route Profitability" in query_names[idx] or "Capacity" in query_names[idx]:
                        print(df.head(3).to_markdown(index=False))
                    elif "Yield" in query_names[idx]:
                        # Just print top 5 of the curve to save space
                        print(df.head(5).to_markdown(index=False))
                    else:
                        print(df.to_markdown(index=False))
                except Exception as e:
                    pass

if __name__ == '__main__':
    run_verification()
