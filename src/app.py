import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Airline Analytics Dashboard", layout="wide", page_icon="✈️")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    flights_path = os.path.join(base_dir, 'data', 'processed', 'Fact_Flights.csv')
    bookings_path = os.path.join(base_dir, 'data', 'processed', 'Fact_Bookings.csv')
    
    if not os.path.exists(flights_path) or not os.path.exists(bookings_path):
        return None, None
        
    df_flights = pd.read_csv(flights_path)
    df_bookings = pd.read_csv(bookings_path)
    
    # Calculate Profit metrics on Flights
    df_flights['Profit'] = 0 # Will calculate after joining revenue
    
    return df_flights, df_bookings

df_flights, df_bookings = load_data()

if df_flights is None:
    st.error("Data not found. Please run src/export_powerbi_data.py first.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters ✈️")
selected_origin = st.sidebar.multiselect("Origin Airport", df_flights['OriginAirport'].unique())
selected_dest = st.sidebar.multiselect("Destination Airport", df_flights['DestAirport'].unique())
selected_pax = st.sidebar.multiselect("Passenger Type", df_bookings['PassengerType'].unique())
selected_cabin = st.sidebar.multiselect("Cabin Class", df_bookings['CabinClass'].unique())

# --- Apply Filters ---
filtered_flights = df_flights.copy()
if selected_origin:
    filtered_flights = filtered_flights[filtered_flights['OriginAirport'].isin(selected_origin)]
if selected_dest:
    filtered_flights = filtered_flights[filtered_flights['DestAirport'].isin(selected_dest)]

filtered_bookings = df_bookings[df_bookings['FlightID'].isin(filtered_flights['FlightID'])]
if selected_pax:
    filtered_bookings = filtered_bookings[filtered_bookings['PassengerType'].isin(selected_pax)]
if selected_cabin:
    filtered_bookings = filtered_bookings[filtered_bookings['CabinClass'].isin(selected_cabin)]

# --- Calculate Metrics ---
total_revenue = filtered_bookings['TotalRevenue'].sum()
total_cost = filtered_flights['TotalOperatingCost'].sum()
gross_profit = total_revenue - total_cost
profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
total_pax = len(filtered_bookings)
total_capacity = filtered_flights['TotalCapacity'].sum()
load_factor = (total_pax / total_capacity * 100) if total_capacity > 0 else 0

st.title("✈️ Airline Revenue & Route Profitability")
st.markdown("Interactive exploration dashboard. **(Complementary to Power BI)**")

# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Gross Profit", f"${gross_profit:,.0f}", f"{profit_margin:.1f}% Margin")
col3.metric("Load Factor", f"{load_factor:.1f}%")
col4.metric("Total Passengers", f"{total_pax:,.0f}")

st.divider()

# --- Visualizations ---
tab1, tab2, tab3 = st.tabs(["Route Profitability", "Customer Segments", "Yield Management"])

with tab1:
    st.subheader("Route Performance")
    
    # Aggregate by route
    rev_by_route = filtered_bookings.groupby('FlightID')['TotalRevenue'].sum().reset_index()
    route_perf = filtered_flights.merge(rev_by_route, on='FlightID', how='left').fillna(0)
    route_summary = route_perf.groupby(['OriginAirport', 'DestAirport']).agg(
        TotalRevenue=('TotalRevenue', 'sum'),
        TotalOperatingCost=('TotalOperatingCost', 'sum')
    ).reset_index()
    route_summary['Profit'] = route_summary['TotalRevenue'] - route_summary['TotalOperatingCost']
    route_summary['Route'] = route_summary['OriginAirport'] + "-" + route_summary['DestAirport']
    
    fig1 = px.bar(route_summary, x='Route', y='Profit', color='Profit', color_continuous_scale='RdYlGn', title="Gross Profit by Route")
    st.plotly_chart(fig1, use_container_width=True)
    
    st.dataframe(route_summary.style.format({'TotalRevenue': '${:,.0f}', 'TotalOperatingCost': '${:,.0f}', 'Profit': '${:,.0f}'}), use_container_width=True)

with tab2:
    st.subheader("Customer Value (LTV)")
    
    ltv = filtered_bookings.groupby(['PassengerType', 'LoyaltyTier']).agg(
        TotalRevenue=('TotalRevenue', 'sum'),
        Customers=('CustomerID', 'nunique')
    ).reset_index()
    ltv['Avg LTV'] = ltv['TotalRevenue'] / ltv['Customers']
    
    fig2 = px.bar(ltv, x='LoyaltyTier', y='Avg LTV', color='PassengerType', barmode='group', title="Average Lifetime Value by Tier & Segment")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Booking Curve (Price vs Days to Departure)")
    
    curve = filtered_bookings.groupby(['DaysToDeparture', 'CabinClass'])['TicketPrice'].mean().reset_index()
    fig3 = px.line(curve, x='DaysToDeparture', y='TicketPrice', color='CabinClass', title="Average Ticket Price over Time")
    fig3.update_xaxes(autorange="reversed") # 90 days on left, 0 on right
    st.plotly_chart(fig3, use_container_width=True)
