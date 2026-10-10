/**
 * HydroFlow Interactive Earth Satellite Explorer
 * Powered by Leaflet.js and Real-Time /predict_geo Satellite Segmentation
 * Supports 4 Analysis Footprint Modes: Small 1x, Medium 2x, Large 3x, and Full Viewport
 */

let hydroMap = null;
let currentGeoOverlay = null;
let currentBbox = null;
let currentMarker = null;
let currentAreaMode = 'small'; // 'small', 'medium', 'large', 'viewport'

let selectedPoint = {
    lat: 22.45,
    lon: 31.85,
    zoom: 12,
    name: 'Lake Nasser (Egypt)'
};

const PRESET_LOCATIONS = {
    'nasser': { name: 'Lake Nasser (Egypt)', lat: 22.45, lon: 31.85, zoom: 12 },
    'aswan': { name: 'Aswan High Dam (Egypt)', lat: 23.97, lon: 32.88, zoom: 13 },
    'cairo_nile': { name: 'Nile River (Cairo)', lat: 30.044, lon: 31.235, zoom: 14 },
    'suez': { name: 'Suez Canal (Great Bitter Lake)', lat: 30.34, lon: 32.36, zoom: 12 },
    'lake_mead': { name: 'Lake Mead Reservoir (USA)', lat: 36.14, lon: -114.43, zoom: 12 },
    'lake_como': { name: 'Lake Como (Italy)', lat: 45.98, lon: 9.26, zoom: 12 }
};

document.addEventListener('DOMContentLoaded', () => {
    initLeafletMap();
    initMapControls();
});

function initLeafletMap() {
    const mapElement = document.getElementById('leaflet-map');
    if (!mapElement) return;

    // Start centered at Lake Nasser, Egypt
    hydroMap = L.map('leaflet-map', {
        center: [selectedPoint.lat, selectedPoint.lon],
        zoom: selectedPoint.zoom,
        zoomControl: true
    });

    // High-resolution Esri World Satellite Imagery Basemap
    L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
            attribution: 'Tiles &copy; Esri, Maxar, Earthstar Geographics, USDA, USGS, AeroGRID, IGN, and GIS User Community',
            maxZoom: 18,
            minZoom: 3
        }
    ).addTo(hydroMap);

    // Save global reference for window resize
    window.hydroMap = hydroMap;

    // Place initial beacon at Lake Nasser
    placeBeacon(selectedPoint.lat, selectedPoint.lon, selectedPoint.name);

    // Map Click event: Places beacon and waits for manual inference
    hydroMap.on('click', (e) => {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;
        const zoom = hydroMap.getZoom();

        selectedPoint = { lat, lon, zoom, name: 'Target Beacon' };
        placeBeacon(lat, lon, 'Target Beacon');
    });

    // Update GPS coordinates display on move
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

    // High-visibility animated beacon marker
    const icon = L.divIcon({
        className: 'custom-beacon-marker',
        html: `
            <div class="beacon-pulse"></div>
            <div class="beacon-core" title="Click to inspect point"></div>
        `,
        iconSize: [44, 44],
        iconAnchor: [22, 22]
    });

    currentMarker = L.marker([lat, lon], { icon }).addTo(hydroMap);

    const modeLabel = currentAreaMode === 'viewport' ? 'Full Viewport' : currentAreaMode.toUpperCase();

    // Interactive popup with coordinates and prominent analyze button
    const popupContent = `
        <div style="min-width: 220px; text-align: center; font-family: system-ui, -apple-system, sans-serif; padding: 2px;">
            <div style="font-weight: 700; font-size: 13px; color: #00e5ff; margin-bottom: 3px; display: flex; align-items: center; justify-content: center; gap: 4px;">
                <i class="fa-solid fa-location-dot"></i> ${name}
            </div>
            <div style="font-size: 11px; color: #94a3b8; font-family: monospace; margin-bottom: 6px;">
                Lat: ${lat.toFixed(4)}° | Lon: ${lon.toFixed(4)}°
            </div>
            <div style="font-size: 10px; color: #38bdf8; font-family: monospace; margin-bottom: 8px;">
                Scope Mode: <b style="color: #00e5ff;">${modeLabel}</b>
            </div>
            <button id="btn-popup-infer" onclick="window.triggerPopupAnalysis()" style="width: 100%; padding: 8px 12px; background: linear-gradient(135deg, #00e5ff, #0284c7); color: #0a0e17; border: none; border-radius: 8px; font-size: 12px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 4px 14px rgba(0, 229, 255, 0.4); transition: transform 0.15s ease;">
                <i class="fa-solid fa-water"></i> Analyze Water Here
            </button>
            <div id="popup-status-text" style="margin-top: 6px; font-size: 11px; font-weight: 600; color: #38bdf8; display: none;"></div>
        </div>
    `;

    currentMarker.bindPopup(popupContent, {
        closeButton: true,
        autoPan: true,
        offset: [0, -14]
    }).openPopup();

    // Update Target Status display in toolbar
    const hint = document.getElementById('selected-target-hint');
    if (hint) {
        hint.textContent = `Selected: [${lat.toFixed(4)}°, ${lon.toFixed(4)}°] (${currentAreaMode.toUpperCase()})`;
    }
}

