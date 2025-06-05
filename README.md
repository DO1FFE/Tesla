# Tesla Weboberfläche

Dieses Repository stellt eine einfache Flask-Webseite bereit, die
Grundinformationen eines Tesla-Fahrzeugs über die Tesla Owner API anzeigt.

## Voraussetzungen

* Python 3
* Flask (`pip install flask`)
* Netzwerkzugriff auf die Tesla Owner API
* Ein gültiges Tesla-API-Token, gespeichert in der Umgebungsvariable
  `TESLA_TOKEN`

## Verwendung

1. Einen Zugangstoken für dein Tesla-Konto erstellen.
2. Die Umgebungsvariable `TESLA_TOKEN` setzen:

```bash
export TESLA_TOKEN=dein_token
```

3. Die Webanwendung starten:

```bash
python3 tesla_web.py
```

4. Im Browser `http://localhost:8066/` öffnen (oder die entsprechende Adresse
deines Servers), um den Fahrzeugstatus zu sehen.

Die Anwendung ruft dein erstes registriertes Fahrzeug ab und zeigt dessen
Status, Innen- und Außentemperatur sowie den Batteriestand an. 
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

Für die Anmeldung per OAuth müssen bestimmte Umgebungsvariablen gesetzt sein.
Um Flask-Sitzungen sicher zu signieren, wird insbesondere `FLASK_SECRET_KEY`
benötigt.

```bash
export FLASK_SECRET_KEY=ein_geheimer_schlüssel
```

