"""
Data processing functions for LST and NDVI calculations
"""
import xarray as xr
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for server
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import base64
from io import BytesIO
from PIL import Image


def calculate_lst(ds):
    """
    Calculates Land Surface Temperature in Celsius from Landsat Level 2 'lwir11' band.
    Formula: Kelvin = DN * 0.003418 + 149.0
    Celsius = Kelvin - 273.15
    """
    if 'lwir11' not in ds:
        raise ValueError("Dataset must contain 'lwir11' band for LST calculation.")
    
    # Convert to float for calculation
    st_band = ds.lwir11.astype('float32')
    
    # Apply Scale Factor and Offset for Collection 2 Level 2
    kelvin = st_band * 0.003418 + 149.0
    celsius = kelvin - 273.15
    
    # Mask unreasonably low values which likely indicate no-data or background
    # 0 DN translates to ~149K or -124C. Real earth temps rarely go below -90C.
    celsius = celsius.where(celsius > -100)
    
    return celsius


def calculate_ndvi(ds):
    """
    Calculates NDVI (Normalized Difference Vegetation Index).
    Formula: (NIR - Red) / (NIR + Red)
    """
    if 'nir08' not in ds or 'red' not in ds:
        raise ValueError("Dataset must contain 'nir08' and 'red' bands.")
        
    # Scale factors for Collection 2 Level 2 Surface Reflectance
    # DN * 2.75e-5 - 0.2
    
    nir = ds.nir08.astype('float32') * 0.0000275 - 0.2
    red = ds.red.astype('float32') * 0.0000275 - 0.2
    
    # Avoid division by zero
    ndvi = (nir - red) / (nir + red + 1e-6)
    
    # Clip to valid range [-1, 1] usually, but let's just leave it raw for inspection
    # Mask invalid data
    ndvi = ndvi.where(ndvi > -1.0).where(ndvi < 1.0)
    
    return ndvi


