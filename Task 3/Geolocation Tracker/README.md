# IP Geolocation Tracker

A Flask web application that fetches geolocation data based on IP addresses and displays the location on an interactive map.

## Project Structure

```
geolocation-tracker/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── templates/
│   └── index.html             # Main HTML template
│
└── static/
    ├── css/
    │   └── style.css          # Stylesheet
    └── js/
        └── map.js             # JavaScript for map functionality
```

## Features

- 🌍 **IP Geolocation Lookup** - Enter any IP address or detect your own automatically
- 🗺️ **Interactive Map** - View locations on an OpenStreetMap powered by Leaflet.js
- 📊 **Detailed Information** - Display country, region, city, ISP, timezone, and coordinates
- 🎨 **Modern UI** - Beautiful gradient design with smooth animations
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Installation

1. **Clone or download the project**

2. **Create the project structure:**
   ```bash
   mkdir -p geolocation-tracker/templates
   mkdir -p geolocation-tracker/static/css
   mkdir -p geolocation-tracker/static/js
   ```

3. **Place the files in their respective directories:**
   - `app.py` in the root directory
   - `index.html` in the `templates/` folder
   - `style.css` in the `static/css/` folder
   - `map.js` in the `static/js/` folder

4. **Install dependencies:**
   ```bash
   cd geolocation-tracker
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Flask application:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Use the application:**
   - Leave the input field empty and click "Locate IP" to see your own location
   - Enter any public IP address to track its location
   - Press Enter or click the button to search

## API Endpoint

The application exposes a REST API endpoint:

**POST** `/api/locate`

**Request Body:**
```json
{
  "ip": "8.8.8.8"
}
```

**Response:**
```json
{
  "ip": "8.8.8.8",
  "country": "United States",
  "region": "California",
  "city": "Mountain View",
  "lat": 37.4056,
  "lon": -122.0775,
  "isp": "Google LLC",
  "timezone": "America/Los_Angeles"
}
```

## Technical Details

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Map Library:** Leaflet.js
- **Geolocation API:** ip-api.com (free tier, 45 requests/minute)
- **Map Tiles:** OpenStreetMap

## Notes

- The application uses the free ip-api.com service which has a rate limit of 45 requests per minute
- Localhost IPs (127.0.0.1) are automatically detected and the public IP is fetched instead
- The application runs in debug mode by default - disable for production use

## License

Free to use and modify for personal and commercial projects.