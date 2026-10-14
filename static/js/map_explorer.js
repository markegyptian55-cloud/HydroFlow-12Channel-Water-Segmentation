/**
 * HydroFlow Interactive Earth Satellite Explorer
 * Powered by Leaflet.js and Real-Time /predict_geo Satellite Segmentation
 * Strict Honesty: Zero simulated/fake overlays or hardcoded numbers
 */

let hydroMap = null;
let currentGeoOverlay = null;
let currentBbox = null;
let currentMarker = null;
let currentAreaMode = 'small'; // 'small', 'medium', 'large', 'viewport'

let selectedPoint = {
    lat: 22.4500,
    lon: 31.8500,
    zoom: 12,
    name: 'Lake Nasser (Egypt)'
};

const PRESET_LOCATIONS = {
    'nasser': { name: 'Lake Nasser (Egypt)', lat: 22.4500, lon: 31.8500, zoom: 12 },
    'aswan': { name: 'Aswan High Dam (Egypt)', lat: 23.9700, lon: 32.8800, zoom: 13 },
    'cairo_nile': { name: 'Nile River (Cairo)', lat: 30.0440, lon: 31.2350, zoom: 14 },
    'suez': { name: 'Suez Canal / Bitter Lakes', lat: 30.3400, lon: 32.3600, zoom: 12 },
    'lake_mead': { name: 'Lake Mead (USA)', lat: 36.1400, lon: -114.4300, zoom: 12 },
    'lake_como': { name: 'Lake Como (Italy)', lat: 45.9800, lon: 9.2600, zoom: 12 }
};

document.addEventListener('DOMContentLoaded', () => {
    initLeafletMap();
    initMapControls();
});

/* ==========================================================================
   1. LEAFLET MAP INITIALIZATION
   ========================================================================== */
function initLeafletMap() {
    const mapElement = document.getElementById('leaflet-map');
    if (!mapElement) return;

    hydroMap = L.map('leaflet-map', {
        center: [selectedPoint.lat, selectedPoint.lon],
        zoom: selectedPoint.zoom,
        zoomControl: true
    });

    // High-resolution Esri World Satellite Imagery Basemap
    L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
            attribution: '&copy; Esri, Maxar, Earthstar Geographics, USDA, USGS',
            maxZoom: 18,
            minZoom: 3
        }
    ).addTo(hydroMap);

    window.hydroMap = hydroMap;

    // Place initial beacon at Lake Nasser
    placeBeacon(selectedPoint.lat, selectedPoint.lon, selectedPoint.name);

    // Map Click: reposition beacon only (NO auto-analysis)
    hydroMap.on('click', (e) => {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;
        const zoom = hydroMap.getZoom();

        selectedPoint = { lat, lon, zoom, name: 'Target Beacon' };
        placeBeacon(lat, lon, 'Target Beacon');
    });

    hydroMap.on('move', () => {
        updateMapCenterDisplay();
    });
    updateMapCenterDisplay();
}

function updateMapCenterDisplay() {
    if (!hydroMap) return;
    const center = hydroMap.getCenter();
    const zoom = hydroMap.getZoom();

    const gpsDisplay = document.getElementById('map-gps-display');
    if (gpsDisplay) {
        gpsDisplay.textContent = `Lat: ${center.lat.toFixed(4)}° | Lon: ${center.lng.toFixed(4)}° | Zoom: ${zoom}`;
    }
}