def generate_lst_image(lst_array, dpi=150):
    """
    Generate a PNG image from LST data with temperature color scale.
    
    Parameters:
    -----------
    lst_array : xarray.DataArray
        Land Surface Temperature data in Celsius
    dpi : int
        Image resolution (default: 150)
        
    Returns:
    --------
    tuple : (base64_encoded_png, bounds)
        - base64_encoded_png : str
        - bounds : [[minLat, minLon], [maxLat, maxLon]]
    """
    # Get data bounds - extract before image generation
    coords = lst_array.coords
    
    print(f"Available coordinates: {list(coords.keys())}")
    print(f"Array shape: {lst_array.shape}")
    print(f"Array dims: {lst_array.dims}")
    
    # Handle different coordinate naming conventions
    if 'longitude' in coords and 'latitude' in coords:
        lon_vals = coords['longitude'].values
        lat_vals = coords['latitude'].values
        print(f"Using longitude/latitude coords")
    elif 'x' in coords and 'y' in coords:
        # For WGS84 (EPSG:4326), x=longitude, y=latitude
        lon_vals = coords['x'].values
        lat_vals = coords['y'].values
        print(f"Using x/y coords")
        print(f"X range: {lon_vals.min()} to {lon_vals.max()}")
        print(f"Y range: {lat_vals.min()} to {lat_vals.max()}")
    else:
        # Last resort fallback
        lon_vals = np.array([0, 1])
        lat_vals = np.array([0, 1])
        print("WARNING: No recognized coordinates found, using fallback!")
    
    # Create Leaflet-compatible bounds [[minLat, minLon], [maxLat, maxLon]]
    bounds = [
        [float(lat_vals.min()), float(lon_vals.min())],  # [minLat, minLon]
        [float(lat_vals.max()), float(lon_vals.max())]   # [maxLat, maxLon]
    ]
    
    print(f"LST Image bounds: {bounds}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10), dpi=dpi)
    
    # Use magma colormap (dark to bright) - good for temperature
    # Clip extremes for better visualization
    vmin = float(np.nanpercentile(lst_array.values, 2))
    vmax = float(np.nanpercentile(lst_array.values, 98))
    
    # Plot without axes or labels
    im = ax.imshow(
        lst_array.values,
        cmap='RdYlBu_r',  # Red (hot) to Blue (cool)
        vmin=vmin,
        vmax=vmax,
        interpolation='bilinear',
        aspect='auto'
    )
    
    ax.axis('off')
    plt.tight_layout(pad=0)
    
    # Convert to PNG bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    buf.seek(0)
    plt.close(fig)
    
    # Encode as base64
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return img_base64, bounds


def generate_ndvi_image(ndvi_array, dpi=150):
    """
    Generate a PNG image from NDVI data with vegetation color scale.
    
    Parameters:
    -----------
    ndvi_array : xarray.DataArray
        NDVI data (-1 to 1)
    dpi : int
        Image resolution (default: 150)
        
    Returns:
    --------
    tuple : (base64_encoded_png, bounds)
    """
    # Get data bounds - extract before image generation
    coords = ndvi_array.coords
    
    # Handle different coordinate naming conventions
    if 'longitude' in coords and 'latitude' in coords:
        lon_vals = coords['longitude'].values
        lat_vals = coords['latitude'].values
    elif 'x' in coords and 'y' in coords:
        # For WGS84 (EPSG:4326), x=longitude, y=latitude
        lon_vals = coords['x'].values
        lat_vals = coords['y'].values
    else:
        # Last resort fallback
        lon_vals = np.array([0, 1])
        lat_vals = np.array([0, 1])
    
    # Create Leaflet-compatible bounds [[minLat, minLon], [maxLat, maxLon]]
    bounds = [
        [float(lat_vals.min()), float(lon_vals.min())],  # [minLat, minLon]
        [float(lat_vals.max()), float(lon_vals.max())]   # [maxLat, maxLon]
    ]
    
    print(f"NDVI Image bounds: {bounds}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10), dpi=dpi)
    
    # Plot with RdYlGn colormap (Red = bare, Green = vegetation)
    im = ax.imshow(
        ndvi_array.values,
        cmap='RdYlGn',
        vmin=-0.2,
        vmax=0.8,
        interpolation='bilinear',
        aspect='auto'
    )
    
    ax.axis('off')
    plt.tight_layout(pad=0)
    
    # Convert to PNG bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    buf.seek(0)
    plt.close(fig)
    
    # Encode as base64
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return img_base64, bounds


def calculate_statistics(data_array):
    """
    Calculate comprehensive statistics from a data array.
    
    Parameters:
    -----------
    data_array : xarray.DataArray
        Input data
        
    Returns:
    --------
    dict : Statistics dictionary
    """
    # Remove NaN values for calculations
    values = data_array.values.flatten()
    valid_values = values[~np.isnan(values)]
    
    if len(valid_values) == 0:
        return {
            'min': 0,
            'max': 0,
            'mean': 0,
            'median': 0,
            'std': 0,
            'p25': 0,
            'p75': 0
        }
    
    stats = {
        'min': float(np.min(valid_values)),
        'max': float(np.max(valid_values)),
        'mean': float(np.mean(valid_values)),
        'median': float(np.median(valid_values)),
        'std': float(np.std(valid_values)),
        'p25': float(np.percentile(valid_values, 25)),
        'p75': float(np.percentile(valid_values, 75))
    }
    
    return stats


def lst_ndvi_correlation(lst_array, ndvi_array):
    """
    Calculate correlation coefficient between LST and NDVI.
    
    Parameters:
    -----------
    lst_array : xarray.DataArray
        LST data
    ndvi_array : xarray.DataArray
        NDVI data
        
    Returns:
    --------
    float : Pearson correlation coefficient
    """
    # Flatten arrays
    lst_flat = lst_array.values.flatten()
    ndvi_flat = ndvi_array.values.flatten()
    
    # Remove NaN values
    valid_mask = ~(np.isnan(lst_flat) | np.isnan(ndvi_flat))
    lst_valid = lst_flat[valid_mask]
    ndvi_valid = ndvi_flat[valid_mask]
    
    if len(lst_valid) < 2:
        return 0.0
    
    # Calculate correlation
    correlation_matrix = np.corrcoef(lst_valid, ndvi_valid)
    correlation = correlation_matrix[0, 1]
    
    return float(correlation)
