# CityCool: Urban Heat Island (UHI) Monitor

**Version 2.0** | A modern web application for monitoring Urban Heat Islands using real-time satellite data

## Features
- **Global Coverage**: Analyze any city using real-time search via Nominatim.
- **Satellite Intelligence**: Fetches **Landsat 8/9 Level 2 Science Products** (Surface Temperature & Surface Reflectance) directly from the [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/).
- **Live Processing**:
  - **LST Calculation**: Converts thermal infrared digital numbers to degrees Celsius.
  - **NDVI Calculation**: Computes vegetation health from Red and Near-Infrared bands.
- **Interactive Dashboard**: Built with Streamlit for easy, web-based interaction.

## Tech Stack
- **Python 3.10+**
- **Data Access**: `pystac-client`, `odc-stac`, `planetary-computer`
- **Geospatial Processing**: `xarray`, `rioxarray`, `geopandas`
- **Visualization**: `streamlit`, `matplotlib`, `folium`

## Installation

UHI Monitor is a professional full-stack web application that analyzes **Urban Heat Islands** using Landsat 8/9 satellite imagery. It provides an intuitive, map-based interface for visualizing Land Surface Temperature (LST) and vegetation health (NDVI) anywhere in the world.

### Key Features

✅ **Full-Page Interactive Map** - Powered by Leaflet.js with satellite basemap  
✅ **Global Coverage** - Analyze any location worldwide  
✅ **Real-Time Satellite Data** - Fetches latest Landsat imagery from Microsoft Planetary Computer  
✅ **Precise Location Selection** - Search by city or click anywhere on the map  
✅ **Professional UI** - Dark theme with glassmorphism design  
✅ **Comprehensive Analytics** - LST/NDVI statistics and correlation analysis  
✅ **Interactive Layers** - Toggle and adjust opacity of temperature and vegetation overlays  

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone or navigate to the repository
cd UHI-Monitor

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

## How It Works

Open your browser and navigate to: **http://localhost:5000**

---

## 📖 How to Use

### 1. Select a Location

**Option A: Search**
- Type a city name in the search box (e.g., "Phoenix, Arizona")
- Press Enter to geocode and zoom to the location

**Option B: Map Click**
- Click anywhere on the map to select precise coordinates
- The app will reverse-geocode the location

### 2. Choose Date Range

- Use the date pickers in the header
- Select a date range (e.g., summer months for strongest UHI effects)
- Recommended: Last 6 months for best data availability

### 3. Analyze

- Click the **"Analyze"** button
- The app will:
  - Fetch the clearest Landsat scene from Microsoft Planetary Computer
  - Calculate Land Surface Temperature (LST)
  - Calculate vegetation index (NDVI)
  - Display overlay layers on the map
  - Show detailed statistics in the right panel

### 4. Explore Results

- **Toggle layers**: Show/hide LST and NDVI layers
- **Adjust opacity**: Use the slider to control layer transparency
- **View statistics**: Min, max, mean, correlation, and UHI magnitude
- **Compare**: Red areas are hot/bare, green areas are cool/vegetated

---

## 🛠️ Technology Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **Flask** | RESTful API server |
| **pystac-client** | STAC catalog search |
| **odc-stac** | Satellite data loading |
| **xarray** | Multi-dimensional arrays |
| **matplotlib** | Image generation |
| **geopy** | Geocoding (Nominatim) |

### Frontend

| Technology | Purpose |
|------------|---------|
| **Leaflet.js** | Interactive maps |
| **Vanilla JavaScript** | Client-side logic |
| **Modern CSS** | Glassmorphism design |
| **ESRI World Imagery** | Satellite basemap |

### Data Source

- **Microsoft Planetary Computer**: Landsat Collection 2 Level-2
- **Landsat 8/9**: Thermal and optical bands
- **STAC API**: Cloud-native geospatial catalog

---

## 📊 Scientific Background

### Land Surface Temperature (LST)

LST measures the radiative temperature of the Earth's surface. It differs from air temperature and is crucial for:
- Urban heat island analysis
- Climate change monitoring
- Agricultural drought assessment
- Energy balance studies

**Our Formula**:
```
LST (Celsius) = (DN × 0.00341802 + 149.0) - 273.15
```

Where DN is the digital number from Landsat Band 10 (thermal infrared).

### NDVI (Vegetation Index)

NDVI indicates vegetation health and density:

```
NDVI = (NIR - Red) / (NIR + Red)
```

**Interpretation**:
- **-1 to 0**: Water, clouds
- **0 to 0.2**: Bare soil, rock
- **0.2 to 0.4**: Sparse vegetation
- **0.4 to 0.7**: Moderate to dense vegetation
- **0.7 to 1.0**: Very dense, healthy vegetation

### Urban Heat Island Effect

Urban areas are typically **2-10°C warmer** than surrounding rural areas due to:
- Dark surfaces absorbing heat (asphalt, buildings)
- Reduced vegetation and evaporative cooling
- Waste heat from human activities
- Altered wind patterns

**Our Analysis**: We calculate UHI magnitude as the temperature difference between hottest and coolest areas.

---

## 🔧 API Documentation

### Endpoints

#### `GET /`
Serves the main HTML application.

#### `POST /api/search-location`
Geocode a location by name.

**Request**:
```json
{
  "query": "Phoenix, Arizona"
}
```