function placeBeacon(lat, lon, name = 'Target Beacon') {
    if (currentMarker) {
        hydroMap.removeLayer(currentMarker);
    }

    // High-visibility SVG Beacon Marker
    const icon = L.divIcon({
        className: 'custom-beacon-div',
        html: `
            <div style="position: relative; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                <span style="position: absolute; width: 28px; height: 28px; border-radius: 50%; background: var(--water-data); opacity: 0.35; animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
                <span style="position: relative; width: 14px; height: 14px; border-radius: 50%; background: var(--water-data); border: 2px solid #ffffff; box-shadow: 0 0 8px rgba(0,0,0,0.5);"></span>
            </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
    });

    currentMarker = L.marker([lat, lon], { icon }).addTo(hydroMap);

    const modeLabel = currentAreaMode === 'viewport' ? 'Screen' : currentAreaMode.toUpperCase();

    // Popup with manual trigger
    const popupHtml = `
        <div style="font-family: -apple-system, sans-serif; font-size: 12px; color: #0f172a; padding: 4px; text-align: center; min-width: 180px;">
            <div style="font-weight: 700; margin-bottom: 2px; color: #00667e;">${name}</div>
            <div style="font-family: monospace; font-size: 11px; color: #64748b; margin-bottom: 6px;">
                ${lat.toFixed(4)}°, ${lon.toFixed(4)}°
            </div>
            <button onclick="window.triggerMapAnalysis()" style="width: 100%; padding: 6px 10px; background: #00667e; color: #ffffff; border: none; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer;">
                Analyze Surface Water
            </button>
        </div>
    `;

    currentMarker.bindPopup(popupHtml, {
        closeButton: true,
        autoPan: true,
        offset: [0, -10]
    });

    const statusBadge = document.getElementById('map-target-status');
    if (statusBadge) {
        statusBadge.textContent = `Target [${lat.toFixed(2)}°, ${lon.toFixed(2)}°]`;
    }
}

window.triggerMapAnalysis = function() {
    if (selectedPoint) {
        executeGeoInference(selectedPoint.lat, selectedPoint.lon, hydroMap.getZoom());
    }
};

/* ==========================================================================
   2. CONTROLS, SEARCH & AREA MODES
   ========================================================================== */
function initMapControls() {
    // Footprint Mode Selector
    document.querySelectorAll('.area-mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.area-mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAreaMode = btn.dataset.areaMode;
        });
    });

    // Preset dropdown
    const quickJump = document.getElementById('map-quick-jump');
    if (quickJump) {
        quickJump.addEventListener('change', (e) => {
            const loc = PRESET_LOCATIONS[e.target.value];
            if (loc && hydroMap) {
                selectedPoint = { ...loc };
                hydroMap.flyTo([loc.lat, loc.lon], loc.zoom, { duration: 1.2 });
                setTimeout(() => {
                    placeBeacon(loc.lat, loc.lon, loc.name);
                }, 1300);
            }
        });
    }

    // Geocoding Search
    const searchInput = document.getElementById('map-search-input');
    const searchBtn = document.getElementById('btn-search-location');
    if (searchBtn && searchInput) {
        const doSearch = () => handleSearchLocation(searchInput.value);
        searchBtn.addEventListener('click', doSearch);
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') doSearch();
        });
    }

    // Manual Analysis Trigger Button
    const analyzeBtn = document.getElementById('btn-segment-selected');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => {
            if (selectedPoint) {
                executeGeoInference(selectedPoint.lat, selectedPoint.lon, hydroMap.getZoom());
            }
        });
    }

    // Opacity Slider
    const opacitySlider = document.getElementById('map-overlay-opacity');
    if (opacitySlider) {
        opacitySlider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            if (currentGeoOverlay) {
                currentGeoOverlay.setOpacity(val);
            }
        });
    }

    // Retry Button
    const retryBtn = document.getElementById('map-retry-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            if (selectedPoint) {
                executeGeoInference(selectedPoint.lat, selectedPoint.lon, hydroMap.getZoom());
            }
        });
    }
}

async function handleSearchLocation(query) {
    if (!query || !query.trim()) return;
    const clean = query.trim();

    // Check GPS pattern (e.g. "22.45, 31.85")
    const coordMatch = clean.match(/^([-+]?\d*\.?\d+)[,\s]+([-+]?\d*\.?\d+)$/);
    if (coordMatch) {
        const lat = parseFloat(coordMatch[1]);
        const lon = parseFloat(coordMatch[2]);
        if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
            selectedPoint = { lat, lon, zoom: 12, name: `GPS [${lat.toFixed(3)}°, ${lon.toFixed(3)}°]` };
            hydroMap.flyTo([lat, lon], 12, { duration: 1.2 });
            setTimeout(() => placeBeacon(lat, lon, selectedPoint.name), 1300);
            return;
        }
    }

    // Nominatim OpenStreetMap Geocoding
    try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(clean)}`;
        const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
        if (!res.ok) throw new Error('Geocoding service unavailable');
        const results = await res.json();

        if (results && results.length > 0) {
            const top = results[0];
            const lat = parseFloat(top.lat);
            const lon = parseFloat(top.lon);
            const name = top.display_name.split(',')[0];

            selectedPoint = { lat, lon, zoom: 12, name };
            hydroMap.flyTo([lat, lon], 12, { duration: 1.4 });
            setTimeout(() => placeBeacon(lat, lon, name), 1500);
        } else {
            showNotification(`Location "${clean}" not found. Try GPS coordinates like: 22.45, 31.85`, 'warning');
        }
    } catch (err) {
        showNotification(`Search error: ${err.message}`, 'error');
    }
}

/* ==========================================================================
   3. SATELLITE TILE INFERENCE EXECUTION (STRICTLY HONEST)
   ========================================================================== */
async function executeGeoInference(lat, lon, zoom) {
    const loadingBadge = document.getElementById('map-loading-indicator');
    const metricsPanel = document.getElementById('map-metrics-panel');
    const errorBanner = document.getElementById('map-error-banner');
    const actionLabel = document.getElementById('btn-segment-selected-label');

    if (loadingBadge) loadingBadge.style.display = 'flex';
    if (errorBanner) errorBanner.style.display = 'none';
    if (actionLabel) actionLabel.textContent = 'Segmenting...';

    const threshold = parseFloat(document.getElementById('threshold-slider')?.value || 0.50);

    // Visible viewport bounds
    const boundsObj = hydroMap.getBounds();
    const viewport_bounds = [
        [boundsObj.getSouth(), boundsObj.getWest()],
        [boundsObj.getNorth(), boundsObj.getEast()]
    ];

    const getApiUrl = (endpoint) => window.HYDROFLOW_CONFIG?.apiUrl ? window.HYDROFLOW_CONFIG.apiUrl(endpoint) : endpoint;

    try {
        const resp = await fetch(getApiUrl('/predict_geo'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat,
                lon,
                zoom,
                threshold,
                area_mode: currentAreaMode,
                viewport_bounds
            })
        });

        const contentType = resp.headers.get('content-type') || '';
        let data = null;

        if (resp.ok && contentType.includes('application/json')) {
            data = await resp.json();
        } else {
            let errorMsg = `Server error HTTP ${resp.status}`;
            try {
                if (contentType.includes('application/json')) {
                    const errObj = await resp.json();
                    errorMsg = errObj.error?.message || errObj.error || errorMsg;
                }
            } catch (e) {}
            throw new Error(errorMsg);
        }

        // Clean previous layers
        if (currentGeoOverlay) hydroMap.removeLayer(currentGeoOverlay);
        if (currentBbox) hydroMap.removeLayer(currentBbox);

        // Bounding Box footprint outline
        currentBbox = L.rectangle(data.bounds, {
            color: 'var(--water-data)',
            weight: 2,
            dashArray: '4, 4',
            fillColor: 'var(--water-data)',
            fillOpacity: 0.05
        }).addTo(hydroMap);

        // Overlay transparent PNG mask
        const opacity = parseFloat(document.getElementById('map-overlay-opacity')?.value || 0.85);
        currentGeoOverlay = L.imageOverlay(data.overlay_base64, data.bounds, {
            opacity: opacity,
            interactive: false
        }).addTo(hydroMap);

        // Update telemetry panel
        if (metricsPanel) {
            metricsPanel.style.display = 'block';
            const pctEl = document.getElementById('geo-water-pct');
            const pxEl = document.getElementById('geo-water-px');
            const latEl = document.getElementById('geo-latency');
            if (pctEl) pctEl.textContent = `${data.water_percentage.toFixed(1)}%`;
            if (pxEl) pxEl.textContent = data.water_pixels.toLocaleString();
            if (latEl) latEl.textContent = `${data.latency_ms.toFixed(0)} ms`;
        }

        const statusBadge = document.getElementById('map-target-status');
        if (statusBadge) {
            statusBadge.textContent = `${data.water_percentage.toFixed(1)}% Water`;
        }

    } catch (err) {
        console.warn('Map inference failed:', err);

        // STRICTLY HONEST: NO FAKE WATER CONTOURS OR HARDCODED METRICS
        if (currentGeoOverlay) {
            hydroMap.removeLayer(currentGeoOverlay);
            currentGeoOverlay = null;
        }
        if (currentBbox) {
            hydroMap.removeLayer(currentBbox);
            currentBbox = null;
        }
        if (metricsPanel) metricsPanel.style.display = 'none';

        if (errorBanner) {
            errorBanner.style.display = 'flex';
            const msgEl = document.getElementById('map-error-msg');
            if (msgEl) {
                msgEl.textContent = `Analysis failed: ${err.message}. Live satellite segmentation requires active HydroFlow backend.`;
            }
        }

        const statusBadge = document.getElementById('map-target-status');
        if (statusBadge) statusBadge.textContent = 'Service Offline';

    } finally {
        if (loadingBadge) loadingBadge.style.display = 'none';
        if (actionLabel) actionLabel.textContent = 'Analyze Target Point';
    }
}
