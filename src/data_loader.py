import pystac_client
import planetary_computer
from odc.stac import load
import pandas as pd

def fetch_landsat_data(bbox, start_date, end_date, max_cloud_cover=20):
    """
    Fetches Landsat 8/9 Level 2 data from Microsoft Planetary Computer.
    """
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )
    
    time_range = f"{start_date}/{end_date}"
    
    search = catalog.search(
        collections=["landsat-c2-l2"],
        bbox=bbox,
        datetime=time_range,
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
        sortby=[{"field": "eo:cloud_cover", "direction": "asc"}] # Get clearest image first
    )
    
    items = search.item_collection()
    print(f"Found {len(items)} scenes.")
    
    if not items:
        return None
    
    # Take the least cloudy item to avoid loading too much data for a demo
    # In a real app we might want to composite, but for now let's pick the best single scene.
    selected_items = [items[0]]
    
    # Landsat 8/9 Bands: 
    # red: Red
    # nir08: Near Infrared
    # lwir11: Thermal Infrared (Band 10)
    # qa_pixel: Quality Assessment
    
    data = load(
        selected_items,
        bbox=bbox,
        bands=["red", "nir08", "lwir11", "qa_pixel"],
        resolution=0.0003,  # ~30m in degrees for WGS84
        crs="EPSG:4326"  # WGS84 for Leaflet compatibility
    )
    
    return data
