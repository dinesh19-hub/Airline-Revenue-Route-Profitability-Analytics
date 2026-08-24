-- ====================================================================================
-- BAIN-STYLE BUSINESS ANALYTICS QUERIES
-- Database: airline_analytics
-- ====================================================================================

-- 1. Route Profitability Analysis
-- Calculates the total revenue, total costs, and profit margin for each route.
SELECT 
    r.RouteID,
    r.OriginAirport,
    r.DestAirport,
    COUNT(DISTINCT f.FlightID) AS TotalFlights,
    SUM(CASE WHEN b.IsCancelled = False THEN 1 ELSE 0 END) AS TotalPassengers,
    SUM(CASE WHEN b.IsCancelled = False THEN b.TicketPrice + b.AncillaryRevenue ELSE 0 END) AS TotalRevenue,
    SUM(f.FuelCost + f.CrewCost + f.AirportCost + f.OtherOperatingCost) AS TotalOperatingCost,
    SUM(CASE WHEN b.IsCancelled = False THEN b.TicketPrice + b.AncillaryRevenue ELSE 0 END) 
        - SUM(f.FuelCost + f.CrewCost + f.AirportCost + f.OtherOperatingCost) AS Profit,
    (SUM(CASE WHEN b.IsCancelled = False THEN b.TicketPrice + b.AncillaryRevenue ELSE 0 END) 
        - SUM(f.FuelCost + f.CrewCost + f.AirportCost + f.OtherOperatingCost)) 
        / NULLIF(SUM(CASE WHEN b.IsCancelled = False THEN b.TicketPrice + b.AncillaryRevenue ELSE 0 END), 0) AS ProfitMargin
FROM Routes r
JOIN Flights f ON r.RouteID = f.RouteID
LEFT JOIN Bookings b ON f.FlightID = b.FlightID
WHERE f.FlightStatus = 'Completed'
GROUP BY r.RouteID, r.OriginAirport, r.DestAirport
ORDER BY Profit DESC;

-- 2. Capacity Utilization & Load Factor Analysis
-- Calculates the average load factor for flights, segmented by Aircraft Type and Route.
SELECT 
    r.RouteID,
    f.AircraftType,
    AVG(f.TotalCapacity) AS AvgCapacity,
    AVG(PaxCount.TotalPassengers) AS AvgPassengers,
    AVG(PaxCount.TotalPassengers / f.TotalCapacity) AS AverageLoadFactor
FROM Flights f
JOIN Routes r ON f.RouteID = r.RouteID
JOIN (
    SELECT FlightID, COUNT(*) AS TotalPassengers 
    FROM Bookings 
    WHERE IsCancelled = False 
    GROUP BY FlightID
) AS PaxCount ON f.FlightID = PaxCount.FlightID
WHERE f.FlightStatus = 'Completed'
GROUP BY r.RouteID, f.AircraftType
ORDER BY AverageLoadFactor DESC;

-- 3. Customer Segmentation & Value Analysis
-- Segments customers by PassengerType and LoyaltyTier to find the most valuable cohorts.
SELECT 
    c.PassengerType,
    c.LoyaltyTier,
    COUNT(DISTINCT c.CustomerID) AS CustomerCount,
    COUNT(b.BookingID) / COUNT(DISTINCT c.CustomerID) AS BookingsPerCustomer,
    AVG(b.TicketPrice) AS AvgTicketPrice,
    AVG(b.AncillaryRevenue) AS AvgAncillaryRevenue,
    SUM(b.TicketPrice + b.AncillaryRevenue) / COUNT(DISTINCT c.CustomerID) AS AvgCustomerValue
FROM Customers c
JOIN Bookings b ON c.CustomerID = b.CustomerID
WHERE b.IsCancelled = False
GROUP BY c.PassengerType, c.LoyaltyTier
ORDER BY AvgCustomerValue DESC;

-- 4. Yield Management & Booking Curve
-- Analyzes how average ticket prices and booking volume change relative to days until departure.
SELECT 
    DATEDIFF(f.DepartureDateTime, b.BookingDateTime) AS DaysToDeparture,
    b.CabinClass,
    c.PassengerType,
    COUNT(b.BookingID) AS BookingVolume,
    AVG(b.TicketPrice) AS AvgTicketPrice
FROM Bookings b
JOIN Flights f ON b.FlightID = f.FlightID
JOIN Customers c ON b.CustomerID = c.CustomerID
WHERE b.IsCancelled = False
GROUP BY DaysToDeparture, b.CabinClass, c.PassengerType
ORDER BY DaysToDeparture DESC, b.CabinClass;
