import json
import os
import base64
import hashlib
import secrets
from urllib import request as urlrequest, error, parse
from flask import Flask, Response, redirect, request, session, url_for

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

@app.route('/')
def index():
    token = session.get('tesla_token') or os.getenv('TESLA_TOKEN')
    if not token:
        return redirect(url_for('login'))

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
