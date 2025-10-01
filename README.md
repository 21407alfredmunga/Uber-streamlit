# Uber Trip Dashboard

A Power BI-style Streamlit dashboard for analyzing Uber trip data.

## Features

- **KPIs**: Total bookings, booking value, average fare, distance, and duration
- **Revenue Distribution**: Donut charts showing breakdown by payment type and vehicle type
- **Trend Analysis**: Line chart showing booking value over time
- **Location Analysis**: Bar charts for pickup and dropoff location revenue
- **Vehicle Summary**: Table with booking statistics by vehicle type
- **Interactive Filters**: Date range, location, and vehicle type filters

## Setup and Running

1. Make sure you have the virtual environment activated:
   ```bash
   source datascience_env/bin/activate
   ```

2. Install required packages (if not already installed):
   ```bash
   pip install streamlit pandas plotly numpy
   ```

3. Run the dashboard:
   ```bash
   streamlit run uber_dashboard.py
   ```

4. Open your browser to `http://localhost:8501` to view the dashboard.

## Data

The dashboard reads from `data/ncr_ride_bookings.csv` and automatically filters for completed rides only.

## Dashboard Components

### KPIs (Top Row)
- Total Bookings: Count of completed trips
- Total Booking Value: Sum of all fares (displayed in millions if >1M)
- Average Booking Value: Mean fare per trip
- Total Distance: Sum of all trip distances in km
- Average Duration: Mean trip duration in minutes

### Charts
- **Payment Type Distribution**: Donut chart showing revenue breakdown by payment method
- **Vehicle Type Distribution**: Donut chart showing revenue breakdown by vehicle type
- **Trend Analysis**: Line chart showing daily total booking value over time
- **Location Analysis**: Top 10 pickup and dropoff locations by revenue

### Summary Table
Vehicle-wise summary showing:
- Total bookings count
- Total revenue value
- Average fare per trip

### Filters (Sidebar)
- Date range selector
- Pickup location multi-select
- Dropoff location multi-select  
- Vehicle type multi-select

All charts and metrics update dynamically based on the selected filters.