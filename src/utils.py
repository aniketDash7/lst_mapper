from geopy.geocoders import Nominatim

def get_city_coordinates(city_name):
    """
    Returns (bbox, center_lat_lon) for a given city name.
    bbox format: [min_lon, min_lat, max_lon, max_lat]
    """
    try:
        geolocator = Nominatim(user_agent="uhi_monitor_app_v1")
        location = geolocator.geocode(city_name)
        
        if not location:
            return None, None
            
        # Nominatim returns boundingbox as [min_lat, max_lat, min_lon, max_lon]
        raw_bbox = location.raw.get('boundingbox')
        
        if raw_bbox:
            min_lat, max_lat, min_lon, max_lon = [float(x) for x in raw_bbox]
            # Standard GeoJSON bbox: [min_lon, min_lat, max_lon, max_lat]
            bbox = [min_lon, min_lat, max_lon, max_lat]
        else:
            # Fallback
            lat, lon = location.latitude, location.longitude
            delta = 0.1
            bbox = [lon - delta, lat - delta, lon + delta, lat + delta]
            
        return bbox, (location.latitude, location.longitude)
    except Exception as e:
        print(f"Error geocoding {city_name}: {e}")
        return None, None
