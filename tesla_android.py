import json
import os
from urllib import request, error

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

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

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.status = Label(text="Status: ?")
        self.inside_temp = Label(text="Innen-Temp: ?")
        self.outside_temp = Label(text="Außen-Temp: ?")
        self.battery = Label(text="Batterie: ?")
        self.odometer = Label(text="Odometer: ?")
        for w in [self.status, self.inside_temp, self.outside_temp, self.battery, self.odometer]:
            self.add_widget(w)

class TeslaAndroidApp(App):
    def build(self):
        token = os.getenv("TESLA_TOKEN")
        if not token:
            raise RuntimeError("Umgebungsvariable TESLA_TOKEN nicht gesetzt")
        self.client = TeslaClient(token)
        vehicles = self.client.list_vehicles()
        if not vehicles:
            raise RuntimeError("Keine Fahrzeuge gefunden")
        self.vehicle_id = vehicles[0]["id"]
        self.layout = MainLayout()
        Clock.schedule_interval(self.refresh, 10)
        self.refresh(0)
        return self.layout

    def refresh(self, dt):
        data = self.client.vehicle_data(self.vehicle_id)
        climate = data.get("climate_state", {})
        charge_state = data.get("charge_state", {})
        vehicle_state = data.get("vehicle_state", {})
        self.layout.status.text = f"Status: {data.get('state', 'N/A')}"
        self.layout.inside_temp.text = f"Innen-Temp: {climate.get('inside_temp', 'N/A')} °C"
        self.layout.outside_temp.text = f"Außen-Temp: {climate.get('outside_temp', 'N/A')} °C"
        self.layout.battery.text = f"Batterie: {charge_state.get('battery_level', 'N/A')}%"
        self.layout.odometer.text = f"Odometer: {vehicle_state.get('odometer', 'N/A')} km"

if __name__ == '__main__':
    TeslaAndroidApp().run()
