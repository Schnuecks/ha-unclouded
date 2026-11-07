# Unclouded-Anleitung

[English](guide.md) · **Deutsch**

Diese Anleitung erklärt das Panel Schritt für Schritt und wie Unclouded zu seinen
Ergebnissen kommt. Einen kurzen Überblick und die Installation gibt es in der
[README](../README.de.md).

- [Das Panel](#das-panel)
- [Was die Gruppen bedeuten](#was-die-gruppen-bedeuten)
- [Wie Unclouded Integrationen einstuft](#wie-unclouded-integrationen-einstuft)
- [Wie Automationen verfolgt werden](#wie-automationen-verfolgt-werden)
- [Wichtige Automationen und Reparaturen](#wichtige-automationen-und-reparaturen)
- [Die Vorschläge](#die-vorschläge)
- [Fragen](#fragen)

## Das Panel

Öffne **Unclouded** in der Seitenleiste. Nur Administratoren sehen es. Von oben nach unten:

1. **Übersicht:** wie viele Automationen ohne Internet weiterlaufen, als große Zahl und als
   Balken, aufgeteilt in laufen weiter, verlieren nur Benachrichtigungen, verlieren Funktion
   oder fallen aus, und unklar. Ein Klick auf einen Eintrag der Legende springt zur ersten
   Automation dieser Art.
2. **Worum geht es?** Eine kurze Erklärung, beim ersten Besuch aufgeklappt. **Verstanden**
   schließt sie in diesem Browser dauerhaft.
3. **Bitte festlegen** (nur wenn nötig): Integrationen, die nicht angeben, wie sie sich
   verbinden. Wenn du es weißt, wähle lokal, Cloud oder teilweise lokal. Ist alles
   festgelegt, heißt der Kasten **Von dir festgelegt** und bleibt stehen, damit du es wieder
   ändern kannst.
4. **Was du tun kannst:** Vorschläge aus deiner Einrichtung, das Nützlichste zuerst. Jeder
   sagt, warum er wichtig ist und wie es geht; **Betrifft … Automationen** zeigt die
   Automationen, denen er hilft.
5. **Listen der Automationen**, sortiert danach, was ohne Internet mit ihnen passiert. Jede Automation hat einen Satz zur Begründung, **Öffnen ›** führt in den
   Automationseditor, und **Technische Details** zeigt jeden Auslöser, jede Bedingung und
   jede Aktion, die Internet braucht, mit der Integration dahinter und dem Grund.
6. **Sprachassistent:** jede Assist-Pipeline mit Aktivierungswort, Sprache zu Text,
   Gesprächsagent und Text zu Sprache, ob jeder Schritt ohne Internet geht, und die
   Sprachsatelliten, die sie nutzen.
7. **Echte Ausfälle:** was bei den letzten Ausfällen wirklich nicht erreichbar war, verglichen
   mit der Einschätzung von Unclouded (siehe unten).
8. **Integrationen:** jede eingerichtete Integration mit ihrer Einstufung und dem Grund.

Jede Änderung im Panel wird unten im Bild bestätigt.

## Was die Gruppen bedeuten

Die Übersicht und die Listen darunter nutzen dieselben vier Gruppen und Farben:

| Gruppe | Bedeutung |
|---|---|
| **Verlieren Funktion oder fallen aus** (rot) | Ohne Internet löst die Automation nicht aus, eine Bedingung lässt sich nicht prüfen oder etwas wird nicht geschaltet. **fällt ganz aus** markiert die, die dann gar nichts mehr tun. |
| **Verlieren nur Benachrichtigungen** (orange) | Was die Automation schaltet, läuft weiter; nur ihre Benachrichtigungen kommen nicht an. Automationen, die nur benachrichtigen, zählen auch hierher. |
| **Unklar** (grau) | Nichts braucht bekanntermaßen Internet, aber ein Teil ließ sich nicht einstufen. |
| **Laufen weiter** (grün) | Alles, was sie nutzt, ist bei dir zu Hause oder in Home Assistant. |

## Wie Unclouded Integrationen einstuft

Jede Integration gibt an, wie sie sich verbindet (ihre `iot_class`): lokal, Cloud oder in
Home Assistant berechnet. Unclouded geht davon aus und korrigiert, wo das nicht reicht:

- **Hängt von der Einrichtung ab:** Manche Integrationen laufen je nach Einrichtung lokal oder
  über die Cloud. Unclouded liest den Modus aus den Einstellungen der Integration.
- **Handys (Companion App):** lokal, solange das Handy zu Hause ist, unterwegs über das
  Internet – angezeigt als teilweise lokal.
- **Push-Nachrichten:** Sie sehen lokal aus, laufen aber über einen Relay-Server im Internet,
  außer in der App ist Lokaler Push eingeschaltet.
- **Hardware-Adapter** wie Zigbee- oder Thread-Sticks gelten als lokal, **Helfer** wie
  Gruppen, Templates oder Ableitungen als so abhängig wie die Entitäten, aus denen sie
  rechnen.
- **Unbekannt:** Eine Integration ohne Angabe gilt als unbekannt. Du kannst sie unter **Bitte
  festlegen** einstufen. Unclouded lässt dich nur solche Lücken füllen: Was es selbst
  ermittelt hat, lässt sich nicht überstimmen, und deine Wahl zählt nicht mehr, sobald die
  Integration eine Angabe macht.

Ist eine Integration falsch eingestuft? Bitte ein Issue eröffnen, damit eine Regel es für
alle korrigiert.

## Wie Automationen verfolgt werden

Unclouded geht die Auslöser, Bedingungen und Aktionen jeder Automation durch und folgt

- **Entitäten, Geräten und Bereichen** bis zur Integration dahinter,
- **Skripten**, die eine Automation aufruft, in deren eigene Aktionen,
- **Szenen**, gespeicherten und solchen, die mit `scene.apply` oder `scene.create` gesetzt
  werden,
- **Helfern** (Gruppen, Templates, Ableitungen, Verbrauchszähler …) bis zu ihren Quellen,
- **Zonen und Personen** bis zu den Trackern dahinter. Eine Person mit mindestens einem
  Tracker im Heimnetz, etwa vom Router, gilt als lokal,
- **Benachrichtigungen** bis zur Integration und zu ihrem Zustellweg.

Templates werden nach den Entitäten durchsucht, die sie lesen (`states()`, `state_attr()`,
`is_state()`, `states.sensor.x` …). Liest ein Template einen Cloud-Wert mit Ersatzwert, etwa
`float(10)` oder `default(0)`, läuft die Automation ohne Internet weiter, entscheidet aber nach
dem Ersatzwert; das meldet Unclouded eigens. Entity-IDs, die ein Template erst zur Laufzeit
bildet, lassen sich nicht verfolgen und werden ausgelassen.

In einer **Oder**-Bedingung hält ein Cloud-Wert die Automation nicht auf, solange ein anderer
Zweig der Bedingung lokal funktioniert.

## Wichtige Automationen und Reparaturen

Markiere eine Automation mit **★**, wenn es auf sie ankommt, etwa bei einem Alarm. Solange sie
Internet braucht, führt Home Assistant sie unter **Einstellungen → Reparaturen** und sagt, ob
sie ausfällt, nur teilweise läuft oder nur ihre Benachrichtigungen verliert. Nimm den Stern
weg oder sorge dafür, dass die Automation lokal funktioniert, dann verschwindet der Hinweis.

Unclouded merkt sich außerdem, wie sich jede Integration verbunden hat. Braucht eine nach
einem Update mehr Internet als vorher, etwa vorher lokal und jetzt Cloud, nennt ein
Reparaturhinweis sie. Bestätige ihn mit **OK**; gemeldet wird erst wieder, wenn es sich
erneut ändert. Neue Integrationen und Verbesserungen werden nicht gemeldet.

Unclouded prüft das nach dem Start von Home Assistant, wenn Automationen neu geladen werden,
stündlich und nach jeder Änderung im Panel.

## Die Vorschläge

| Vorschlag | Wann er erscheint |
|---|---|
| **Lokalen Push einschalten** | Benachrichtigungen an ein Handy laufen über den Relay-Server. |
| **Wichtigen Meldungen einen zweiten, lokalen Weg geben** | Eine Automation schickt nur Push-Nachrichten. |
| **Anwesenheit auch lokal erkennen** | Kommen und Gehen kommt nur von Handys. Sieht eine Router-Integration das Handy schon, wird ihr Eintrag genannt, auch wenn er noch deaktiviert ist. |
| **Werte prüfen, die ohne Internet ersetzt werden** | Ein Template liest einen Cloud-Wert mit Ersatzwert. |
| **Geräte und Dienste aus der Cloud** | Eine Automation hängt an einer Cloud-Integration. Jede wird mit einem bekannten lokalen Weg genannt, falls es einen gibt. |
| **Durchsagen lokal erzeugen** | Gesprochene Durchsagen erzeugt ein Cloud-Dienst. Feste Sätze spielt Home Assistant aus seinem Zwischenspeicher ab, auch ohne Internet. |

Jeder Vorschlag verlinkt die Seite, auf der du ihn umsetzt, und die betroffenen Automationen
führen in ihren Editor. Unclouded selbst ändert nichts.

## Echte Ausfälle

Der Sensor **Internet** (`binary_sensor.unclouded_internet`) zeigt, ob Home Assistant das
Internet erreicht. Einmal pro Minute baut Unclouded eine Verbindung zu den öffentlichen
DNS-Servern 1.1.1.1 und 9.9.9.9 auf Port 53 auf und schließt sie wieder; gesendet wird nichts.
Erst wenn zweimal hintereinander keiner antwortet, gilt das Internet als weg. Ausfälle unter
zwei Minuten werden nicht behalten.

Nach einem Ausfall zeigt das Panel, was in der Zeit wirklich nicht erreichbar war, vom Beginn
des Ausfalls bis fünf Minuten nach seinem Ende:

- **wie erwartet ausgefallen:** Cloud-Integrationen, deren Entitäten weg waren,
- **als lokal eingestuft, aber ausgefallen:** ein Hinweis, dass etwas anderes beteiligt war,
  etwa eine Cloud-Anmeldung oder eine Bridge,
- **als Cloud eingestuft, lief aber weiter:** nur nach Ausfällen ab 30 Minuten; vielleicht
  läuft sie doch lokal, oder sie zeigt gespeicherte Werte.

Was rund um einen Neustart von Home Assistant nicht erreichbar war, bleibt außen vor.

## Fragen

**Trennt Unclouded zum Testen das Internet?** Nein. Es arbeitet mit dem, wie sich
Integrationen verbinden, und ändert nie etwas. Das Ergebnis ist eine Einschätzung; nach einem
echten Ausfall zeigt das Panel, wie gut sie gepasst hat.

**Ein Alarm, der nur eine Benachrichtigung schickt, steht unter „Verlieren nur
Benachrichtigungen“, obwohl er dann gar nichts tut. Warum?** Weil die Benachrichtigung alles
ist, was er verliert. Bei einem Alarm ist genau das der wichtige Teil: Markiere ihn mit ★ und
gib ihm einen zweiten, lokalen Weg, wie es die Vorschläge beschreiben.

**Eine Integration läuft lokal, aber Unclouded sagt Cloud.** Bitte ein Issue mit der
Integration und ihrer Einrichtung eröffnen.

**Was speichert Unclouded?** Deine Wahl für unbekannte Integrationen und die wichtigen
Automationen in seinem Config-Eintrag, dazu die Handys, bei denen lokaler Push gesehen
wurde; den zuletzt bekannten Stand jeder Integration in `.storage/unclouded.baseline`; die
letzten zehn Ausfälle in `.storage/unclouded.outages`. Entfernst du Unclouded, verschwindet
all das samt seinen Reparaturhinweisen.
