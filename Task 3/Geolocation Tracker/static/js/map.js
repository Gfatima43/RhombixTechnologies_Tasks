// ========================================
// Global Variables
// ========================================
let map;
let marker;

// Live tracking markers
let liveMarker;
let liveCircle;
let polyline;

// Live tracking state
let isLiveTracking = false;
let watchPositionId = null;
// Reverse geocode throttle
let lastReverseGeocodeTime = 0;
const REVERSE_GEOCODE_INTERVAL = 5000; // ms

// Custom Animated Dot Icon for Live Tracking
let liveIcon = L.divIcon({
    className: "",
    html: '<div class="live-dot"></div>',
    iconSize: [20, 20]
});

// Custom marker icon for IP location
let markerIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// ========================================
// Initialize Map
// ========================================
function initMap() {
    // Create map centered on world view
    map = L.map('map', {
        zoomControl: true,
        scrollWheelZoom: true
    }).setView([20, 0], 2);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        minZoom: 2
    }).addTo(map);

    // Add zoom control to top right
    map.zoomControl.setPosition('topright');
}

// ========================================
// Start Live GPS Tracking
// ========================================
function startLiveTracking() {
    if (!navigator.geolocation) {
        showError('GPS is not supported by your browser');
        return;
    }

    // Stop any existing tracking
    stopLiveTracking();
    isLiveTracking = true;

    // Update button states
    const liveBtn = document.querySelector('.live-btn');
    const stopBtn = document.querySelector('.stop-btn');
    liveBtn.disabled = true;
    stopBtn.disabled = false;

    // Show live tracking alert
    const liveStatusAlert = document.getElementById('liveStatusAlert');
    liveStatusAlert.classList.remove('d-none');
    liveStatusAlert.classList.add('show');

    // Hide error if showing
    document.getElementById('errorAlert').classList.add('d-none');

    // Show info card
    const infoCard = document.getElementById('infoCard');
    infoCard.classList.remove('d-none');

    // Fetch IP-based location and show it on the map (so map shows IP data like "Karachi ...")
    fetchLocationForLiveTracking();

    // Show a temporary status while IP lookup runs
    document.getElementById('ip').textContent = 'Detecting...';
    document.getElementById('country').textContent = 'Tracking...';
    document.getElementById('region').textContent = 'Tracking...';
    document.getElementById('city').textContent = 'Tracking...';
    document.getElementById('isp').textContent = 'N/A';
    document.getElementById('timezone').textContent = 'N/A';

    watchPositionId = navigator.geolocation.watchPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const acc = pos.coords.accuracy;

            // Update or create live marker
            if (!liveMarker) {
                liveMarker = L.marker([lat, lon], {
                    icon: liveIcon,
                    draggable: false
                }).addTo(map);

                liveMarker.bindPopup(`
                    <div style="font-family: 'Segoe UI', sans-serif; padding: 5px;">
                        <h6 style="margin: 0 0 10px 0; color: #0C2B4E; font-weight: bold;">
                            <i class="bi bi-broadcast-pin"></i> Live GPS Location
                        </h6>
                        <p style="margin: 5px 0; font-size: 14px;">
                            <strong>Coordinates:</strong> ${lat.toFixed(6)}, ${lon.toFixed(6)}
                        </p>
                        <p style="margin: 5px 0; font-size: 14px;">
                            <strong>Accuracy:</strong> ±${acc.toFixed(0)}m
                        </p>
                    </div>
                `).openPopup();
            } else {
                liveMarker.setLatLng([lat, lon]);
                liveMarker.getPopup().setContent(`
                    <div style="font-family: 'Segoe UI', sans-serif; padding: 5px;">
                        <h6 style="margin: 0 0 10px 0; color: #0C2B4E; font-weight: bold;">
                            <i class="bi bi-broadcast-pin"></i> Live GPS Location
                        </h6>
                        <p style="margin: 5px 0; font-size: 14px;">
                            <strong>Coordinates:</strong> ${lat.toFixed(6)}, ${lon.toFixed(6)}
                        </p>
                        <p style="margin: 5px 0; font-size: 14px;">
                            <strong>Accuracy:</strong> ±${acc.toFixed(0)}m
                        </p>
                    </div>
                `);
            }

            // Update or create accuracy circle
            if (!liveCircle) {
                liveCircle = L.circle([lat, lon], {
                    radius: acc,
                    color: '#28a745',
                    fillColor: '#28a745',
                    fillOpacity: 0.1,
                    weight: 2
                }).addTo(map);
            } else {
                liveCircle.setLatLng([lat, lon]);
                liveCircle.setRadius(acc);
            }

            // Update or create tracking path
            if (!polyline) {
                polyline = L.polyline([[lat, lon]], {
                    color: '#0C2B4E',
                    weight: 3,
                    opacity: 0.7
                }).addTo(map);
            } else {
                polyline.addLatLng([lat, lon]);
            }

            // Smoothly move map to location
            map.setView([lat, lon], map.getZoom() < 13 ? 13 : map.getZoom(), {
                animate: true,
                duration: 1
            });

            // Update info box with live tracking data
            updateLiveTrackingInfo(lat, lon, acc);

            // Also update coords in the IP info card so map/info shows live coords
            updateIPInfoForGPS(lat, lon);

            // Scroll to map on mobile
            if (window.innerWidth < 768) {
                document.getElementById('map').scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        },
        (err) => {
            console.error("GPS Error:", err);
            showError(`GPS Error: ${err.message}. Please enable location services.`);
            stopLiveTracking();
        },
        {
            enableHighAccuracy: true,
            maximumAge: 0,
            timeout: 10000
        }
    );
}

