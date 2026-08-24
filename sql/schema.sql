-- schema.sql
-- MySQL Schema for Airline Analytics

CREATE TABLE Airports (
    AirportCode VARCHAR(3) PRIMARY KEY,
    City VARCHAR(100),
    Country VARCHAR(100),
    Region VARCHAR(50),
    HubStatus BOOLEAN
);

CREATE TABLE Routes (
    RouteID VARCHAR(10) PRIMARY KEY,
    OriginAirport VARCHAR(3),
    DestAirport VARCHAR(3),
    DistanceMiles INT,
    FOREIGN KEY (OriginAirport) REFERENCES Airports(AirportCode),
    FOREIGN KEY (DestAirport) REFERENCES Airports(AirportCode)
);

CREATE TABLE Flights (
    FlightID VARCHAR(15) PRIMARY KEY,
    RouteID VARCHAR(10),
    DepartureDateTime DATETIME,
    AircraftType VARCHAR(50),
    TotalCapacity INT,
    FlightStatus VARCHAR(20), -- 'Completed', 'Cancelled', 'Delayed'
    FuelCost DECIMAL(10,2),
    CrewCost DECIMAL(10,2),
    AirportCost DECIMAL(10,2),
    OtherOperatingCost DECIMAL(10,2),
    FOREIGN KEY (RouteID) REFERENCES Routes(RouteID)
);

CREATE TABLE Customers (
    CustomerID VARCHAR(15) PRIMARY KEY,
    Age INT,
    Gender VARCHAR(10),
    LoyaltyTier VARCHAR(20), -- 'None', 'Silver', 'Gold', 'Platinum'
    PassengerType VARCHAR(20) -- 'Business', 'Leisure'
);

CREATE TABLE Bookings (
    BookingID VARCHAR(20) PRIMARY KEY,
    FlightID VARCHAR(15),
    CustomerID VARCHAR(15),
    BookingDateTime DATETIME,
    CabinClass VARCHAR(20), -- 'Economy', 'Business', 'First'
    TicketPrice DECIMAL(10,2),
    AncillaryRevenue DECIMAL(10,2),
    IsCancelled BOOLEAN,
    FOREIGN KEY (FlightID) REFERENCES Flights(FlightID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);
