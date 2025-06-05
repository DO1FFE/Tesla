# Tesla Weboberfläche

Dieses Repository stellt eine einfache Flask-Webseite bereit, die
Grundinformationen eines Tesla-Fahrzeugs über die Tesla Owner API anzeigt.

## Voraussetzungen

* Python 3
* Flask (`pip install flask`)
* Netzwerkzugriff auf die Tesla Owner API
* Entweder ein bereits erzeugtes Tesla-API-Token in der Umgebungsvariable
  `TESLA_TOKEN` oder ein Login über den integrierten OAuth-Fluss

## Verwendung

1. Die Webanwendung starten:

```bash
python3 tesla_web.py
```
2. Im Browser `http://localhost:8066/` öffnen (oder die entsprechende Adresse
deines Servers). Wenn kein Token in `TESLA_TOKEN` vorhanden ist, kannst du dich
über `/login` per OAuth anmelden.

Die Anwendung ruft dein erstes registriertes Fahrzeug ab und zeigt dessen
Status, Innen- und Außentemperatur sowie den Batteriestand an. Zusätzlich wird
eine kleine Karte mit der aktuellen Position des Fahrzeugs eingeblendet.
Ein Klick auf „Aktualisieren“ lädt die Seite neu.

## Tkinter-GUI

Zusätzlich zur Weboberfläche gibt es eine kleine Desktop-Anwendung,
die alle über die Tesla-API verfügbaren Parameter anzeigt. Auch hier muss
die Umgebungsvariable `TESLA_TOKEN` gesetzt sein.

```bash
python3 tesla_gui.py
```

Nach dem Start werden die Fahrzeugdaten abgerufen und in übersichtlichen
Abschnitten dargestellt. Über den Button „Aktualisieren" lassen sich die
Werte jederzeit neu laden.

## OAuth Login

Für die Anmeldung per OAuth muss Flask einen geheimen Schlüssel besitzen.
Setze dafür die Variable `FLASK_SECRET_KEY`:

```bash
export FLASK_SECRET_KEY=ein_geheimer_schluessel
```

Danach kann die Anmeldung über `/login` gestartet werden. Tesla leitet nach
dem Login auf `/oauth/callback` zurück und das erhaltene Access-Token wird in
der Sitzung gespeichert.
Optional lassen sich `TESLA_CLIENT_ID` und `TESLA_REDIRECT_URI` anpassen,
standardmäßig wird jedoch der offizielle `ownerapi`-Client und
`http://localhost:8066/oauth/callback` verwendet.

