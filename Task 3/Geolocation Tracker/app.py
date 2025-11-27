from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Configuration for Geolocation API
API_CONFIG = {
    'ipapi': {
        'enabled': True,  # Free, no API key needed
        'url': 'http://ip-api.com/json/',
        'rate_limit': '45 requests/minute'
    }
}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/about')
def about():
    """Render the About page"""
    return render_template('about.html')

# Auto IP Location Fetching
@app.route('/ip-location')
def ip_location():
    try:
        # Use ip-api.com for a simple, no-key lookup of the client's public IP
        resp = requests.get('http://ip-api.com/json/', params={'fields': 'status,message,query,city,regionName,country,lat,lon,isp,timezone'}, timeout=5)
        resp.raise_for_status()
        res = resp.json()

        if res.get('status') == 'fail':
            return jsonify({'error': res.get('message', 'Unable to fetch IP location')}), 500

        data = {
            'ip': res.get('query'),
            'city': res.get('city'),
            'region': res.get('regionName'),
            'country': res.get('country'),
            'latitude': res.get('lat'),
            'longitude': res.get('lon'),
            'isp': res.get('isp'),
            'timezone': res.get('timezone')
        }
        return jsonify(data)

    except Exception:
        return jsonify({"error": "Unable to fetch IP-based location"}), 500

@app.route('/api/locate', methods=['POST'])
def locate_ip():
    """
    API endpoint to fetch geolocation data for an IP address
    Expects JSON: {"ip": "223.123.105.30", "provider": "ipapi"}
    Returns geolocation data or error
    """
    try:
        data = request.get_json()
        ip = data.get('ip', '').strip()
        
        # Auto-detect actual user public IP when empty or localhost
        if not ip or ip in ("127.0.0.1", "localhost", "::1"):
            ip = ""
        
        # Using ip-api.com (free, no API key required)
        # Rate limit: 45 requests per minute
        url = f'http://ip-api.com/json/{ip}'
        params = {
            'fields': 'status,message,country,regionName,city,lat,lon,isp,timezone,query'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        geo_data = response.json()
        
        if geo_data.get('status') == 'fail':
            return jsonify({'error': geo_data.get('message', 'Invalid IP address')}), 400
        
        return jsonify({
            'ip': geo_data.get('query'),
            'country': geo_data.get('country'),
            'region': geo_data.get('regionName'),
            'city': geo_data.get('city'),
            'lat': geo_data.get('lat'),
            'lon': geo_data.get('lon'),
            'isp': geo_data.get('isp'),
            'timezone': geo_data.get('timezone'),
            'provider': 'ip-api.com'
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch from ip-api: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("IP Geolocation Tracker - API Configuration")
    print("="*60)
    for provider, config in API_CONFIG.items():
        status = "✓ ENABLED" if config['enabled'] else "✗ DISABLED"
        print(f"\n{provider.upper()}: {status}")
        print(f"  URL: {config['url']}")
        print(f"  Rate Limit: {config['rate_limit']}")
        if 'api_key' in config:
            has_key = config['api_key'] and config['api_key'] != f'YOUR_{provider.upper()}_API_KEY_HERE'
            print(f"  API Key: {'✓ Configured' if has_key else '✗ Not configured'}")
    print("\n" + "="*60)
    print("Server starting on http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
