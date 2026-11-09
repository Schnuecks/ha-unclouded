<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg"><img src="docs/logo.svg" width="96" alt="Unclouded"></picture></p>

# Unclouded

[English](README.md) · **Deutsch**

<p align="center">
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.10%2B-41BDF5?logo=homeassistant&logoColor=white" alt="Home Assistant 2026.10+">
  <img src="https://img.shields.io/badge/HACS-default-41BDF5" alt="In HACS verfügbar">
  <a href="LICENSE"><img src="https://img.shields.io/badge/Lizenz-MIT-4C9A2A" alt="Lizenz MIT"></a>
  <img src="https://img.shields.io/badge/gepflegt-ja-4C9A2A" alt="Gepflegt">
</p>

Unclouded zeigt, was in deinem Home Assistant noch läuft, wenn das Internet weg ist, und
was du für den Rest tun kannst.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/overview-de-dark.png"><img src="docs/screenshots/overview-de.png" width="720" alt="Übersicht und Vorschläge"></picture></p>

## Warum es das gibt

Mein Home Assistant läuft zu Hause, also dachte ich, er macht auch ohne Internet weiter.
Als ich genauer hingeschaut habe, war das bei vielem nicht so:

- Benachrichtigungen ans Handy liefen über einen Server im Internet.
- Ob jemand zu Hause ist, wusste Home Assistant nur über den Standort der Handys.
- Die Erinnerung, das Badfenster zu schließen, wenn es draußen kalt wird, holte die
  Temperatur von einem Wetterdienst im Internet. Ohne Internet wäre sie einfach nie gekommen.

Home Assistant zeigt bei jeder Integration, ob sie die Cloud nutzt. Was das für die eigenen
Automationen bedeutet, zeigt es nicht. Genau da setzt Unclouded an.

## Was es macht

Unclouded geht alle deine Automationen durch und verfolgt sie über Skripte, Szenen, Helfer,
Personen und Templates bis zu den Integrationen dahinter. Dann sortiert es sie in Gruppen:

- laufen weiter
- laufen, aber ihre Benachrichtigungen kommen nicht an
- fallen ganz oder teilweise aus

Zu jeder Automation gibt es einen kurzen Grund, zum Beispiel „Benachrichtigung an Annas
Handy kommt nicht an“.

Dazu bekommst du Vorschläge, die zu deiner Einrichtung passen, zum Beispiel:

- lokalen Push für die Companion-App einschalten
- wichtigen Meldungen einen zweiten Weg geben, der ohne Internet funktioniert
- Anwesenheit zusätzlich über den Router erkennen – Unclouded nennt dir für jedes Handy den
  passenden Router-Eintrag
- eine lokale Alternative nutzen, wo es für eine Cloud-Integration eine gibt

Jeder Vorschlag führt direkt zu der Seite, auf der du ihn umsetzt.

Außerdem prüft Unclouded deinen Sprachassistenten, meldet, wenn eine Integration nach einem
Update stärker vom Internet abhängt als vorher, und du kannst wichtige Automationen mit einem
Stern markieren, damit sie unter Reparaturen auftauchen. Ein kleiner Sensor behält deine
Verbindung im Blick. Nach einem echten Ausfall zeigt das Panel, was wirklich ausgefallen
ist. So siehst du, wie gut die Einschätzung gepasst hat.

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

**HACS:** Über den Knopf oder in HACS nach **Unclouded** suchen, herunterladen und Home
Assistant neu starten.

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Schnuecks&repository=ha-unclouded&category=integration)

**Von Hand:** `custom_components/unclouded` in den Ordner `custom_components` deiner Home
Assistant-Konfiguration kopieren und neu starten.

Danach die Integration unter **Einstellungen → Geräte & Dienste → Integration hinzufügen →
Unclouded** hinzufügen. Das Panel erscheint für Administratoren in der Seitenleiste.

## Gut zu wissen

Unclouded rechnet aus, was ohne Internet passieren würde – ausprobiert wird dabei nichts.
Grundlage ist, wie sich jede Integration verbindet: lokal oder über die Cloud. Bei manchen
Integrationen hängt das von der Einrichtung ab, viele davon kennt Unclouded. Erkennt es das
bei einer deiner Integrationen nicht, kannst du es selbst festlegen.

Um echte Ausfälle zu bemerken, verbindet sich Unclouded einmal pro Minute kurz mit den
öffentlichen DNS-Servern 1.1.1.1 und 9.9.9.9 auf Port 53. Daten sendet es dabei nicht. Das
ist die einzige Verbindung, die es selbst aufbaut.

Setzt ein Template eine Entity-ID erst zusammen, während die Automation läuft, kann
Unclouded sie nicht verfolgen und lässt sie aus.

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