// Global hook for popup button click
window.triggerPopupAnalysis = function() {
    if (selectedPoint) {
        executeGeoInference(selectedPoint.lat, selectedPoint.lon, hydroMap.getZoom());
    }
};

function setAreaMode(mode) {
    currentAreaMode = mode;

    // Toggle button active classes
    document.querySelectorAll('.area-mode-btn').forEach(btn => {
        if (btn.getAttribute('data-area-mode') === mode) {
            btn.classList.add('active', 'bg-cyan-500', 'text-dark-900', 'shadow');
            btn.classList.remove('text-slate-300');
        } else {
            btn.classList.remove('active', 'bg-cyan-500', 'text-dark-900', 'shadow');
            btn.classList.add('text-slate-300');
        }
    });

    // Update primary action button text
    const actionLabel = document.getElementById('btn-segment-selected-label');
    if (actionLabel) {
        if (mode === 'viewport') {
            actionLabel.textContent = 'Analyze Full Viewport Screen';
        } else if (mode === 'large') {
            actionLabel.textContent = 'Analyze Target (Large 3x)';
        } else if (mode === 'medium') {
            actionLabel.textContent = 'Analyze Target (Medium 2x)';
        } else {
            actionLabel.textContent = 'Analyze Target (Small 1x)';
        }
    }

    // Update hint text
    const hint = document.getElementById('selected-target-hint');
    if (hint && selectedPoint) {
        hint.textContent = `Selected: [${selectedPoint.lat.toFixed(4)}°, ${selectedPoint.lon.toFixed(4)}°] (${mode.toUpperCase()})`;
    }
}

