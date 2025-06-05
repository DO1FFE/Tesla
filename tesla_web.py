import json
import os
import secrets
from urllib import request, error
from flask import Flask, Response, redirect, request as flask_request, session, url_for

API_BASE = "https://owner-api.teslamotors.com/api/1"

class TeslaClient:
    def __init__(self, token):
        self.token = token

    def _get(self, endpoint):
        url = f"{API_BASE}{endpoint}"
        req = request.Request(url)
        req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with request.urlopen(req) as resp:
                return json.load(resp)
        except error.URLError as e:
            raise RuntimeError(f"API request failed: {e}")

    def list_vehicles(self):
        data = self._get("/vehicles")
        return data.get("response", [])

    def vehicle_data(self, vehicle_id):
        data = self._get(f"/vehicles/{vehicle_id}/vehicle_data")
        return data.get("response", {})

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'change-me')


@app.route('/login')
def login():
    """Start OAuth flow and store state in session."""
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    redirect_uri = url_for('callback', _external=True)
    auth_url = (
        "https://auth.tesla.com/oauth2/v3/authorize?"
        "client_id=ownerapi&response_type=code"
        f"&redirect_uri={redirect_uri}&state={state}"
    )
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Handle OAuth callback and validate state."""
    stored_state = session.get('oauth_state')
    returned_state = flask_request.args.get('state')
    if not stored_state or stored_state != returned_state:
        return Response('Invalid state parameter', status=400)

    session.pop('oauth_state', None)
    code = flask_request.args.get('code')
    return f'Received code: {code}'

@app.route('/')
def index():
    token = os.getenv('TESLA_TOKEN')
    if not token:
        return Response('Umgebungsvariable TESLA_TOKEN nicht gesetzt', status=500)

    client = TeslaClient(token)
    try:
        vehicles = client.list_vehicles()
    except Exception as e:
        return Response(f'Fehler beim Laden der Fahrzeuge: {e}', status=500)

    if not vehicles:
        return 'Keine Fahrzeuge gefunden'

    vehicle_id = vehicles[0]['id']
    try:
        data = client.vehicle_data(vehicle_id)
    except Exception as e:
        return Response(f'Fehler beim Abrufen der Fahrzeugdaten: {e}', status=500)

    climate = data.get('climate_state', {})
    charge_state = data.get('charge_state', {})
    state = data.get('state', 'unbekannt')
    temp_in = climate.get('inside_temp', 'N/A')
    temp_out = climate.get('outside_temp', 'N/A')
    battery = charge_state.get('battery_level', 'N/A')

    html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Tesla Model S Anzeige</title>
    </head>
    <body>
        <h1>Tesla Model S Anzeige</h1>
        <p><strong>Fahrzeugstatus:</strong> {state}</p>
        <p><strong>Innen-Temperatur:</strong> {temp_in} °C</p>
        <p><strong>Außen-Temperatur:</strong> {temp_out} °C</p>
        <p><strong>Batteriestand:</strong> {battery}%</p>
        <a href='/'>Aktualisieren</a>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8066)
