"""
Geospatial utilities for location search and geocoding
"""
from geopy.geocoders import Nominatim
import numpy as np


def get_city_coordinates(city_name):
    """
    Legacy function for backwards compatibility.
    Returns (bbox, center_lat_lon) for a given city name.
    bbox format: [min_lon, min_lat, max_lon, max_lat]
    """
    result = search_locations(city_name)
    if result:
        bbox = result['bbox']
        center = (result['lat'], result['lon'])
        return bbox, center
    return None, None


def search_locations(query, buffer_km=15):
    """
    Search for a location by name and return structured data.
    
    Parameters:
    -----------
    query : str
        Location search query (e.g., "Phoenix, Arizona", "Tokyo", "New York City")
    buffer_km : float
        Buffer distance in kilometers for bounding box (default: 15km)
        
    Returns:
    --------
    dict or None
        {
            'name': str,        # Full location name
            'lat': float,       # Latitude
            'lon': float,       # Longitude
            'bbox': [float],    # [minLon, minLat, maxLon, maxLat]
            'display_name': str # Formatted address
        }
    """
    try:
        geolocator = Nominatim(user_agent="uhi_monitor_app_v2", timeout=10)
        location = geolocator.geocode(query, addressdetails=True)
        
        if not location:
            return None
        
        lat, lon = location.latitude, location.longitude
        
        # Try to get bounding box from raw data
        raw_bbox = location.raw.get('boundingbox')
        
        if raw_bbox:
            # Nominatim returns [min_lat, max_lat, min_lon, max_lon]
            min_lat, max_lat, min_lon, max_lon = [float(x) for x in raw_bbox]
            bbox = [min_lon, min_lat, max_lon, max_lat]
        else:
            # Create bbox from center point with buffer
            bbox = get_city_bbox(lat, lon, buffer_km)
        
        # Extract location name
        address = location.raw.get('address', {})
        name_parts = []
        
        # Build hierarchical name
        for key in ['city', 'town', 'village', 'state', 'country']:
            if key in address:
                name_parts.append(address[key])
        
        name = ', '.join(name_parts) if name_parts else location.address.split(',')[0]
        
        return {
            'name': name,
            'lat': lat,
            'lon': lon,
            'bbox': bbox,
            'display_name': location.address
        }
        
    except Exception as e:
        print(f"Error searching location '{query}': {e}")
        return None


def get_city_bbox(lat, lon, buffer_km=15):
    """
    Create a bounding box around a point with a given buffer.
    
    Parameters:
    -----------
    lat : float
        Latitude in degrees
    lon : float
        Longitude in degrees
    buffer_km : float
        Buffer distance in kilometers (default: 15km)
        
    Returns:
    --------
    list
        [minLon, minLat, maxLon, maxLat]
    """
    # Convert km to degrees (approximate)
    # 1 degree latitude ≈ 111 km everywhere
    # 1 degree longitude ≈ 111 km * cos(latitude)
    lat_buffer = buffer_km / 111.0
    lon_buffer = buffer_km / (111.0 * np.cos(np.radians(lat)))
    
    bbox = [
        lon - lon_buffer,  # minLon
        lat - lat_buffer,  # minLat
        lon + lon_buffer,  # maxLon
        lat + lat_buffer   # maxLat
    ]
    
    return bbox


def reverse_geocode(lat, lon, buffer_km=15):
    """
    Reverse geocode coordinates to get location information.
    
    Parameters:
    -----------
    lat : float
        Latitude in degrees
    lon : float
        Longitude in degrees
    buffer_km : float
        Buffer for bounding box (default: 15km)
        
    Returns:
    --------
    dict or None
        Same structure as search_locations()
    """
    try:
        geolocator = Nominatim(user_agent="uhi_monitor_app_v2", timeout=10)
        location = geolocator.reverse((lat, lon), addressdetails=True)
        
        if not location:
            return None
        
        # Create bbox from coordinates
        bbox = get_city_bbox(lat, lon, buffer_km)
        
        # Extract location name
        address = location.raw.get('address', {})
        name_parts = []
        
        for key in ['city', 'town', 'village', 'county', 'state', 'country']:
            if key in address:
                name_parts.append(address[key])
        
        name = ', '.join(name_parts[:3]) if name_parts else f"Location ({lat:.4f}, {lon:.4f})"
        
        return {
            'name': name,
            'lat': lat,
            'lon': lon,
            'bbox': bbox,
            'display_name': location.address
        }
        
    except Exception as e:
        print(f"Error reverse geocoding ({lat}, {lon}): {e}")
        return None