**Response**:
```json
{
  "success": true,
  "location": {
    "name": "Phoenix, Arizona, USA",
    "lat": 33.4484,
    "lon": -112.0740,
    "bbox": [-112.2091, 33.3133, -111.9389, 33.5835]
  }
}
```

#### `POST /api/reverse-geocode`
Reverse geocode coordinates to location name.

**Request**:
```json
{
  "lat": 33.4484,
  "lon": -112.0740
}
```

#### `POST /api/analyze`
Process LST and NDVI for a region.

**Request**:
```json
{
  "bbox": [-112.2091, 33.3133, -111.9389, 33.5835],
  "start_date": "2024-06-01",
  "end_date": "2024-08-31",
  "max_cloud_cover": 15
}
```

**Response**: Returns base64-encoded images, bounds, statistics, and correlation data.

---

<<<<<<< HEAD
## 📂 Project Structure

=======
## Project Structure
>>>>>>> 1596af02ec96fdfc99271aaeb95947a1a6b8d505
```
UHI-Monitor/
├── flask_app.py              # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # Satellite data fetching (pystac-client, odc-stac)
│   ├── processor.py          # LST/NDVI calculations + image generation
│   └── utils.py              # Geocoding utilities (geopy)
├── templates/
│   └── index.html            # Main web interface
└── static/
    ├── css/
    │   └── style.css         # Glassmorphism styling
    └── js/
        └── app.js            # Frontend application logic
```

---

## 🎨 Design Philosophy

### Visual Excellence

- **Dark Mode**: Reduces eye strain, looks professional
- **Glassmorphism**: Translucent panels with backdrop blur
- **Vibrant Gradients**: Purple-blue to pink accents
- **Smooth Animations**: Hover effects, transitions, loading states

### User Experience

- **Full-Page Map**: Content is the focus, not chrome
- **Minimal Clicks**: Search or click, then analyze
- **Instant Feedback**: Loading states, toast notifications
- **Responsive**: Works on desktop and mobile

### Code Quality

- **Well-Documented**: Comprehensive docstrings and comments
- **Error Handling**: Graceful failures with user-friendly messages
- **RESTful API**: Standard HTTP methods and status codes
- **Modular**: Separation of concerns (data, processing, UI)

---

## 🔬 Example Use Cases

### 1. Urban Planning
Identify heat hotspots in cities to prioritize:
- Green infrastructure (parks, trees)
- Cool pavement deployment
- Building energy efficiency programs

### 2. Public Health
Assess heat exposure risks for:
- Vulnerable populations (elderly, children)
- Outdoor workers
- Heat wave emergency planning

### 3. Climate Research
Track long-term trends:
- Urban warming patterns
- Land use change impacts
- Vegetation loss correlation with temperature

### 4. Agriculture
Monitor crop stress:
- Irrigation effectiveness
- Drought impact assessment
- Microclimate analysis

---

## 🚦 Troubleshooting

### "Failed to fetch" Error
- **Cause**: Flask server not running or crashed
- **Solution**: Restart `python flask_app.py`

### "No suitable satellite data found"
- **Cause**: High cloud cover or no Landsat coverage
- **Solution**: 
  - Expand date range
  - Increase `max_cloud_cover` parameter
  - Try different season (summer usually has less clouds)

### Layers not appearing on map
- **Cause**: Bounds calculation issue or data all NaN
- **Solution**: Check browser console for errors, verify location has Landsat coverage

### Map zooms out too much
- **Cause**: Incorrect coordinate system or bounds
- **Solution**: Fixed in v2.0 with WGS84 CRS

---

## 📈 Performance

### Typical Response Times

- **Location Search**: 0.5-2 seconds (depends on Nominatim)
- **Satellite Data Fetch**: 3-10 seconds (depends on scene size)
- **LST/NDVI Processing**: 2-5 seconds
- **Total Analysis Time**: 5-15 seconds

### Data Sizes

- **Input**: ~50-200 MB (Landsat scene, 4 bands)
- **Output Images**: ~200-500 KB each (PNG, base64)
- **JSON Response**: ~1-2 MB

---

## 🌐 Deployment

### Development (Current)

```bash
python flask_app.py
# Runs on http://localhost:5000
# Debug mode enabled
```

### Production (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app
```

For production deployment, also consider:
- **Nginx**: Reverse proxy for static files and SSL
- **Docker**: Containerization for portability
- **Redis**: Caching for geocoding results
- **Logging**: Error tracking (e.g., Sentry)

---

## 📝 License

MIT License - Feel free to use, modify, and distribute!

---

## 🙏 Acknowledgments

- **Microsoft Planetary Computer** - Free Landsat data access
- **Leaflet.js** - Excellent mapping library
- **OpenStreetMap** - Nominatim geocoding service
- **ESRI** - World Imagery basemap tiles
- **NASA/USGS** - Landsat satellite program

---

## 📚 Additional Resources

- [Technical Explainer](technical_explainer.md) - Deep dive into architecture and implementation
- [Landsat Collection 2 Documentation](https://www.usgs.gov/landsat-missions/landsat-collection-2)
- [STAC Specification](https://stacspec.org/)
- [Leaflet.js Documentation](https://leafletjs.com/)

---

## 📧 Support

For questions or issues:
1. Check the Technical Explainer document
2. Review troubleshooting section
3. Examine browser console and Flask logs

---

**Built with ❤️ using Python, Flask, and modern web technologies**

**Version**: 2.0.0  
**Last Updated**: January 2026
