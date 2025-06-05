import json
import os
from urllib import request, error
from flask import Flask, Response

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
    drive_state = data.get('drive_state', {})
    state = data.get('state', 'unbekannt')
    temp_in = climate.get('inside_temp', 'N/A')
    temp_out = climate.get('outside_temp', 'N/A')
    battery = charge_state.get('battery_level', 'N/A')
    lat = drive_state.get('latitude')
    lon = drive_state.get('longitude')

    html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Tesla Model S Anzeige</title>
        <link
            rel="stylesheet"
            href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
            integrity="sha256-sA+e2LYCNyZWFuoL1snzAkCNMAdg72yzp7b2uJZi+X0="
            crossorigin=""
        />
        <script
            src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha256-GZ0jM8CX/tD+07r9qza1cS2H91TGaE/fhXxzT6iZl/k="
            crossorigin=""
        ></script>
    </head>
    <body>
        <h1>Tesla Model S Anzeige</h1>
        <p><strong>Fahrzeugstatus:</strong> {state}</p>
        <p><strong>Innen-Temperatur:</strong> {temp_in} °C</p>
        <p><strong>Außen-Temperatur:</strong> {temp_out} °C</p>
        <p><strong>Batteriestand:</strong> {battery}%</p>
        <div id="map" style="height: 300px;"></div>
        <script>
            var map = L.map('map').setView([
                {lat if lat is not None else 0},
                {lon if lon is not None else 0}
            ], 13);
            L.tileLayer(
                'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
                {{'maxZoom': 19, 'attribution': '&copy; OpenStreetMap contributors'}}
            ).addTo(map);
            L.marker([
                {lat if lat is not None else 0},
                {lon if lon is not None else 0}
            ]).addTo(map);
        </script>
        <a href='/'>Aktualisieren</a>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8066)
