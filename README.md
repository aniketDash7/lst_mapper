# 🌡️ CityCool: Urban Heat Island (UHI) Monitor

**CityCool** is a geospatial data science tool that monitors Urban Heat Islands using satellite imagery. It allows users to visualize how vegetation cover (NDVI) directly correlates with Land Surface Temperature (LST) in any city around the world.

## 🚀 Features
- **Global Coverage**: Analyze any city using real-time search via Nominatim.
- **Satellite Intelligence**: Fetches **Landsat 8/9 Level 2 Science Products** (Surface Temperature & Surface Reflectance) directly from the [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/).
- **Live Processing**:
  - **LST Calculation**: Converts thermal infrared digital numbers to degrees Celsius.
  - **NDVI Calculation**: Computes vegetation health from Red and Near-Infrared bands.
- **Interactive Dashboard**: Built with Streamlit for easy, web-based interaction.

## 🛠️ Tech Stack
- **Python 3.10+**
- **Data Access**: `pystac-client`, `odc-stac`, `planetary-computer`
- **Geospatial Processing**: `xarray`, `rioxarray`, `geopandas`
- **Visualization**: `streamlit`, `matplotlib`, `folium`

## 📦 Installation

1. **Clone the repository** (or navigate to the folder):
   ```bash
   cd UHI-Monitor
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If you are using Anaconda, ensure you are in the correct environment.*

## 🚦 Usage

Run the dashboard with one command:

```bash
streamlit run app.py
```

1. **Enter a City**: e.g., "Bangalore", "New York", "Tokyo".
2. **Select Date Range**: Choose a summer month for the most distinct Heat Island effect.
3. **Analyze**: The app will download the clearest satellite image and generate two maps:
   - **Left**: Land Surface Temperature (°C)
   - **Right**: Normalized Difference Vegetation Index (NDVI)

## 🧮 How It Works

### 1. Data Ingestion (`src.data_loader`)
We query the Microsoft Planetary Computer STAC API for the `landsat-c2-l2` collection. We filter by:
- **Location**: Bounding box of the selected city.
- **Cloud Cover**: We sort images to find the one with the least clouds (<10% default).

### 2. Physical Processing (`src.processor`)
We use **Landsat Collection 2** scaling factors to derive physical units:

**Land Surface Temperature (LST):**
$$ T_{Celsius} = (DN \times 0.003418 + 149.0) - 273.15 $$
*Signal Source: Band 10 (TIRS)*

**Vegetation Index (NDVI):**
$$ NDVI = \frac{NIR - Red}{NIR + Red} $$
*Signal Source: Band 5 (NIR) and Band 4 (Red)*

## 📂 Project Structure
```
UHI-Monitor/
├── app.py              # Main dashboard script
├── requirements.txt    # Python dependencies
├── src/
│   ├── data_loader.py  # STAC API search & loading logic
│   ├── processor.py    # Math formulas for LST & NDVI
│   └── utils.py        # Geocoding helper (City -> Lat/Lon)
└── README.md           # This file
```
