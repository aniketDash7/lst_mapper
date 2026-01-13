import xarray as xr
import numpy as np

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
