<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg"><img src="docs/logo.svg" width="96" alt="Unclouded"></picture></p>

# Unclouded

[English](README.md) · **Deutsch**

<p align="center">
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.10%2B-41BDF5?logo=homeassistant&logoColor=white" alt="Home Assistant 2026.10+">
  <img src="https://img.shields.io/badge/HACS-custom-41BDF5" alt="HACS Custom Repository">
  <a href="LICENSE"><img src="https://img.shields.io/badge/Lizenz-MIT-4C9A2A" alt="Lizenz MIT"></a>
  <img src="https://img.shields.io/badge/gepflegt-ja-4C9A2A" alt="Gepflegt">
</p>

Unclouded zeigt, was in deinem Home Assistant noch läuft, wenn das Internet weg ist, und
was du für den Rest tun kannst.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/overview-de-dark.png"><img src="docs/screenshots/overview-de.png" width="720" alt="Übersicht und Vorschläge"></picture></p>

## Warum es das gibt

Mein Home Assistant läuft zu Hause, also bin ich davon ausgegangen, dass er auch ohne
Internet weitermacht. Als ich genauer hingeschaut habe, war das bei vielem nicht so.
Benachrichtigungen ans Handy liefen über einen Relay-Server im Internet. Ob jemand zu Hause
ist, kam nur von den Handys. Und die Erinnerung, das Badfenster zu schließen, holte die
Außentemperatur von einem Wetterdienst, mit 10 °C als Ersatzwert. Ohne Internet hätte sie
also jedes Mal still mildes Wetter angenommen.

Home Assistant zeigt bei jeder Integration, ob sie die Cloud nutzt. Was das für die eigenen
Automationen heißt, zeigt es nicht. Genau da setzt Unclouded an.

## Was es macht

Unclouded geht jede Automation durch, folgt Skripten, Szenen, Helfern, Personen und
Templates bis zu den Integrationen dahinter und sortiert die Automationen danach, ob sie
weiterlaufen, nur ihre Benachrichtigungen verlieren oder ausfallen. Zu jeder gibt es einen
kurzen Satz mit dem Grund, etwa „Benachrichtigung an Alex's phone kommt nicht an“.

Dazu kommen Vorschläge, die zu deiner Einrichtung passen: lokalen Push einschalten,
wichtigen Meldungen einen zweiten Weg geben, der zu Hause funktioniert, Anwesenheit auch über
den Router erkennen (mit dem passenden Router-Eintrag für jedes Handy) und welche
Cloud-Integrationen eine lokale Alternative haben. Jeder Vorschlag führt direkt zu der Seite,
auf der du ihn umsetzt.

Außerdem prüft Unclouded die Pipelines deines Sprachassistenten, meldet, wenn eine
Integration nach einem Update mehr Internet braucht als vorher, und du kannst wichtige
Automationen mit einem Stern markieren, damit sie unter Reparaturen auftauchen. Ein kleiner
Sensor beobachtet die Verbindung, und nach einem echten Ausfall zeigt das Panel, was
wirklich weg war. So siehst du, wie gut die Einschätzung gepasst hat.

Unclouded liest nur. An deiner Einrichtung ändert es nichts.

## So funktioniert es

1. Öffne **Unclouded** in der Seitenleiste. Oben steht, wie viele Automationen ohne
   Internet weiterlaufen.
2. **Was du tun kannst** listet die Vorschläge, das Nützlichste zuerst.
3. Darunter stehen alle Automationen, sortiert danach, was mit ihnen passiert.
   **Technische Details** zeigt, welcher Auslöser, welche Bedingung oder Aktion Internet
   braucht und warum.

   <picture><source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/automations-de-dark.png"><img src="docs/screenshots/automations-de.png" width="640" alt="Automationen, die nur ihre Benachrichtigungen verlieren"></picture>

4. Markiere wichtige Automationen mit einem Stern. Home Assistant führt sie dann unter
   **Einstellungen → Reparaturen**, solange sie vom Internet abhängen.

Die [Anleitung](docs/anleitung.md) geht das Panel im Detail durch und erklärt, wie Unclouded
zu seinen Ergebnissen kommt.

## Installation

Unclouded braucht Home Assistant 2026.10 oder neuer.

**HACS:** In HACS das Menü → **Benutzerdefinierte Repositories** öffnen,
`https://github.com/Schnuecks/ha-unclouded` mit dem Typ **Integration** hinzufügen, dann
**Unclouded** installieren und Home Assistant neu starten.

**Von Hand:** `custom_components/unclouded` in den Ordner `custom_components` deiner Home
Assistant-Konfiguration kopieren und neu starten.

Danach die Integration unter **Einstellungen → Geräte & Dienste → Integration hinzufügen →
Unclouded** hinzufügen. Das Panel erscheint für Administratoren in der Seitenleiste.

## Gut zu wissen

Es ist eine Einschätzung, kein Test. Unclouded trennt nie dein Internet, sondern arbeitet
damit, wie sich jede Integration verbindet. Manche Integrationen laufen je nach Einrichtung
lokal oder über die Cloud, und einige davon kennt Unclouded. Sagt eine nicht, wie sie sich
verbindet, kannst du es Unclouded selbst sagen.

Um echte Ausfälle zu bemerken, baut Unclouded einmal pro Minute eine Verbindung zu den
öffentlichen DNS-Servern 1.1.1.1 und 9.9.9.9 auf Port 53 auf und schließt sie wieder.
Gesendet wird nichts. Das ist die einzige Verbindung, die es selbst aufbaut.

Entity-IDs, die ein Template erst während der Automation bildet, lassen sich nicht verfolgen
und werden ausgelassen.

Ist etwas falsch eingestuft, eröffne bitte ein Issue mit der Integration und ihrer
Einrichtung, damit es für alle korrigiert wird. Siehe [CONTRIBUTING](CONTRIBUTING.md).

## Entwicklung

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
ruff check . && ruff format --check . && pytest
```

Siehe [CONTRIBUTING](CONTRIBUTING.md).

## Wie es entsteht

Unclouded entsteht mit Hilfe eines KI-Programmierassistenten. Ich lege Funktionen und
Verhalten fest, prüfe die Änderungen und teste sie in meinem eigenen Home Assistant.
Veröffentlicht wird nichts, was die automatischen Prüfungen nicht besteht: die Tests,
hassfest von Home Assistant und die HACS-Prüfung.

## Unterstützen

Unclouded ist kostenlos und bleibt es. Wenn es dir hilft, kannst du mir auf Ko-fi einen
Kaffee spendieren; das hält das Projekt am Laufen. Danke!

<p>
  <a href="https://ko-fi.com/schnuecks"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Unterstütze mich auf Ko-fi"></a>
</p>

## Rückmeldungen

Fehlerberichte und Ideen sind als
[GitHub-Issues](https://github.com/Schnuecks/ha-unclouded/issues) willkommen. Siehe auch
[CONTRIBUTING](CONTRIBUTING.md) und [SECURITY](SECURITY.md).

Was sich in jeder Version geändert hat, steht im [CHANGELOG](CHANGELOG.md).

**Was du erwarten kannst:** Unclouded ist ein Hobbyprojekt, das ich in meinem eigenen Home
Assistant nutze. Issues und Pull Requests schaue ich mir an, wenn ich Zeit habe, ohne
garantierte Antwortzeit.

## Lizenz

Copyright (c) 2026 Schnuecks. Veröffentlicht unter der [MIT-Lizenz](LICENSE).
