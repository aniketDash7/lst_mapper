"""
UHI-Monitor Flask Application
Professional web interface for Urban Heat Island monitoring
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import datetime
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import traceback

from src.utils import search_locations, get_city_bbox, reverse_geocode
from src.data_loader import fetch_landsat_data
from src.processor import (
    calculate_lst, 
    calculate_ndvi, 
    generate_lst_image, 
    generate_ndvi_image,
    calculate_statistics,
    lst_ndvi_correlation
)

app = Flask(__name__)
CORS(app)  # Enable CORS for API endpoints

# Configure Flask
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'UHI-Monitor API',
        'version': '2.0.0'
    })


@app.route('/api/search-location', methods=['POST'])
def search_location():
    """
    Search for a location by name and return coordinates + bounding box
    
    Request JSON:
    {
        "query": "Phoenix, Arizona"
    }
    
    Response JSON:
    {
        "success": true,
        "location": {
            "name": "Phoenix, Arizona, USA",
            "lat": 33.4484,
            "lon": -112.0740,
            "bbox": [minLon, minLat, maxLon, maxLat]
        }
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter is required'
            }), 400
        
        # Search for location
        result = search_locations(query)
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'Location "{query}" not found. Please try a different search.'
            }), 404
        
        return jsonify({
            'success': True,
            'location': result
        })
        
    except Exception as e:
        print(f"Error in search_location: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error during location search'
        }), 500


@app.route('/api/reverse-geocode', methods=['POST'])
def reverse_geocode_endpoint():
    """
    Reverse geocode coordinates to get location name and bbox
    
    Request JSON:
    {
        "lat": 33.4484,
        "lon": -112.0740
    }
    """
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')
        
        if lat is None or lon is None:
            return jsonify({
                'success': False,
                'error': 'Latitude and longitude are required'
            }), 400
        
        result = reverse_geocode(lat, lon)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Could not reverse geocode coordinates'
            }), 404
        
        return jsonify({
            'success': True,
            'location': result
        })
        
    except Exception as e:
        print(f"Error in reverse_geocode: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Internal server error during reverse geocoding'
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze LST and NDVI for a given location and date range
    
    Request JSON:
    {
        "bbox": [minLon, minLat, maxLon, maxLat],
        "start_date": "2024-06-01",
        "end_date": "2024-08-31",
        "max_cloud_cover": 15
    }
    
    Response JSON:
    {
        "success": true,
        "data": {
            "scene_date": "2024-07-15",
            "cloud_cover": 5.2,
            "lst": {
                "image": "base64_encoded_png",
                "bounds": [[minLat, minLon], [maxLat, maxLon]],
                "statistics": {...}
            },
            "ndvi": {
                "image": "base64_encoded_png",
                "bounds": [[minLat, minLon], [maxLat, maxLon]],
                "statistics": {...}
            },
            "correlation": -0.72
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        bbox = data.get('bbox')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        max_cloud_cover = data.get('max_cloud_cover', 15)
        
        if not bbox or len(bbox) != 4:
            return jsonify({
                'success': False,
                'error': 'Valid bounding box is required'
            }), 400
        
        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'error': 'Start date and end date are required'
            }), 400
        
        print(f"Analyzing region: bbox={bbox}, dates={start_date} to {end_date}")
        
        # Fetch satellite data
        ds = fetch_landsat_data(bbox, start_date, end_date, max_cloud_cover)
        
        if ds is None:
            return jsonify({
                'success': False,
                'error': 'No suitable satellite data found. Try increasing cloud cover tolerance or expanding date range.'
            }), 404
        
        # Select first (clearest) scene if multiple exist
        if 'time' in ds.dims:
            scene = ds.isel(time=0)
            scene_date = str(scene.time.values)[:10]
        else:
            scene = ds
            scene_date = start_date
        
        # Calculate LST and NDVI
        print("Calculating LST and NDVI...")
        lst = calculate_lst(scene)
        ndvi = calculate_ndvi(scene)
        
        # Generate images
        print("Generating visualization images...")
        lst_image_b64, lst_bounds = generate_lst_image(lst)
        ndvi_image_b64, ndvi_bounds = generate_ndvi_image(ndvi)
        
        print(f"Generated LST bounds: {lst_bounds}")
        print(f"Generated NDVI bounds: {ndvi_bounds}")
        
        # Calculate statistics
        lst_stats = calculate_statistics(lst)
        ndvi_stats = calculate_statistics(ndvi)
        
        # Calculate correlation
        correlation = lst_ndvi_correlation(lst, ndvi)
        
        # Prepare response
        response_data = {
            'success': True,
            'data': {
                'scene_date': scene_date,
                'cloud_cover': float(max_cloud_cover),  # Could extract actual cloud cover from metadata
                'lst': {
                    'image': lst_image_b64,
                    'bounds': lst_bounds,
                    'statistics': lst_stats
                },
                'ndvi': {
                    'image': ndvi_image_b64,
                    'bounds': ndvi_bounds,
                    'statistics': ndvi_stats
                },
                'correlation': correlation,
                'uhi_magnitude': lst_stats['max'] - lst_stats['min']
            }
        }
        
        print("Analysis complete!")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in analyze: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Starting UHI-Monitor Flask Application...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
