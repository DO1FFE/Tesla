import json
import os
import sys
import webbrowser
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from urllib import request, error

LOGIN_URL = "https://auth.tesla.com/"

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

class TeslaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tesla Model S Anzeige")
        self.status_var = tk.StringVar()
        self.temp_in_var = tk.StringVar()
        self.temp_out_var = tk.StringVar()
        self.battery_var = tk.StringVar()
        self.client = None
        self.vehicle_id = None

        tk.Label(root, text="Fahrzeugstatus:").grid(row=0, column=0, sticky="w")
        tk.Label(root, textvariable=self.status_var).grid(row=0, column=1, sticky="w")

        tk.Label(root, text="Innen-Temperatur:").grid(row=1, column=0, sticky="w")
        tk.Label(root, textvariable=self.temp_in_var).grid(row=1, column=1, sticky="w")

        tk.Label(root, text="Außen-Temperatur:").grid(row=2, column=0, sticky="w")
        tk.Label(root, textvariable=self.temp_out_var).grid(row=2, column=1, sticky="w")

        tk.Label(root, text="Batteriestand:").grid(row=3, column=0, sticky="w")
        tk.Label(root, textvariable=self.battery_var).grid(row=3, column=1, sticky="w")

        tk.Button(root, text="Aktualisieren", command=self.refresh).grid(row=4, column=0, columnspan=2, sticky="we")

        self.text = ScrolledText(root, width=80, height=20)
        self.text.grid(row=5, column=0, columnspan=2, sticky="nsew")

        root.grid_rowconfigure(5, weight=1)
        root.grid_columnconfigure(1, weight=1)

        self.initialize_client()

    def initialize_client(self):
        token = os.getenv("TESLA_TOKEN")
        if not token:
            messagebox.showerror("Fehler", "Umgebungsvariable TESLA_TOKEN nicht gesetzt")
            self.root.destroy()
            return
        self.client = TeslaClient(token)
        try:
            vehicles = self.client.list_vehicles()
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            self.root.destroy()
            return
        if not vehicles:
            messagebox.showinfo("Information", "Keine Fahrzeuge gefunden")
            self.root.destroy()
            return
        self.vehicle_id = vehicles[0]["id"]
        self.refresh()

    def _format_data(self, data):
        lines = []
        for section in sorted(data.keys()):
            value = data[section]
            if isinstance(value, dict):
                lines.append(section + ":")
                for k in sorted(value.keys()):
                    lines.append(f"  {k}: {value[k]}")
            else:
                lines.append(f"{section}: {value}")
            lines.append("")
        return "\n".join(lines)

    def refresh(self):
        if not self.client or not self.vehicle_id:
            return
        try:
            data = self.client.vehicle_data(self.vehicle_id)
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
            return
        climate = data.get("climate_state", {})
        charge_state = data.get("charge_state", {})
        state = data.get("state", "unknown")
        self.status_var.set(state)
        self.temp_in_var.set(f"{climate.get('inside_temp', 'N/A')} °C")
        self.temp_out_var.set(f"{climate.get('outside_temp', 'N/A')} °C")
        self.battery_var.set(f"{charge_state.get('battery_level', 'N/A')}%")

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, self._format_data(data))

if __name__ == "__main__":
    if "--login" in sys.argv:
        webbrowser.open(LOGIN_URL)
    else:
        root = tk.Tk()
        app = TeslaApp(root)
        root.mainloop()
