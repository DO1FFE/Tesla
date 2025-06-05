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
Die Werte aktualisieren sich automatisch alle 10&nbsp;Sekunden per AJAX und
zeigen zusätzlich Kilometerstand und Reifendrücke an.

## Tkinter-GUI

Zusätzlich zur Weboberfläche gibt es eine kleine Desktop-Anwendung,
die alle über die Tesla-API verfügbaren Parameter anzeigt. Auch hier muss
die Umgebungsvariable `TESLA_TOKEN` gesetzt sein.

```bash
python3 tesla_gui.py
```

Nach dem Start werden die Fahrzeugdaten abgerufen und in übersichtlichen
Abschnitten dargestellt. Die Werte werden alle 10&nbsp;Sekunden automatisch
aktualisiert und zeigen neben Temperatur und Batteriestand jetzt auch den
Kilometerstand sowie die Reifendrücke an. Über den Button „Aktualisieren" lässt
sich die Aktualisierung auch manuell anstoßen.

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


## Android-App (Kivy)

Neben der Desktop- und Webvariante gibt es nun auch ein einfaches Kivy-Programm, 
das sich zu einer Android-APK bauen lässt. Es zeigt die gleichen Fahrzeugdaten an 
wie die Tkinter-GUI.

1. Kivy und Buildozer installieren (am besten in einer Python-Virtualenv).
2. Mit `buildozer init` eine Buildozer-Konfiguration erzeugen und in `buildozer.spec`
   den Python-Quellcode `tesla_android.py` eintragen.
3. Anschließend kann die APK mit `buildozer -v android debug` gebaut werden.

Vor dem Start muss wie gewohnt die Umgebungsvariable `TESLA_TOKEN` gesetzt sein.