function initMapControls() {
    // Area Mode (Scope) Buttons
    document.querySelectorAll('.area-mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.getAttribute('data-area-mode');
            setAreaMode(mode);
        });
    });

    // Quick Jumps Dropdown
    const jumpSelect = document.getElementById('map-quick-jump');
    if (jumpSelect) {
        jumpSelect.addEventListener('change', (e) => {
            const locKey = e.target.value;
            if (PRESET_LOCATIONS[locKey]) {
                const loc = PRESET_LOCATIONS[locKey];
                selectedPoint = { lat: loc.lat, lon: loc.lon, zoom: loc.zoom, name: loc.name };
                hydroMap.flyTo([loc.lat, loc.lon], loc.zoom, { duration: 1.4 });
                setTimeout(() => {
                    placeBeacon(loc.lat, loc.lon, loc.name);
                }, 1500);
            }
        });
    }

    // Primary Action Button: Segment Selected Target Beacon or Full Viewport
    const segmentSelectedBtn = document.getElementById('btn-segment-selected');
    if (segmentSelectedBtn) {
        segmentSelectedBtn.addEventListener('click', () => {
            const zoom = hydroMap.getZoom();
            if (currentAreaMode === 'viewport') {
                const center = hydroMap.getCenter();
                executeGeoInference(center.lat, center.lng, zoom);
            } else {
                executeGeoInference(selectedPoint.lat, selectedPoint.lon, zoom);
            }
        });
    }

    // Secondary Action Button: Segment Current Map Center View
    const segmentCenterBtn = document.getElementById('btn-segment-center');
    if (segmentCenterBtn) {
        segmentCenterBtn.addEventListener('click', () => {
            const center = hydroMap.getCenter();
            const zoom = hydroMap.getZoom();
            selectedPoint = { lat: center.lat, lon: center.lng, zoom: zoom, name: 'Map Center' };
            placeBeacon(center.lat, center.lng, 'Map Center');
            executeGeoInference(center.lat, center.lng, zoom);
        });
    }

    // Geocoding Search: Button click & Enter key
    const searchBtn = document.getElementById('btn-search-location');
    const searchInput = document.getElementById('map-search-input');

    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => {
            handleSearchLocation(searchInput.value);
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleSearchLocation(searchInput.value);
            }
        });
    }

    // Mask Opacity Slider
    const opacitySlider = document.getElementById('map-overlay-opacity');
    if (opacitySlider) {
        opacitySlider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            if (currentGeoOverlay) {
                currentGeoOverlay.setOpacity(val);
            }
        });
    }
}

