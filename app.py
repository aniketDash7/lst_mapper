import streamlit as st
import datetime
import matplotlib.pyplot as plt
import numpy as np
from src.utils import get_city_coordinates
from src.data_loader import fetch_landsat_data
from src.processor import calculate_lst, calculate_ndvi

st.set_page_config(page_title="CityCool: UHI Monitor", layout="wide")

st.title("🌡️ CityCool: Urban Heat Island Monitor")
st.markdown("""
Monitor Land Surface Temperature (LST) and Vegetation Health (NDVI) using Landsat 8/9 satellite data.
Identify urban hot spots and their correlation with lack of green cover.
""")

# Sidebar Controls
with st.sidebar:
    st.header("Settings")
    city_name = st.text_input("Enter City Name", "Bengaluru")
    
    today = datetime.date.today()
    last_year = today - datetime.timedelta(days=365)
    
    date_range = st.date_input(
        "Date Range",
        (last_year, today)
    )
    
    max_cloud = st.slider("Max Cloud Cover (%)", 0, 100, 10)
    
    analyze_btn = st.button("Analyze Region")

if analyze_btn:
    if not city_name:
        st.error("Please enter a city name.")
    else:
        with st.spinner(f"Geocoding {city_name}..."):
            bbox, center = get_city_coordinates(city_name)
            
        if not bbox:
            st.error("City not found. Please try again.")
        else:
            st.success(f"Found {city_name} at {center}")
            
            with st.spinner("Searching and fetching Satellite Data (this may take a moment)..."):
                start_date = date_range[0]
                end_date = date_range[1] if len(date_range) > 1 else date_range[0]
                
                ds = fetch_landsat_data(bbox, start_date, end_date, max_cloud)
                
            if ds is None:
                st.warning("No suitable data found for this criteria. Try increasing cloud cover tolerance or date range.")
            else:
                # Select the first time step (clearest image)
                # ds is an xarray Dataset with time, y, x
                # We squeeze the time dimension if it exists and we selected one
                
                # Check dimensions
                if 'time' in ds.dims:
                     # Already sorted by cloud cover in data_loader, so take first
                    scene = ds.isel(time=0)
                    time_str = str(scene.time.values)[:10]
                    st.info(f"Analyzing Scene from: {time_str}")
                else:
                    scene = ds
                    st.info("Analyzing Scene")

                # Calculations
                with st.spinner("Processing LST and NDVI..."):
                    lst = calculate_lst(scene)
                    ndvi = calculate_ndvi(scene)
                
                # Visualization
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Land Surface Temperature (°C)")
                    fig1, ax1 = plt.subplots(figsize=(10, 10))
                    im1 = lst.plot(ax=ax1, cmap='magma', add_colorbar=True, robust=True)
                    ax1.set_title("LST (°C)")
                    ax1.axis('off')
                    st.pyplot(fig1)
                    
                    # Stats
                    avg_temp = float(lst.mean())
                    max_temp = float(lst.max())
                    st.metric("Avg Temp", f"{avg_temp:.1f}°C")
                    st.metric("Max Temp", f"{max_temp:.1f}°C")

                with col2:
                    st.subheader("Vegetation Index (NDVI)")
                    fig2, ax2 = plt.subplots(figsize=(10, 10))
                    # NDVI standard cmap is RdYlGn (Red=Low, Green=High)
                    im2 = ndvi.plot(ax=ax2, cmap='RdYlGn', add_colorbar=True, vmin=-0.2, vmax=0.8)
                    ax2.set_title("NDVI")
                    ax2.axis('off')
                    st.pyplot(fig2)
                    
                    # Stats
                    avg_ndvi = float(ndvi.mean())
                    st.metric("Avg NDVI", f"{avg_ndvi:.2f}")

                st.markdown("---")
                st.caption("Data Source: Microsoft Planetary Computer (Landsat Collection 2 Level 2)")
