# Power BI Dashboard Implementation Guide

This guide provides the exact blueprint for recreating the Bain-style Airline Revenue and Route Profitability dashboard in Power BI.

## 1. Data Import & Modeling
1. Open Power BI Desktop.
2. Click **Get Data > Text/CSV**.
3. Import `data/processed/Fact_Flights.csv` and `data/processed/Fact_Bookings.csv`.
4. Go to the **Model View** and ensure a `1-to-Many` relationship exists from `Fact_Flights[FlightID]` to `Fact_Bookings[FlightID]`. (Cross filter direction: Both).

## 2. DAX Measures
Create a new Measure table (or place them in `Fact_Flights` / `Fact_Bookings`):

### Financials
```dax
Total Revenue = SUM(Fact_Bookings[TotalRevenue])
Total Operating Cost = SUM(Fact_Flights[TotalOperatingCost])
Gross Profit = [Total Revenue] - [Total Operating Cost]
Profit Margin % = DIVIDE([Gross Profit], [Total Revenue], 0)
Average Ticket Price = AVERAGE(Fact_Bookings[TicketPrice])
```

### Operations
```dax
Total Passengers = COUNTROWS(Fact_Bookings)
Total Capacity = SUM(Fact_Flights[TotalCapacity])
Load Factor % = DIVIDE([Total Passengers], [Total Capacity], 0)
Total Flights = COUNTROWS(Fact_Flights)
```

### Customer Value
```dax
Average LTV = DIVIDE([Total Revenue], DISTINCTCOUNT(Fact_Bookings[CustomerID]), 0)
```

## 3. Visualizations Blueprint

### Page 1: Route Profitability & Operations
- **KPI Cards (Top):** `Total Revenue`, `Gross Profit`, `Profit Margin %`, `Load Factor %`.
- **Matrix (Left):** 
  - Rows: `OriginAirport`, `DestAirport`
  - Values: `Total Revenue`, `Total Operating Cost`, `Gross Profit`, `Profit Margin %` (conditional formatting: green positive, red negative).
- **Line Chart (Top Right):** 
  - X-Axis: `DepartureDate` (Month)
  - Y-Axis: `Load Factor %`
- **Bar Chart (Bottom Right):** 
  - Y-Axis: `OriginAirport` & `DestAirport` 
  - X-Axis: `Profit Margin %`

### Page 2: Customer Value & Yield Management
- **Pie Chart / Donut Chart:**
  - Legend: `PassengerType` (Business vs Leisure)
  - Values: `Total Revenue`
- **Bar Chart (Customer Value):**
  - X-Axis: `LoyaltyTier`
  - Y-Axis: `Average LTV`
  - Legend: `PassengerType`
- **Line Chart (Booking Curve):**
  - X-Axis: `DaysToDeparture` (Sort Descending)
  - Y-Axis: `Average Ticket Price`
  - Legend: `CabinClass`
