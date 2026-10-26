# ha-unclouded – Konzept (Entwurf)

Stand: 2026-10-26 · privates Repo, kein Zeitdruck

## Problem

Wer HA betreibt, weiß meist nicht genau, was bei einem Internetausfall (oder wenn ein Hersteller seine
Cloud abschaltet) noch funktioniert. HA zeigt nur pro Integration ein Globus-Symbol („Requires Internet“),
aber nicht, welche **Automationen, Szenen, Skripte und Dashboards** davon betroffen sind.
Kein bekanntes Werkzeug rechnet das für die eigene Installation aus (siehe Recherche
`/work/reports/HA Add-on Ideen Lückenanalyse.md`).

## Ziel

Eine Antwort auf: **„Was geht bei mir kaputt, wenn das Internet weg ist – und was davon ist mir wichtig?“**

## Befund auf home (Probe 2026-10-26)

- `manifest/list` + `config_entries/get` liefern die iot_class aller genutzten Integrationen:
  cloud_polling 5, cloud_push 5, local_polling 20, local_push 21, calculated 5, ohne Angabe 1 (`plant`).
- `search/related` liefert pro Automation Entitäten, Geräte, Config-Entries **und Integrationen** direkt –
  die Kette Automation → Integration ist damit ohne eigenes Parsen da (Beispiel `automation.bambu_abschalten`
  → matter, bambu_lab).
- **Wichtigste Erkenntnis: iot_class allein stimmt nicht.**
  - `tronity` (custom) meldet `local_polling`, spricht aber mit einer Cloud-API.
  - `xiaomi_miot`, `bambu_lab`, `sonoff` können je nach Einrichtung lokal *oder* über die Cloud laufen –
    das hängt vom Config-Entry ab, nicht von der Integration.
  - `calculated`/Helfer (group, template) erben die Abhängigkeit ihrer Quellen.
  → Der Mehrwert gegenüber dem Globus-Symbol liegt genau hier: Korrekturen pro Config-Entry
    und Vererbung über Helfer.

## Probe 2: alle 35 Automationen auf home (2026-10-26)

Ergebnis grob: nur ~10 von 35 laufen ohne Internet vollständig; ~23 schicken iPhone-Push, die ohne
Internet nicht ankommt; 2 hängen an Anwesenheit über das Handy.

Was daraus fürs Design folgt:
- **`search/related` reicht nicht.** Es liefert Entitäten/Integrationen, aber **keine Aktionen**
  (`notify.*`, `tts.*`). Die größte Abhängigkeit steckt aber genau dort → Automationen müssen zusätzlich
  geparst werden (Aktionen, auch in Skripten und choose/if-Zweigen).
- **Benachrichtigungen sind der Hauptfall.** `mobile_app` meldet `local_push`, die Push läuft aber über
  Apple/Google → braucht Internet. Ausnahme: iOS-„Local Push“, wenn das Handy im Heim-WLAN ist
  → Einstufung „teilweise“. Automatisch lesbar: Config-Entry `mobile_app` → `data.app_data.push_url`
  (home: `https://mobile-apps.home-assistant.io/...` = Relay im Internet); Local-Push-Fähigkeit
  über `app_data.push_websocket_channel` (auf home bei keinem Gerät gesetzt, und
  „Lokaler Push“ ist in der App tatsächlich aus – vom Nutzer bestätigt; ein Datenpunkt, mit
  eingeschaltetem Local Push noch gegenprüfen). `notify.pushover` (cloud_push) und `tts.home_assistant_cloud` korrekt erkannt.
- **Teilweise ist wichtig:** z. B. Überhitzungsschutz schaltet lokal ab (läuft), nur die Meldung fehlt.
  Ausgabe muss zwischen „Aktion fällt aus“ und „nur Meldung fällt aus“ unterscheiden.
- **Kritische Fälle hervorheben:** Notstrom-Meldungen bei Stromausfall – genau dann ist das Internet
  oft auch weg. Idee: Nutzer markiert Automationen als „wichtig“, nur dafür ein Repair-Hinweis.
  Aber: auf home hängt die Fritzbox per PoE-Adapter an der FOSSiBOT → Internet bleibt bei Stromausfall,
  solange der Kabelanbieter selbst Strom hat. Das Tool darf also nicht pauschal „kritisch“ sagen,
  sondern nur „hängt am Internet“; die Bewertung macht der Nutzer.
  (Intern, später: Szenario „Strom weg“ ≠ „Internet weg“ – was hängt an der Notstromversorgung?)
- **Anwesenheit:** Zonen-Trigger (alle weg / wieder da) hängen daran, wie das Handy HA von unterwegs
  erreicht (externe URL / Nabu Casa / VPN) → ohne Internet bleibt der Zähler stehen. Erkennbar über
  `zone`/`person`/`device_tracker` aus `mobile_app`. Der Zugangsweg muss nicht bekannt sein:
  Standortmeldungen von unterwegs brauchen immer das Internet am Zuhause (home: WireGuard/wg-easy).
- **Korrekturliste bestätigt:** `sonoff` (Modus lokal/cloud), `xiaomi_miot` (Modus), `tronity` (Cloud).
  Erste Regeln, aus dem Config-Entry lesbar (also automatisch, ohne Nutzerfrage):
  - `sonoff`: `options.mode` = local → lokal; auto → lokal mit Cloud-Rückfall (lokal, sofern das Gerät
    „LAN control“ an hat – das steht nicht im Entry, Hinweis anzeigen); cloud → Cloud.
    home: auto + LAN control an → lokal (vom Nutzer bestätigt).
  - `xiaomi_miot`: `data.conn_mode` = local / cloud / auto; auto heißt je Gerät/Eigenschaft
    unterschiedlich → „unbekannt, vermutlich teilweise“. home: auto.