async function handleSearchLocation(query) {
    if (!query || !query.trim()) return;
    const cleanQuery = query.trim();

    // Check if query is GPS coordinates (e.g., "26.5, 56.5" or "26.5 56.5")
    const coordPattern = /^([-+]?\d*\.?\d+)[,\s]+([-+]?\d*\.?\d+)$/;
    const match = cleanQuery.match(coordPattern);
    if (match) {
        const lat = parseFloat(match[1]);
        const lon = parseFloat(match[2]);
        if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
            selectedPoint = { lat, lon, zoom: 12, name: `GPS [${lat.toFixed(3)}, ${lon.toFixed(3)}]` };
            hydroMap.flyTo([lat, lon], 12, { duration: 1.2 });
            setTimeout(() => {
                placeBeacon(lat, lon, selectedPoint.name);
            }, 1300);
            return;
        }
    }

    // Otherwise, query OpenStreetMap Nominatim Geocoding API
    const searchBtn = document.getElementById('btn-search-location');
    if (searchBtn) searchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

    try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(cleanQuery)}`;
        const resp = await fetch(url, { headers: { 'Accept': 'application/json' } });
        if (!resp.ok) throw new Error('Geocoding search failed');
        const results = await resp.json();

        if (results && results.length > 0) {
            const topResult = results[0];
            const lat = parseFloat(topResult.lat);
            const lon = parseFloat(topResult.lon);
            const shortName = topResult.name || cleanQuery;

            selectedPoint = { lat, lon, zoom: 12, name: shortName };
            hydroMap.flyTo([lat, lon], 12, { duration: 1.5 });
            setTimeout(() => {
                placeBeacon(lat, lon, shortName);
            }, 1600);
        } else {
            alert(`Location "${cleanQuery}" not found. You can enter direct GPS coordinates like: 26.5, 56.5`);
        }
    } catch (err) {
        console.error('Geocoding error:', err);
    } finally {
        if (searchBtn) searchBtn.innerHTML = 'Search';
    }
}

async function executeGeoInference(lat, lon, zoom) {
    const loadingBadge = document.getElementById('map-loading-indicator');
    const metricsPanel = document.getElementById('map-metrics-panel');
    const actionLabel = document.getElementById('btn-segment-selected-label');
    const popupStatus = document.getElementById('popup-status-text');

    if (loadingBadge) loadingBadge.classList.remove('hidden');
    if (actionLabel) actionLabel.textContent = 'Analyzing...';
    if (popupStatus) {
        popupStatus.style.display = 'block';
        popupStatus.innerHTML = '<i class="fa-solid fa-satellite fa-spin"></i> Querying satellite tile...';
    }

    try {
        const threshold = parseFloat(document.getElementById('threshold-slider')?.value || 0.5);

        // Get visible map viewport bounds
        const boundsObj = hydroMap.getBounds();
        const viewport_bounds = [
            [boundsObj.getSouth(), boundsObj.getWest()],
            [boundsObj.getNorth(), boundsObj.getEast()]
        ];

        const resp = await fetch('/predict_geo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat,
                lon,
                zoom,
                threshold,
                area_mode: currentAreaMode,
                viewport_bounds: viewport_bounds
            })
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || `HTTP ${resp.status}`);
        }

        const data = await resp.json();

        // 1. Remove previous overlay and bounding box
        if (currentGeoOverlay) {
            hydroMap.removeLayer(currentGeoOverlay);
        }
        if (currentBbox) {
            hydroMap.removeLayer(currentBbox);
        }

        // 2. Add Tile/Scope Footprint Bounding Box (Visual Boundary)
        const bboxColor = data.water_percentage > 0.05 ? '#00e5ff' : '#f59e0b';
        currentBbox = L.rectangle(data.bounds, {
            color: bboxColor,
            weight: 2,
            dashArray: '5, 5',
            fillColor: bboxColor,
            fillOpacity: 0.05,
            interactive: true
        }).addTo(hydroMap);

        const scopeTitle = data.area_mode === 'viewport' ? 'Full Viewport Screen' : `${data.area_mode.toUpperCase()} Footprint`;
        currentBbox.bindTooltip(
            `<strong>${scopeTitle}</strong><br>Detected Water: <b>${data.water_percentage.toFixed(1)}%</b> (${data.water_pixels.toLocaleString()} px)`,
            { sticky: true }
        );

        // 3. Render Transparent PNG Water Overlay onto Leaflet Map
        const opacity = parseFloat(document.getElementById('map-overlay-opacity')?.value || 0.85);
        currentGeoOverlay = L.imageOverlay(data.overlay_base64, data.bounds, {
            opacity: opacity,
            interactive: false
        }).addTo(hydroMap);

        // 4. Update Geo Metrics Telemetry Panel
        if (metricsPanel) {
            metricsPanel.classList.remove('hidden');
            document.getElementById('geo-water-pct').textContent = `${data.water_percentage.toFixed(1)}%`;
            document.getElementById('geo-water-px').textContent = `${data.water_pixels.toLocaleString()} px`;
            document.getElementById('geo-latency').textContent = `${data.latency_ms.toFixed(0)} ms`;
            document.getElementById('geo-bounds').textContent = `[${data.bounds[0][0].toFixed(3)}, ${data.bounds[0][1].toFixed(3)}] to [${data.bounds[1][0].toFixed(3)}, ${data.bounds[1][1].toFixed(3)}]`;
        }

        // 5. Update Popup Status
        if (popupStatus) {
            if (data.water_percentage > 0.05) {
                popupStatus.innerHTML = `<span style="color:#00e5ff;">🌊 Water: <b>${data.water_percentage.toFixed(1)}%</b> (${data.water_pixels.toLocaleString()} px)</span>`;
            } else {
                popupStatus.innerHTML = `<span style="color:#fbbf24;">🏜️ 0.0% Water (Arid / Land Area)</span>`;
            }
        }

    } catch (err) {
        console.error('Geo inference error:', err);
        if (popupStatus) {
            popupStatus.innerHTML = `<span style="color:#ef4444;">❌ Analysis failed: ${err.message}</span>`;
        }
    } finally {
        if (loadingBadge) loadingBadge.classList.add('hidden');
        const defaultLabel = currentAreaMode === 'viewport' ? 'Analyze Full Viewport Screen' : `Analyze Target (${currentAreaMode.toUpperCase()})`;
        if (actionLabel) actionLabel.textContent = defaultLabel;
    }
}
