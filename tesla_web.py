import json
import os
import base64
import hashlib
import secrets
from urllib import request as urlrequest, error, parse
from flask import Flask, Response, jsonify, redirect, request, session, url_for

API_BASE = "https://owner-api.teslamotors.com/api/1"
AUTH_URL = "https://auth.tesla.com/oauth2/v3/authorize"
TOKEN_URL = "https://auth.tesla.com/oauth2/v3/token"
CLIENT_ID = os.getenv("TESLA_CLIENT_ID", "ownerapi")
REDIRECT_URI = os.getenv("TESLA_REDIRECT_URI", "http://localhost:8066/oauth/callback")

class TeslaClient:
    def __init__(self, token):
        self.token = token

    def _get(self, endpoint):
        url = f"{API_BASE}{endpoint}"
        req = urlrequest.Request(url)
        req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urlrequest.urlopen(req) as resp:
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
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(16))


def fetch_vehicle_values():
    token = session.get("tesla_token") or os.getenv("TESLA_TOKEN")
    if not token:
        raise RuntimeError("Kein Tesla-Token vorhanden")

    client = TeslaClient(token)
    vehicles = client.list_vehicles()
    if not vehicles:
        raise RuntimeError("Keine Fahrzeuge gefunden")

    vehicle_id = vehicles[0]["id"]
    data = client.vehicle_data(vehicle_id)

    climate = data.get("climate_state", {})
    charge_state = data.get("charge_state", {})
    drive_state = data.get("drive_state", {})
    vehicle_state = data.get("vehicle_state", {})

    return {
        "state": data.get("state", "unbekannt"),
        "inside_temp": climate.get("inside_temp", "N/A"),
        "outside_temp": climate.get("outside_temp", "N/A"),
        "battery_level": charge_state.get("battery_level", "N/A"),
        "odometer": vehicle_state.get("odometer", "N/A"),
        "tpms_pressure_fl": vehicle_state.get("tpms_pressure_fl", "N/A"),
        "tpms_pressure_fr": vehicle_state.get("tpms_pressure_fr", "N/A"),
        "tpms_pressure_rl": vehicle_state.get("tpms_pressure_rl", "N/A"),
        "tpms_pressure_rr": vehicle_state.get("tpms_pressure_rr", "N/A"),
        "latitude": drive_state.get("latitude"),
        "longitude": drive_state.get("longitude"),
    }

@app.route('/')
def index():
    try:
        values = fetch_vehicle_values()
    except Exception:
        return redirect(url_for('login'))

    lat = values.get("latitude")
    lon = values.get("longitude")
    map_html = ""
    if lat is not None and lon is not None:
        map_url = f"https://maps.google.com/maps?q={lat},{lon}&z=15&output=embed"
        map_html = f"<iframe id='map' src='{map_url}'></iframe>"

    html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Tesla Model S Anzeige</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f8f8;
                color: #333;
                padding: 20px;
            }}
            .container {{
                background: #fff;
                border-radius: 8px;
                padding: 20px;
                max-width: 500px;
                margin: auto;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                text-align: center;
            }}
            iframe {{
                width: 100%;
                height: 300px;
                border: none;
                margin-top: 10px;
            }}
            .tpms {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 5px;
            }}
        </style>
    </head>
    <body>
        <div class='container'>
            <h1>Tesla Model S Anzeige</h1>
            <p><strong>Fahrzeugstatus:</strong> <span id='state'>{values['state']}</span></p>
            <p><strong>Innen-Temperatur:</strong> <span id='temp_in'>{values['inside_temp']} °C</span></p>
            <p><strong>Außen-Temperatur:</strong> <span id='temp_out'>{values['outside_temp']} °C</span></p>
            <p><strong>Batteriestand:</strong> <span id='battery'>{values['battery_level']}%</span></p>
            <p><strong>Odometer:</strong> <span id='odometer'>{values['odometer']} km</span></p>
            <div class='tpms'>
                <div>FL: <span id='tpms_fl'>{values['tpms_pressure_fl']}</span> bar</div>
                <div>FR: <span id='tpms_fr'>{values['tpms_pressure_fr']}</span> bar</div>
                <div>RL: <span id='tpms_rl'>{values['tpms_pressure_rl']}</span> bar</div>
                <div>RR: <span id='tpms_rr'>{values['tpms_pressure_rr']}</span> bar</div>
            </div>
            {map_html}
        </div>
        <script>
            async function update() {{
                const r = await fetch('/data');
                if (!r.ok) return;
                const d = await r.json();
                document.getElementById('state').textContent = d.state;
                document.getElementById('temp_in').textContent = d.inside_temp + ' \u00b0C';
                document.getElementById('temp_out').textContent = d.outside_temp + ' \u00b0C';
                document.getElementById('battery').textContent = d.battery_level + '%';
                document.getElementById('odometer').textContent = d.odometer + ' km';
                document.getElementById('tpms_fl').textContent = d.tpms_pressure_fl;
                document.getElementById('tpms_fr').textContent = d.tpms_pressure_fr;
                document.getElementById('tpms_rl').textContent = d.tpms_pressure_rl;
                document.getElementById('tpms_rr').textContent = d.tpms_pressure_rr;
                if (d.latitude !== null && d.longitude !== null) {{
                    document.getElementById('map').src =
                        `https://maps.google.com/maps?q=${{d.latitude}},${{d.longitude}}&z=15&output=embed`;
                }}
            }}
            update();
            setInterval(update, 10000);
        </script>
    </body>
    </html>
    """
    return html


@app.route('/data')
def data():
    try:
        values = fetch_vehicle_values()
    except Exception as e:
        return Response(str(e), status=500)
    return jsonify(values)


@app.route("/login")
def login():
    code_verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b"=").decode("ascii")
    session["code_verifier"] = code_verifier
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    state = secrets.token_urlsafe(16)
    session["state"] = state
    params = parse.urlencode(
        {
            "client_id": CLIENT_ID,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email offline_access",
            "state": state,
        }
    )
    return redirect(f"{AUTH_URL}?{params}")


@app.route("/oauth/callback")
def oauth_callback():
    if request.args.get("state") != session.get("state"):
        return Response("Ungültiger State", status=400)
    code = request.args.get("code")
    if not code:
        return Response("Fehlender Code", status=400)
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "code_verifier": session.get("code_verifier"),
        "redirect_uri": REDIRECT_URI,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(TOKEN_URL, data=data)
    req.add_header("Content-Type", "application/json")
    try:
        with urlrequest.urlopen(req) as resp:
            token_data = json.load(resp)
    except error.URLError as e:
        return Response(f"Token-Anforderung fehlgeschlagen: {e}", status=500)
    session["tesla_token"] = token_data.get("access_token")
    session["refresh_token"] = token_data.get("refresh_token")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8066)
