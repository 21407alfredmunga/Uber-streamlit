import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

# Configure the page
st.set_page_config(
    page_title="Uber Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the Uber dataset"""
    try:
        # Load the data
        df = pd.read_csv('data/ncr_ride_bookings.csv')
        
        # Clean and rename columns to match the requirements
        df.columns = df.columns.str.strip()
        
        # Create a mapping for the required column names
        column_mapping = {
            'Booking ID': 'trip_id',
            'Date': 'date',
            'Pickup Location': 'pickup',
            'Drop Location': 'dropoff',
            'Booking Value': 'fare',
            'Ride Distance': 'distance_miles',
            'Vehicle Type': 'vehicle_type',
            'Payment Method': 'payment_type',
            'Avg CTAT': 'duration_min'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter only completed rides for meaningful analysis
        df = df[df['Booking Status'] == 'Completed'].copy()
        
        # Clean numeric columns
        df['fare'] = pd.to_numeric(df['fare'], errors='coerce')
        df['distance_miles'] = pd.to_numeric(df['distance_miles'], errors='coerce')
        df['duration_min'] = pd.to_numeric(df['duration_min'], errors='coerce')
        
        # Remove rows with null fare values (can't analyze revenue without fare)
        df = df.dropna(subset=['fare'])
        
        # Clean string columns
        df['trip_id'] = df['trip_id'].astype(str).str.replace('"', '')
        df['pickup'] = df['pickup'].fillna('Unknown')
        df['dropoff'] = df['dropoff'].fillna('Unknown')
        df['payment_type'] = df['payment_type'].fillna('Unknown')
        df['vehicle_type'] = df['vehicle_type'].fillna('Unknown')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_kpi_metrics(df):
    """Create KPI metrics for the dashboard"""
    if df.empty:
        return 0, 0, 0, 0, 0
    
    total_bookings = len(df)
    total_booking_value = df['fare'].sum()
    avg_booking_value = df['fare'].mean()
    total_distance = df['distance_miles'].sum()
    avg_duration = df['duration_min'].mean()
    
    return total_bookings, total_booking_value, avg_booking_value, total_distance, avg_duration

def create_donut_chart(df, column, title):
    """Create a donut chart for categorical analysis"""
    if df.empty:
        return go.Figure()
    
    value_counts = df.groupby(column)['fare'].sum().reset_index()
    
    fig = px.pie(
        value_counts, 
        values='fare', 
        names=column,
        title=title,
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        height=400,
        font=dict(size=12)
    )
    
    return fig

def create_trend_chart(df):
    """Create a line chart showing booking value trend over time"""
    if df.empty:
        return go.Figure()
    
    # Group by date and sum fare
    daily_revenue = df.groupby(df['date'].dt.date)['fare'].sum().reset_index()
    daily_revenue.columns = ['date', 'total_fare']
    
    fig = px.line(
        daily_revenue,
        x='date',
        y='total_fare',
        title='Total Booking Value Over Time',
        labels={'total_fare': 'Total Booking Value (₹)', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    return fig

def create_location_chart(df, location_type, title):
    """Create bar chart for location analysis"""
    if df.empty:
        return go.Figure()
    
    location_revenue = df.groupby(location_type)['fare'].sum().reset_index()
    location_revenue = location_revenue.sort_values('fare', ascending=False).head(10)
    
    fig = px.bar(
        location_revenue,
        x=location_type,
        y='fare',
        title=title,
        labels={'fare': 'Revenue (₹)', location_type: location_type.title()}
    )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig

def create_vehicle_summary_table(df):
    """Create vehicle summary table"""
    if df.empty:
        return pd.DataFrame()
    
    vehicle_summary = df.groupby('vehicle_type').agg({
        'trip_id': 'count',
        'fare': ['sum', 'mean']
    }).round(2)
    
    # Flatten column names
    vehicle_summary.columns = ['Total_Bookings', 'Total_Value', 'Avg_Fare']
    vehicle_summary = vehicle_summary.reset_index()
    vehicle_summary = vehicle_summary.sort_values('Total_Value', ascending=False)
    
    return vehicle_summary

def apply_filters(df, date_range, pickup_filter, dropoff_filter, vehicle_filter):
    """Apply sidebar filters to the dataframe"""
    filtered_df = df.copy()
    
    # Date range filter
    if date_range:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= start_date) & 
            (filtered_df['date'].dt.date <= end_date)
        ]
    
    # Pickup filter
    if pickup_filter and 'All' not in pickup_filter:
        filtered_df = filtered_df[filtered_df['pickup'].isin(pickup_filter)]
    
    # Dropoff filter
    if dropoff_filter and 'All' not in dropoff_filter:
        filtered_df = filtered_df[filtered_df['dropoff'].isin(dropoff_filter)]
    
    # Vehicle type filter
    if vehicle_filter and 'All' not in vehicle_filter:
        filtered_df = filtered_df[filtered_df['vehicle_type'].isin(vehicle_filter)]
    
    return filtered_df

def main():
    # Title
    st.markdown('<h1 class="main-header">🚗 Uber Trip Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data available. Please check your data file.")
        return
    
    # Sidebar filters
    st.sidebar.title("🔍 Filters")
    
    # Date range filter
    min_date = df['date'].dt.date.min()
    max_date = df['date'].dt.date.max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Pickup location filter
    pickup_locations = ['All'] + sorted(df['pickup'].unique().tolist())
    pickup_filter = st.sidebar.multiselect(
        "Select Pickup Locations",
        pickup_locations,
        default=['All']
    )
    
    # Dropoff location filter
    dropoff_locations = ['All'] + sorted(df['dropoff'].unique().tolist())
    dropoff_filter = st.sidebar.multiselect(
        "Select Dropoff Locations",
        dropoff_locations,
        default=['All']
    )
    
    # Vehicle type filter
    vehicle_types = ['All'] + sorted(df['vehicle_type'].unique().tolist())
    vehicle_filter = st.sidebar.multiselect(
        "Select Vehicle Types",
        vehicle_types,
        default=['All']
    )
    
    # Apply filters
    filtered_df = apply_filters(df, date_range, pickup_filter, dropoff_filter, vehicle_filter)
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return
    
    # KPIs
    st.subheader("📊 Key Performance Indicators")
    total_bookings, total_value, avg_value, total_distance, avg_duration = create_kpi_metrics(filtered_df)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Bookings",
            value=f"{total_bookings:,}"
        )
    
    with col2:
        st.metric(
            label="Total Booking Value",
            value=f"₹{total_value/1_000_000:.2f}M" if total_value >= 1_000_000 else f"₹{total_value:,.0f}"
        )
    
    with col3:
        st.metric(
            label="Avg Booking Value",
            value=f"₹{avg_value:.0f}"
        )
    
    with col4:
        st.metric(
            label="Total Distance",
            value=f"{total_distance:,.0f} km"
        )
    
    with col5:
        st.metric(
            label="Avg Duration",
            value=f"{avg_duration:.1f} min"
        )
    
    # Donut Charts
    st.subheader("🍩 Revenue Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        payment_chart = create_donut_chart(filtered_df, 'payment_type', 'Revenue by Payment Type')
        st.plotly_chart(payment_chart, use_container_width=True)
    
    with col2:
        vehicle_chart = create_donut_chart(filtered_df, 'vehicle_type', 'Revenue by Vehicle Type')
        st.plotly_chart(vehicle_chart, use_container_width=True)
    
    # Trend Analysis
    st.subheader("📈 Trend Analysis")
    trend_chart = create_trend_chart(filtered_df)
    st.plotly_chart(trend_chart, use_container_width=True)
    
    # Location Analysis
    st.subheader("📍 Location Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        pickup_chart = create_location_chart(filtered_df, 'pickup', 'Top 10 Revenue by Pickup Location')
        st.plotly_chart(pickup_chart, use_container_width=True)
    
    with col2:
        dropoff_chart = create_location_chart(filtered_df, 'dropoff', 'Top 10 Revenue by Dropoff Location')
        st.plotly_chart(dropoff_chart, use_container_width=True)
    
    # Vehicle Summary Table
    st.subheader("🚙 Vehicle Summary")
    vehicle_summary = create_vehicle_summary_table(filtered_df)
    
    if not vehicle_summary.empty:
        # Format the values for better display
        vehicle_summary['Total_Value'] = vehicle_summary['Total_Value'].apply(lambda x: f"₹{x:,.0f}")
        vehicle_summary['Avg_Fare'] = vehicle_summary['Avg_Fare'].apply(lambda x: f"₹{x:.0f}")
        
        st.dataframe(
            vehicle_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "vehicle_type": st.column_config.TextColumn("Vehicle Type"),
                "Total_Bookings": st.column_config.NumberColumn("Total Bookings"),
                "Total_Value": st.column_config.TextColumn("Total Value"),
                "Avg_Fare": st.column_config.TextColumn("Average Fare")
            }
        )
    
    # Display data info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Data Info")
    st.sidebar.markdown(f"**Total Records:** {len(filtered_df):,}")
    st.sidebar.markdown(f"**Date Range:** {filtered_df['date'].dt.date.min()} to {filtered_df['date'].dt.date.max()}")
    st.sidebar.markdown(f"**Vehicle Types:** {filtered_df['vehicle_type'].nunique()}")
    st.sidebar.markdown(f"**Pickup Locations:** {filtered_df['pickup'].nunique()}")

if __name__ == "__main__":
    main()