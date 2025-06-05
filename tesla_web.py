import os
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-me')

CLIENT_ID = os.environ.get('TESLA_CLIENT_ID', 'ownerapi')
CLIENT_SECRET = os.environ.get('TESLA_CLIENT_SECRET')
REDIRECT_URI = os.environ.get(
    'TESLA_REDIRECT_URI',
    'http://localhost:5000/callback'
)
SCOPE = os.environ.get('TESLA_SCOPE', 'openid email offline_access')

authorize_url = 'https://auth.tesla.com/oauth2/v3/authorize'
token_url = 'https://auth.tesla.com/oauth2/v3/token'


def get_vehicle_location():
    token = session.get('access_token')
    if not token:
        return None, 'not authenticated'

    headers = {'Authorization': f'Bearer {token}'}
    vehicles_url = 'https://owner-api.teslamotors.com/api/1/vehicles'
    resp = requests.get(vehicles_url, headers=headers)
    if resp.status_code != 200:
        return None, 'failed to fetch vehicles'
    vehicles = resp.json().get('response', [])
    if not vehicles:
        return None, 'no vehicles'
    vid = vehicles[0]['id']
    data_url = (
        f'https://owner-api.teslamotors.com/api/1/vehicles/{vid}/vehicle_data'
    )
    resp = requests.get(data_url, headers=headers)
    if resp.status_code != 200:
        return None, 'failed to fetch vehicle data'
    data = resp.json().get('response', {}).get('drive_state', {})
    lat = data.get('latitude')
    lon = data.get('longitude')
    if lat is None or lon is None:
        return None, 'location unavailable'
    return {'lat': lat, 'lon': lon}, None


@app.route('/')
def index():
    if 'access_token' in session:
        return (
            '<a href="/location">Show Location</a> | '
            '<a href="/logout">Logout</a>'
        )
    return '<a href="/login">Login with Tesla</a>'


@app.route('/login')
def login():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPE,
    }
    return redirect(f"{authorize_url}?{urlencode(params)}")


@app.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        return f"Error: {error}", 400

    code = request.args.get('code')
    if not code:
        return 'Missing code', 400

    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    if CLIENT_SECRET:
        data['client_secret'] = CLIENT_SECRET

    resp = requests.post(token_url, json=data)
    if resp.status_code != 200:
        return f"Token exchange failed: {resp.text}", 400

    token_data = resp.json()
    session['access_token'] = token_data.get('access_token')
    session['refresh_token'] = token_data.get('refresh_token')
    session['expires_in'] = token_data.get('expires_in')
    return redirect(url_for('index'))


@app.route('/location')
def location():
    loc, error = get_vehicle_location()
    if error:
        return error, 400

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel='stylesheet'
              href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>
        <style>#map {{ height: 400px; }}</style>
    </head>
    <body>
        <div id='map'></div>
        <script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>
        <script>
            var map = L.map('map').setView([{loc['lat']}, {loc['lon']}], 15);
            L.tileLayer(
                'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
                {{maxZoom: 19}}
            ).addTo(map);
            L.marker([{loc['lat']}, {loc['lon']}]).addTo(map);
        </script>
    </body>
    </html>
    """
    return html


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