// ========================================
// Stop Live GPS Tracking
// ========================================
function stopLiveTracking() {
    if (watchPositionId !== null) {
        navigator.geolocation.clearWatch(watchPositionId);
        watchPositionId = null;
    }

    isLiveTracking = false;

    // Remove tracking markers
    if (liveMarker) {
        map.removeLayer(liveMarker);
        liveMarker = null;
    }
    if (liveCircle) {
        map.removeLayer(liveCircle);
        liveCircle = null;
    }
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null;
    }

    // Update button states
    const liveBtn = document.querySelector('.live-btn');
    const stopBtn = document.querySelector('.stop-btn');
    liveBtn.disabled = false;
    stopBtn.disabled = true;

    // Hide live tracking alert
    const liveStatusAlert = document.getElementById('liveStatusAlert');
    liveStatusAlert.classList.remove('show');
    liveStatusAlert.classList.add('d-none');

    // Hide accuracy badge
    document.getElementById('accuracyBadge').classList.add('d-none');
}

// ========================================
// Update Live Tracking Info
// ========================================
function updateLiveTrackingInfo(lat, lon, accuracy) {
    document.getElementById('coords').textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)}`;

    // Show and update accuracy badge
    const accuracyBadge = document.getElementById('accuracyBadge');
    const accuracyValue = document.getElementById('accuracyValue');
    accuracyValue.textContent = Math.round(accuracy);
    accuracyBadge.classList.remove('d-none');

    const infoCard = document.getElementById('infoCard');
    if (!infoCard.classList.contains('show')) {
        infoCard.classList.remove('d-none');
    }
}

// ========================================
// ========================================
// Fetch IP Location Data for Live Tracking
// ========================================
async function fetchLocationForLiveTracking() {
    try {
        const response = await fetch('/api/locate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ip: '',  // empty to auto-detect user's IP
                provider: 'ipapi'
            })
        });

        const data = await response.json();

        if (data && !data.error) {
            // Update info card and place IP marker on the map
            updateInfoBox(data);
            updateMap(data);
            // Ensure info card visible
            document.getElementById('infoCard').classList.remove('d-none');
        }
    } catch (err) {
        console.error('Error fetching IP location for live tracking:', err);
    }
}

// ========================================
// Update IP Info Based on GPS Coordinates
// ========================================
function updateIPInfoForGPS(lat, lon) {
    // Update just the coordinates display so the info card shows live coords
    const coordsEl = document.getElementById('coords');
    if (coordsEl) {
        coordsEl.textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
    }
}

// Reverse geocode lat/lon to get city/region/country (uses Nominatim)
async function reverseGeocode(lat, lon) {
    try {
        const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&accept-language=en`;
        const resp = await fetch(url, {
            headers: {
                'Referer': window.location.origin
            }
        });
        if (!resp.ok) return null;
        const json = await resp.json();
        const addr = json.address || {};
        // Try several fields for city/region
        const city = addr.city || addr.town || addr.village || addr.hamlet || addr.county || '';
        const region = addr.state || addr.region || '';
        const country = addr.country || '';
        return { city, region, country };
    } catch (e) {
        console.error('Reverse geocode failed', e);
        return null;
    }
}

// Update info card with live GPS coordinates and (throttled) reverse-geocoded place info
async function updateIPInfoForGPS(lat, lon) {
    // Update coords immediately
    const coordsEl = document.getElementById('coords');
    if (coordsEl) coordsEl.textContent = `${lat.toFixed(6)}, ${lon.toFixed(6)}`;

    // Update accuracy badge if present (some callers set it already)
    const accuracyBadge = document.getElementById('accuracyBadge');
    if (accuracyBadge && accuracyBadge.classList.contains('d-none')) {
        accuracyBadge.classList.remove('d-none');
    }

    // Throttle reverse geocoding to avoid too many requests
    const now = Date.now();
    if (now - lastReverseGeocodeTime < REVERSE_GEOCODE_INTERVAL) return;
    lastReverseGeocodeTime = now;

    const place = await reverseGeocode(lat, lon);
    if (!place) return;

    // Only update fields when we have values
    if (place.city) document.getElementById('city').textContent = place.city;
    if (place.region) document.getElementById('region').textContent = place.region;
    if (place.country) document.getElementById('country').textContent = place.country;
}