- **Lücken der Probe:** Entitäten ohne Registry-Eintrag (YAML-`sensor`, `input_*`) ohne Plattform;
  Template-Quellen nur eine Ebene tief aufgelöst; `plant` ohne iot_class.

## Umfang 1.0 (nur das)

Offline-Analyse als HACS-Integration, nur lesend. Fertig = 1.0. Nichts darüber hinaus ankündigen.

### Analyse (HACS-Integration, nur lesen)
1. Klassifizierung je Config-Entry: lokal / Cloud / Cloud nur bei Einrichtung / unbekannt.
   Quellen: iot_class, eingebaute Korrekturliste (z. B. tronity), Einstellungen des Entries (Modus lokal/cloud),
   manuelle Übersteuerung durch den Nutzer.
2. Vererbung: Helfer, Gruppen, Template-Sensoren übernehmen die „schlechteste“ Abhängigkeit ihrer Quellen.
3. Auswertung pro Automation/Skript/Szene: **läuft weiter / teilweise / fällt aus** – mit Begründung
   („Trigger lokal, Aktion `notify.pushover` braucht Cloud“).
4. Ausgabe: eigenes Panel mit Übersicht + Sensoren (Anzahl betroffener Automationen) + Repair-Hinweis,
   wenn eine als wichtig markierte Automation an der Cloud hängt.
5. Warnung, wenn sich die Klasse einer Integration nach einem Update ändert.

## Ideen für später (intern – nicht in README, Roadmap oder Release-Texte)

Wird nur gebaut, wenn 1.0 sich bewährt hat; erscheint dann als Überraschung, nicht als Vorankündigung.
Architektur der 1.0 (Abhängigkeitsgraph) so anlegen, dass das andocken kann – mehr nicht.

- Konflikterkennung zwischen Automationen (Recherche-Idee 3), nutzt denselben Graphen.

### Abgleich mit der Wirklichkeit (ohne Eingriff)
- Bei einem echten Internetausfall (erkannt per eigenem Ping) mitschreiben, welche Entitäten
  `unavailable` werden und welche Automationen fehlschlagen → Vorhersage gegen Realität prüfen,
  Korrekturliste verbessern. Kein Risiko, weil nichts abgeschaltet wird.

### Simulation (vielleicht irgendwann)
- Ausgehenden Verkehr zeitlich begrenzt sperren (nur LAN erlauben), mit automatischem Rückbau.
- Erst nach gründlichen Tests auf einer Testinstanz; Risiko: HA danach von außen nicht erreichbar.
- Ob das überhaupt nötig ist, entscheidet sich nach Stufe 2.

### Simulation über eine Sandbox-Kopie (vielleicht irgendwann, erst nach Test der Geräte-Doppelverbindungen auf home)
- Simulation nicht am echten HA, sondern an einer **Kopie aus dem letzten Backup**, die LAN darf, aber kein Internet.
- In der Kopie: Automationen, Skripte, HomeKit-Bridge, Benachrichtigungen, Funkadapter (Zigbee/Thread-Funk) aus –
  sie soll nur **laden und beobachten**, nie schalten.
- Ergebnis der Kopie (welche Integrationen laden, welche Entitäten `unavailable` sind) ist die echte Antwort;
  die Analyse rechnet sie auf Automationen hoch und erklärt sie.
- Ohne Kopie bleibt die Analyse als reine Vorhersage nutzbar.
- Dieselbe Kopie mit einer **neueren HA-Version** gestartet = Update-Probelauf (Idee 1 der Recherche).
  Ein Motor, zwei Fragen: „Was geht ohne Internet?“ und „Was geht nach dem Update?“

Risiken: doppelte Verbindungen zu Geräten (ESPHome, MQTT-Client-IDs, Kameras), Geräte mit nur einem
Client, Matter-/Thread-Fabric, Speicherbedarf einer zweiten HA-Instanz. Eine App kann laut Recherche
keine weiteren Container starten → Kopie läuft im App-Container selbst. home läuft ohne Supervisor
(Container `hass`), dort wäre es ein eigener Container im Stack.

## Abgrenzung

- Kein Netzwerk-Monitor (dafür gibt es eigene Ping-/Leitungs-Werkzeuge).
- Keine Telemetrie, keine Cloud – das Werkzeug selbst ist rein lokal.
- Keine Überschneidung mit Nine Lives.
- Grundlage (Abhängigkeitsgraph) später wiederverwendbar für eine Konflikterkennung (Idee 3).

## Offene Fragen

- ~~Name~~ → ha-unclouded (2026-10-26).
- Wie erkennt man „lokal oder Cloud“ pro Config-Entry generisch? Je Integration eine Regel nötig?
- Aktionen wie `notify.*`, `tts.*`, `conversation.*` (z. B. anthropic) gesondert behandeln.
- Dashboards einbeziehen oder erst später?

## Nächste Schritte (ohne Eile)

1. Probe erweitern: alle 35 Automationen auswerten, Ergebnis von Hand gegenprüfen.
2. Korrekturliste für die eigenen Integrationen anlegen und daran sehen, wie viel Pflege das wird.
3. Erst dann entscheiden, ob es ein Projekt wird.
