// ====================================
// UHI Monitor - Main Application
// ====================================

// Global State
const state = {
    map: null,
    currentLocation: null,
    lstLayer: null,
    ndviLayer: null,
    currentBounds: null,
    analysisData: null,
};

// API Base URL (change if deployed)
const API_BASE = window.location.origin;

// ====================================
// Initialization
// ====================================

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initEventListeners();
    initDatePickers();
    // Auto-search for a default location (optional)
    // searchLocation('Phoenix, Arizona');
});

// ====================================
// Map Initialization
// ====================================

function initMap() {
    // Initialize Leaflet map
    state.map = L.map('map', {
        center: [20, 0],
        zoom: 3,
        zoomControl: true,
        minZoom: 2,
        maxZoom: 18,
    });

    // Add satellite basemap (ESRI World Imagery)
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri',
        maxZoom: 18,
    }).addTo(state.map);

    // Add click handler for map
    state.map.on('click', handleMapClick);

    console.log('✅ Map initialized');
}

// ====================================
// Event Listeners
// ====================================

function initEventListeners() {
    // Search input
    const searchInput = document.getElementById('location-search');
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value.trim();
            if (query) {
                searchLocation(query);
            }
        }
    });

    // Analyze button
    document.getElementById('analyze-btn').addEventListener('click', handleAnalyze);

    // Close stats panel
    document.getElementById('close-stats').addEventListener('click', () => {
        document.getElementById('stats-panel').style.display = 'none';
    });

    // Layer toggles
    document.getElementById('toggle-lst').addEventListener('change', (e) => {
        if (state.lstLayer) {
            if (e.target.checked) {
                state.map.addLayer(state.lstLayer);
            } else {
                state.map.removeLayer(state.lstLayer);
            }
        }
        updateLegend();
    });

    document.getElementById('toggle-ndvi').addEventListener('change', (e) => {
        if (state.ndviLayer) {
            if (e.target.checked) {
                state.map.addLayer(state.ndviLayer);
            } else {
                state.map.removeLayer(state.ndviLayer);
            }
        }
        updateLegend();
    });

    // Opacity slider
    const opacitySlider = document.getElementById('layer-opacity');
    opacitySlider.addEventListener('input', (e) => {
        const opacity = e.target.value / 100;
        document.getElementById('opacity-value').textContent = `${e.target.value}%`;

        if (state.lstLayer) {
            state.lstLayer.setOpacity(opacity);
        }
        if (state.ndviLayer) {
            state.ndviLayer.setOpacity(opacity);
        }
    });
}

// ====================================
// Legend Management
// ====================================

function updateLegend() {
    const legendPanel = document.getElementById('legend-panel');
    const lstLegend = document.getElementById('lst-legend');
    const ndviLegend = document.getElementById('ndvi-legend');

    const lstToggle = document.getElementById('toggle-lst').checked;
    const ndviToggle = document.getElementById('toggle-ndvi').checked;

    // Show/hide individual legend items
    lstLegend.style.display = (lstToggle && state.lstLayer) ? 'block' : 'none';
    ndviLegend.style.display = (ndviToggle && state.ndviLayer) ? 'block' : 'none';

    // Show legend panel if any layer is visible
    if ((lstToggle && state.lstLayer) || (ndviToggle && state.ndviLayer)) {
        legendPanel.style.display = 'block';
    } else {
        legendPanel.style.display = 'none';
    }
}

// ====================================
// Date Pickers
// ====================================