// ========================================
// Fetch Location Data from IP API
// ========================================
async function fetchLocation() {
    const ip = document.getElementById('ipInput').value.trim();
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const loadingState = document.getElementById('loadingState');
    const infoCard = document.getElementById('infoCard');

    // Stop live tracking if active
    if (isLiveTracking) {
        stopLiveTracking();
    }

    // Reset UI
    errorAlert.classList.remove('show');
    errorAlert.classList.add('d-none');
    infoCard.classList.add('d-none');
    loadingState.classList.remove('d-none');

    try {
        const response = await fetch('/api/locate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ip: ip,
                provider: 'ipapi'
            })
        });

        const data = await response.json();
        loadingState.classList.add('d-none');

        if (data.error) {
            showError(data.error);
            return;
        }

        // Update info card with location data
        updateInfoBox(data);

        // Update map with marker
        updateMap(data);

        // Show info card with animation
        infoCard.classList.remove('d-none');

        // Scroll to results on mobile
        if (window.innerWidth < 768) {
            document.getElementById('map').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }

    } catch (error) {
        loadingState.classList.add('d-none');
        showError('Failed to fetch location data. Please check your internet connection and try again.');
        console.error('Error:', error);
    }
}

// ========================================
// Update Information Card
// ========================================
function updateInfoBox(data) {
    document.getElementById('ip').textContent = data.ip || 'Unknown';
    document.getElementById('country').textContent = data.country || 'Unknown';
    document.getElementById('region').textContent = data.region || 'Unknown';
    document.getElementById('city').textContent = data.city || 'Unknown';
    document.getElementById('coords').textContent = data.lat && data.lon
        ? `${data.lat.toFixed(6)}, ${data.lon.toFixed(6)}`
        : 'Unknown';
    document.getElementById('isp').textContent = data.isp || 'Unknown';
    document.getElementById('timezone').textContent = data.timezone || 'Unknown';

    // Hide accuracy badge for IP location
    document.getElementById('accuracyBadge').classList.add('d-none');
}

// ========================================
// Update Map with Marker
// ========================================
function updateMap(data) {
    // Remove existing marker if present
    if (marker) {
        map.removeLayer(marker);
    }

    // Validate coordinates
    if (!data.lat || !data.lon) {
        showError('Invalid coordinates received');
        return;
    }

    // Add new marker with custom icon
    marker = L.marker([data.lat, data.lon], { icon: markerIcon }).addTo(map);

    // Create popup with detailed location info
    const popupContent = `
        <div style="font-family: 'Segoe UI', sans-serif; padding: 5px;">
            <h6 style="margin: 0 0 10px 0; color: #0C2B4E; font-weight: bold;">
                <i class="bi bi-geo-alt-fill"></i> ${data.city || 'Unknown City'}
            </h6>
            <p style="margin: 5px 0; font-size: 14px;">
                <strong>Region:</strong> ${data.region || 'N/A'}
            </p>
            <p style="margin: 5px 0; font-size: 14px;">
                <strong>Country:</strong> ${data.country || 'N/A'}
            </p>
            <p style="margin: 5px 0; font-size: 14px;">
                <strong>IP:</strong> ${data.ip || 'N/A'}
            </p>
            <p style="margin: 5px 0; font-size: 12px; color: #6C757D;">
                ${data.lat.toFixed(6)}, ${data.lon.toFixed(6)}
            </p>
        </div>
    `;

    marker.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'custom-popup'
    }).openPopup();

    // Animate map to location with smooth transition
    map.flyTo([data.lat, data.lon], 10, {
        duration: 1.5,
        easeLinearity: 0.5
    });
}

// ========================================
// Show Error Message
// ========================================
function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.textContent = message;
    errorAlert.classList.remove('d-none');
    errorAlert.classList.add('show');

    // Scroll to error message on mobile
    if (window.innerWidth < 768) {
        errorAlert.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

// ========================================
// DOM Content Loaded Event
// ========================================
document.addEventListener('DOMContentLoaded', function () {
    // Initialize map on page load
    initMap();

    // Fetch user's own location on page load
    setTimeout(() => {
        fetchLocation();
    }, 500);

    // Handle form submission
    const form = document.getElementById('ipSearchForm');
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        fetchLocation();
    });

    // Allow Enter key to trigger search
    document.getElementById('ipInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            fetchLocation();
        }
    });

    // Add button event listeners
    document.querySelector('.live-btn').addEventListener('click', startLiveTracking);
    document.querySelector('.stop-btn').addEventListener('click', stopLiveTracking);

    // Disable stop button initially
    document.querySelector('.stop-btn').disabled = true;

    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Close alert on dismiss
    const alertCloseButtons = document.querySelectorAll('.btn-close');
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function () {
            const alert = this.closest('.alert');
            alert.classList.remove('show');
            alert.classList.add('d-none');
        });
    });
});

// ========================================
// Responsive Map Resize
// ========================================
window.addEventListener('resize', function () {
    if (map) {
        map.invalidateSize();
    }
});