function initDatePickers() {
    const today = new Date();
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(today.getMonth() - 6);

    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');

    startDate.value = formatDate(sixMonthsAgo);
    endDate.value = formatDate(today);
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// ====================================
// Location Search
// ====================================

async function searchLocation(query) {
    showLoading('Searching location...', 'Geocoding request');

    try {
        const response = await fetch(`${API_BASE}/api/search-location`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        const result = await response.json();

        if (!result.success) {
            showToast('Error', result.error || 'Location not found', 'error');
            hideLoading();
            return;
        }

        const location = result.location;
        state.currentLocation = location;

        // Update UI
        document.getElementById('selected-location').style.display = 'block';
        document.getElementById('location-name').textContent = location.name;
        document.getElementById('location-coords').textContent =
            `${location.lat.toFixed(4)}°, ${location.lon.toFixed(4)}°`;

        // Fly to location
        const [minLon, minLat, maxLon, maxLat] = location.bbox;
        const bounds = [[minLat, minLon], [maxLat, maxLon]];
        state.map.fitBounds(bounds, { padding: [50, 50] });

        showToast('Success', `Found ${location.name}`, 'success');
        hideLoading();

    } catch (error) {
        console.error('Search error:', error);
        showToast('Error', 'Failed to search location', 'error');
        hideLoading();
    }
}

// ====================================
// Map Click Handler
// ====================================

async function handleMapClick(e) {
    const { lat, lng: lon } = e.latlng;

    showLoading('Reverse geocoding...', 'Finding location');

    try {
        const response = await fetch(`${API_BASE}/api/reverse-geocode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ lat, lon }),
        });

        const result = await response.json();

        if (!result.success) {
            hideLoading();
            // Still set location even if geocoding fails
            state.currentLocation = {
                name: `Location (${lat.toFixed(4)}, ${lon.toFixed(4)})`,
                lat,
                lon,
                bbox: [lon - 0.15, lat - 0.15, lon + 0.15, lat + 0.15],
            };
        } else {
            const location = result.location;
            state.currentLocation = location;

            document.getElementById('selected-location').style.display = 'block';
            document.getElementById('location-name').textContent = location.name;
            document.getElementById('location-coords').textContent =
                `${location.lat.toFixed(4)}°, ${location.lon.toFixed(4)}°`;
        }

        hideLoading();
        showToast('Location Selected', 'Click "Analyze" to process satellite data', 'info');

    } catch (error) {
        console.error('Reverse geocode error:', error);
        hideLoading();
    }
}

// ====================================
// Analysis
// ====================================

async function handleAnalyze() {
    if (!state.currentLocation) {
        showToast('No Location', 'Please search for or click a location first', 'error');
        return;
    }

    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    if (!startDate || !endDate) {
        showToast('Invalid Dates', 'Please select valid date range', 'error');
        return;
    }

    showLoading('Analyzing region...', 'Fetching satellite data from Microsoft Planetary Computer');

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                bbox: state.currentLocation.bbox,
                start_date: startDate,
                end_date: endDate,
                max_cloud_cover: 15,
            }),
        });

        const result = await response.json();

        if (!result.success) {
            showToast('Analysis Failed', result.error || 'Could not process data', 'error');
            hideLoading();
            return;
        }

        state.analysisData = result.data;

        updateLoadingText('Processing LST and NDVI...', 'Rendering visualization');

        // Add layers to map
        await addDataLayers(result.data);

        // Update statistics panel
        updateStatsPanel(result.data);

        // Show stats panel
        document.getElementById('stats-panel').style.display = 'block';

        hideLoading();
        showToast('Analysis Complete', 'LST and NDVI layers added to map', 'success');

    } catch (error) {
        console.error('Analysis error:', error);
        showToast('Error', 'Failed to analyze region', 'error');
        hideLoading();
    }
}

// ====================================
// Data Layer Management
// ====================================

async function addDataLayers(data) {
    // Remove existing layers
    if (state.lstLayer) {
        state.map.removeLayer(state.lstLayer);
    }
    if (state.ndviLayer) {
        state.map.removeLayer(state.ndviLayer);
    }

    const opacity = document.getElementById('layer-opacity').value / 100;

    // Add LST layer
    const lstImageUrl = `data:image/png;base64,${data.lst.image}`;
    state.lstLayer = L.imageOverlay(lstImageUrl, data.lst.bounds, {
        opacity: opacity,
        interactive: false,
    });

    // Add NDVI layer
    const ndviImageUrl = `data:image/png;base64,${data.ndvi.image}`;
    state.ndviLayer = L.imageOverlay(ndviImageUrl, data.ndvi.bounds, {
        opacity: opacity,
        interactive: false,
    });

    // Add to map (check toggles)
    if (document.getElementById('toggle-lst').checked) {
        state.lstLayer.addTo(state.map);
    }
    if (document.getElementById('toggle-ndvi').checked) {
        state.ndviLayer.addTo(state.map);
    }

    // Fit bounds
    state.map.fitBounds(data.lst.bounds, { padding: [50, 50] });

    // Update legend
    updateLegend();
}

// ====================================
// Statistics Panel
// ====================================

function updateStatsPanel(data) {
    // Scene info
    document.getElementById('scene-date').textContent = data.scene_date;
    document.getElementById('cloud-cover').textContent = `${data.cloud_cover.toFixed(1)}%`;

    // LST statistics
    document.getElementById('lst-min').textContent = `${data.lst.statistics.min.toFixed(1)}°C`;
    document.getElementById('lst-max').textContent = `${data.lst.statistics.max.toFixed(1)}°C`;
    document.getElementById('lst-mean').textContent = `${data.lst.statistics.mean.toFixed(1)}°C`;
    document.getElementById('lst-std').textContent = `${data.lst.statistics.std.toFixed(1)}°C`;

    // NDVI statistics
    document.getElementById('ndvi-min').textContent = data.ndvi.statistics.min.toFixed(3);
    document.getElementById('ndvi-max').textContent = data.ndvi.statistics.max.toFixed(3);
    document.getElementById('ndvi-mean').textContent = data.ndvi.statistics.mean.toFixed(3);
    document.getElementById('ndvi-std').textContent = data.ndvi.statistics.std.toFixed(3);

    // Correlation
    const correlation = data.correlation;
    document.getElementById('correlation').textContent = correlation.toFixed(3);

    // Update correlation bar (convert -1 to 1 range to 0 to 100%)
    const fillPercent = ((Math.abs(correlation) * 100));
    document.getElementById('correlation-fill').style.width = `${fillPercent}%`;

    // Interpretation
    const absCorr = Math.abs(correlation);
    let interpretation = '';
    if (absCorr > 0.7) {
        interpretation = 'Strong';
    } else if (absCorr > 0.4) {
        interpretation = 'Moderate';
    } else {
        interpretation = 'Weak';
    }
    interpretation += correlation < 0 ? ' negative correlation' : ' positive correlation';
    interpretation += ' - ' + (correlation < 0 ?
        'Higher vegetation leads to lower temperature (cooling effect)' :
        'Higher vegetation leads to higher temperature');

    document.getElementById('correlation-text').textContent = interpretation;

    // UHI Magnitude
    document.getElementById('uhi-magnitude').textContent = `${data.uhi_magnitude.toFixed(1)}°C`;
}

// ====================================
// UI Helpers
// ====================================

function showLoading(text = 'Loading...', subtext = '') {
    const overlay = document.getElementById('loading-overlay');
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-subtext').textContent = subtext;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function updateLoadingText(text, subtext = '') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-subtext').textContent = subtext;
}

function showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
    `;

    container.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

console.log('✅ UHI Monitor application initialized');
