// Unclouded sidebar panel. Plain web component without build step or dependencies;
// it talks to the integration through the unclouded/* WebSocket commands.

const STRINGS = {
  en: {
    intro: "What keeps working in your Home Assistant when the internet is down.",
    refresh: "Check again",
    section_loss: "Lose function or stop",
    section_notify: "Only lose their notifications",
    section_unknown: "Not sure",
    section_works: "Keep working",
    hint_loss: "Without the internet these are not triggered or do not switch something.",
    hint_notify: "What these switch keeps working; only their messages do not arrive without the internet.",
    hint_unknown: "Nothing here is known to need the internet, but some parts could not be checked.",
    hint_works: "These only use things inside your home.",
    stopsCompletely: "stops completely",
    open: "Open",
    markImportant: "Mark as important: Home Assistant then reports under Repairs when it needs the internet",
    unmarkImportant: "Marked as important; click to remove",
    decide: "Please decide",
    decideHint:
      "These integrations do not say how they connect. If you know, choose it here; the automations are judged again right away.",
    notChosen: "Unknown – choose…",
    choice_local: "Local",
    choice_cloud: "Cloud",
    choice_partial: "Partly local",
    yourChoice: "your choice",
    decided: "Decided by you",
    decidedHint: "You classified these integrations yourself. You can change it here at any time.",
    integrationNoEntry: "entities without config entry",
    // Summary and explanation
    heroLabel: "If the internet goes down",
    heroOf: "of {total}",
    heroText: "automations keep working as usual",
    legend_works: "keep working",
    legend_notify: "only lose their notifications",
    legend_loss: "lose function or stop",
    legend_unknown: "not sure",
    summaryAllGood: "Everything runs inside your home. An internet outage does not affect your automations.",
    whatTitle: "What is this about?",
    whatText1:
      "Many devices and services in Home Assistant work through servers on the internet: those of the manufacturer, of Apple or Google, or of a cloud service. If the internet is down, the provider has an outage or switches its service off, something at home stops working too.",
    whatText2:
      "Unclouded checks every automation: what triggers it, what it checks and what it does. It shows what still works without the internet, what does not, and what you can do so that the important things keep working.",
    whatText3: "Unclouded only reads. It changes nothing in your setup.",
    hide: "Got it",
    // Advice
    adviceTitle: "What you can do",
    adviceHint: "Suggestions worked out from your setup, the most useful first.",
    affects: "Concerns {n} automations",
    affects1: "Concerns 1 automation",
    showAffected: "Show affected automations",
    noAdvice: "Nothing to do. Well done.",
    advice_local_push_title: "Turn on local push",
    advice_local_push_why:
      "Notifications to {entries} go through a relay server on the internet. Without internet they do not arrive, not even while you are at home.",
    advice_local_push_how:
      "In the Home Assistant app: Settings → Companion App → tap your server → “Internal URL”. Enter the address of Home Assistant in your home network (for example http://192.168.1.10:8123), add the name of your home Wi-Fi and leave “Local Push” on. The app needs location access to recognise the Wi-Fi. While the phone is on that Wi-Fi, notifications then arrive without the internet.",
    advice_local_fallback_title: "Give important alerts a second, local way",
    advice_local_fallback_why:
      "These automations only send a push notification. Without internet you would not notice anything, however important it is.",
    advice_local_fallback_how:
      "For the ones that matter, add a signal that works at home: let a light flash, make an announcement on a speaker or show a message on the TV. Mark them with ★ and Home Assistant reminds you under Repairs while they still depend on the internet.",
    advice_presence_title: "Detect presence locally as well",
    advice_presence_why:
      "So far Home Assistant only learns from the phones whether someone is at home. While away, they report their location over the internet. If it is down, the last known state stays put, and automations that react to coming or going do not run.",
    advice_presence_how_helpers:
      "The {helpers} integrations already see which devices are on your Wi-Fi. Find the phone there and add it to the person as another device (Settings → People). Home Assistant then knows without the internet whether someone is at home.",
    advice_presence_how_helpers1:
      "The {helpers} integration already sees which devices are on your Wi-Fi. Find the phone there and add it to the person as another device (Settings → People). Home Assistant then knows without the internet whether someone is at home.",
    advice_presence_how:
      "Set up an integration for your router or Wi-Fi that sees which devices are connected, and add the phone found there to the person (Settings → People).",
    advice_substitutes_title: "Check values that are replaced without the internet",
    advice_substitutes_why:
      "These automations read values from {entries} in a template with a fallback, for example float(10). Without the internet they keep running, but with the fallback instead of the real value – often without anyone noticing.",
    advice_substitutes_how:
      "Use a sensor in your home where there is one (for example your own outdoor sensor instead of a weather service). Otherwise check in the template with has_value() whether the value is there, and decide what should happen without it.",
    advice_cloud_devices_title:
      "Devices and services in the cloud",
    advice_cloud_devices_why:
      "With {entries}, everything comes from servers on the internet. Without internet, or once the provider shuts the service down, nothing responds.",
    advice_cloud_devices_how:
      "For each integration, whether there is a local way:",
    advice_local_tts_title: "Make announcements locally",
    advice_local_tts_why: "Spoken announcements are created by a cloud service ({entries}).",
    advice_local_tts_how:
      "Two ways that also work on small hardware: Home Assistant keeps every announcement it has created once (folder tts) and plays it again from there, even without the internet – so use a fixed sentence for important announcements, without changing values in it. Or use local text-to-speech such as Piper only as a fallback while the internet is down; for short sentences it is fast enough even on small machines.",
    // Concrete steps with links
    stepsLabel: "Go to:",
    link_integration: "{name} settings",
    link_people: "People",
    link_wyoming: "Add Wyoming",
    link_piper: "Piper add-on",
    link_whisper: "Whisper add-on",
    link_assistants: "Voice assistants",
    pushPending: "Unclouded notices it by itself once the phone is on your Wi-Fi with local push on; this can take up to 10 minutes.",
    alt_sonoff: "Set the mode to “auto” or “local” in the integration's options.",
    alt_xiaomi_miot: "Choose the connection mode “auto” or “local” for this entry.",
    alt_tuya: "Tuya Local or LocalTuya (HACS) control many Tuya devices directly in your Wi-Fi.",
    alt_switchbot_cloud: "The SwitchBot Bluetooth integration controls many SwitchBot devices locally.",
    alt_tado: "tado° devices can also be added locally: older ones through HomeKit Device, tado° X through Matter.",
    alt_meross_cloud: "Meross LAN (HACS) controls Meross devices directly in your network.",
    alt_weather: "Weather data comes from the internet by nature. A local weather station, for example through Ecowitt, keeps working.",
    alt_none:
      "No local way is known for {name}. For devices, prefer ones with Matter, Zigbee or a local API when you replace them.",
    // Sentences per automation
    say_notify_lost: "notification to {who} does not arrive",
    say_notify_home: "notification to {who} only arrives at home",
    say_tts: "announcement via {who} is not made",
    say_trigger: "{what} ({who}) comes from the cloud, so the automation is not triggered",
    say_presence: "presence from phones only arrives over the internet while away",
    say_trigger_partial: "{what} ({who}) only arrives over the internet while away, so the automation may not be triggered",
    say_condition: "condition on {what} ({who}) cannot be checked",
    say_action: "{what} ({who}) is not switched",
    say_substitute: "without the internet {what} ({who}) is replaced by a fixed value, so the automation decides on that value",
    say_alternative: "without the internet {what} ({who}) cannot be checked, but the other options of the condition still work",
    say_unknown: "unclear how {what} connects",
    say_all_local: "uses only devices in your home",
    details: "Technical details",
    howLabel: "How:",
    matchIntro: "Found in your setup:",
    matchKnown: "{integration} knows this phone as “{tracker}” ({entity}).",
    matchDisabled:
      "The entry is still disabled: Settings → Devices & services → Entities → open “{tracker}” → cog → turn on “Enabled”.",
    matchAssign: "Then Settings → People → {person} → add {entity} under “Track device”.",
    matchApple:
      "So that the router recognises the iPhone again and again: on the iPhone, Settings → Wi-Fi → ⓘ next to your home Wi-Fi → “Private Wi-Fi Address” → “Fixed”.",
    savedOverride: "Saved. The automations have been checked again.",
    savedImportant: "Marked as important. If it needs the internet, it is listed under Settings → Repairs.",
    savedUnimportant: "No longer marked as important.",
    none: "None.",
    part_trigger: "Trigger",
    part_condition: "Condition",
    part_action: "Action",
    via: "via",
    voice: "Voice assistant",
    voiceHint: "Each Assist pipeline turns speech into text, acts on it and answers. If one step needs the internet, voice control does not work during an outage.",
    voiceOk: "works without the internet",
    voicePartial: "only partly without the internet",
    voiceFails: "does not work without the internet",
    voiceUnknown: "not sure",
    voicePreferred: "preferred",
    voiceUsedBy: "Used by: {names}",
    stage_wake_word: "Wake word",
    stage_stt: "Speech to text",
    stage_conversation: "Conversation agent",
    stage_tts: "Text to speech",
    voiceAdvice: "A fully local voice assistant needs a lot of computing power, above all for speech recognition (Whisper); on small machines it is often too slow to use. Realistic: commands Home Assistant understands itself work locally with “Prefer handling commands locally”, and announcements with fixed sentences come from the cache. Local alternatives, if your hardware is up to it: Whisper and Piper through the Wyoming integration.",
    integrations: "Integrations",
    integrationsHint: "How each set-up integration connects, as found out by Unclouded. Automations are judged on this basis.",
    reach_cloud: "Cloud",
    reach_partial: "Partly local",
    reach_unknown: "Unknown",
    reach_local: "Local",
    reach_internal: "Inside Home Assistant",
    noAutomations: "There are no automations yet.",
    error: "Error",
    reasons: {
      iot_class_local: "talks to devices in your network",
      template_substitute: "read in a template with a fallback value; without the internet that value is used",
      built_in_agent: "built-in agent of Home Assistant",
      agent_local_first: "cloud agent, but commands Home Assistant understands itself are handled locally",
      iot_class_cloud: "talks to a cloud service",
      iot_class_calculated: "computed inside Home Assistant",
      iot_class_missing: "the integration does not say how it connects",
      sonoff_local: "set up in local mode",
      sonoff_auto: "set up in auto mode: local for devices with LAN control, otherwise cloud",
      sonoff_cloud: "set up in cloud mode",
      xiaomi_miot_local: "set up in local mode",
      xiaomi_miot_auto: "set up in auto mode: local or cloud depending on device and value",
      xiaomi_miot_cloud: "set up in cloud mode",
      mobile_app: "local while the phone is at home, over the internet when it is away",
      mobile_app_presence: "the phone reports its position over the internet while away",
      mobile_app_push_relay: "push notifications go through a relay server on the internet",
      mobile_app_local_push: "arrives over local push while the phone is at home",
      mobile_app_no_push: "the phone has no way to receive push notifications",
      known_cloud: "uses a cloud service, whatever the integration declares",
      notify_unknown: "could not find out which integration sends this",
      entry_missing: "the integration behind it is no longer set up",
      device_missing: "the device no longer exists",
      user_override: "chosen by you",
      person_local_tracker: "a device in your home network tells whether the person is at home",
    },
  },
  de: {
    intro: "Was in deinem Home Assistant weiterläuft, wenn das Internet weg ist.",
    refresh: "Neu prüfen",
    section_loss: "Verlieren Funktion oder fallen aus",
    section_notify: "Verlieren nur Benachrichtigungen",
    section_unknown: "Unklar",
    section_works: "Laufen weiter",
    hint_loss: "Ohne Internet lösen diese nicht aus oder schalten etwas nicht.",
    hint_notify: "Was sie schalten, läuft weiter; nur ihre Nachrichten kommen ohne Internet nicht an.",
    hint_unknown: "Nichts davon braucht bekanntermaßen Internet, aber manche Teile ließen sich nicht prüfen.",
    hint_works: "Diese nutzen nur, was bei dir zu Hause ist.",
    stopsCompletely: "fällt ganz aus",
    open: "Öffnen",
    markImportant: "Als wichtig markieren: Home Assistant meldet dann unter Reparaturen, wenn sie Internet braucht",
    unmarkImportant: "Als wichtig markiert; Klick nimmt die Markierung weg",
    decide: "Bitte festlegen",
    decideHint:
      "Diese Integrationen geben nicht an, wie sie sich verbinden. Wenn du es weißt, wähle es hier; die Automationen werden sofort neu bewertet.",
    notChosen: "Unbekannt – wählen …",
    choice_local: "Lokal",
    choice_cloud: "Cloud",
    choice_partial: "Teilweise lokal",
    yourChoice: "deine Wahl",
    decided: "Von dir festgelegt",
    decidedHint: "Diese Integrationen hast du selbst eingestuft. Hier kannst du es jederzeit ändern.",
    integrationNoEntry: "Entitäten ohne Einrichtung",
    heroLabel: "Wenn das Internet ausfällt",
    heroOf: "von {total}",
    heroText: "Automationen laufen normal weiter",
    legend_works: "laufen weiter",
    legend_notify: "verlieren nur Benachrichtigungen",
    legend_loss: "verlieren Funktion oder fallen aus",
    legend_unknown: "unklar",
    summaryAllGood: "Alles läuft bei dir zu Hause. Ein Internetausfall betrifft deine Automationen nicht.",
    whatTitle: "Worum geht es?",
    whatText1:
      "Viele Geräte und Dienste in Home Assistant arbeiten über Server im Internet: die des Herstellers, von Apple oder Google oder eines Cloud-Dienstes. Ist das Internet weg, hat der Anbieter eine Störung oder schaltet er seinen Dienst ab, funktioniert auch bei dir zu Hause etwas nicht mehr.",
    whatText2:
      "Unclouded prüft jede Automation: was sie auslöst, was sie prüft und was sie tut. Es zeigt, was ohne Internet weiterläuft, was nicht, und was du tun kannst, damit das Wichtige auch ohne Internet funktioniert.",
    whatText3: "Unclouded liest nur. Es ändert nichts an deiner Einrichtung.",
    hide: "Verstanden",
    adviceTitle: "Was du tun kannst",
    adviceHint: "Vorschläge aus deiner Einrichtung, das Nützlichste zuerst.",
    affects: "Betrifft {n} Automationen",
    affects1: "Betrifft 1 Automation",
    showAffected: "Betroffene Automationen zeigen",
    noAdvice: "Nichts zu tun. Gut gemacht.",
    advice_local_push_title: "Lokalen Push einschalten",
    advice_local_push_why:
      "Benachrichtigungen an {entries} laufen über einen Relay-Server im Internet. Ohne Internet kommen sie nicht an, auch nicht, wenn du zu Hause bist.",
    advice_local_push_how:
      "In der Home-Assistant-App: Einstellungen → Companion App → deinen Server antippen → „Interne URL“. Dort die Adresse von Home Assistant im Heimnetz eintragen (zum Beispiel http://192.168.1.10:8123), den Namen deines WLANs hinzufügen und „Lokaler Push“ eingeschaltet lassen. Damit die App das WLAN erkennt, braucht sie die Standortfreigabe. Ist das Handy in diesem WLAN, kommen Nachrichten dann auch ohne Internet an.",
    advice_local_fallback_title: "Wichtigen Meldungen einen zweiten, lokalen Weg geben",
    advice_local_fallback_why:
      "Diese Automationen schicken nur eine Push-Nachricht. Ohne Internet bekommst du nichts davon mit, egal wie wichtig es ist.",
    advice_local_fallback_how:
      "Ergänze bei den wichtigen ein Signal, das zu Hause funktioniert: eine Lampe blinken lassen, eine Durchsage über einen Lautsprecher oder einen Hinweis auf dem Fernseher. Markiere sie mit ★, dann erinnert Home Assistant unter Reparaturen daran, solange sie vom Internet abhängen.",
    advice_presence_title: "Anwesenheit auch lokal erkennen",
    advice_presence_why:
      "Ob jemand zu Hause ist, erfährt Home Assistant bisher nur von den Handys. Unterwegs melden sie ihren Standort über das Internet. Fällt es aus, bleibt der letzte Stand stehen, und Automationen, die auf Kommen oder Gehen reagieren, laufen nicht.",
    advice_presence_how_helpers:
      "Die Integrationen {helpers} sehen schon, welche Geräte in deinem WLAN sind. Such dort das Handy heraus und füge es der Person als weiteres Gerät hinzu (Einstellungen → Personen). Dann weiß Home Assistant auch ohne Internet, ob jemand zu Hause ist.",
    advice_presence_how_helpers1:
      "Die Integration {helpers} sieht schon, welche Geräte in deinem WLAN sind. Such dort das Handy heraus und füge es der Person als weiteres Gerät hinzu (Einstellungen → Personen). Dann weiß Home Assistant auch ohne Internet, ob jemand zu Hause ist.",
    advice_presence_how:
      "Richte eine Integration für deinen Router oder dein WLAN ein, die sieht, welche Geräte verbunden sind, und füge das Handy von dort der Person hinzu (Einstellungen → Personen).",
    advice_substitutes_title: "Werte prüfen, die ohne Internet ersetzt werden",
    advice_substitutes_why:
      "Diese Automationen lesen Werte von {entries} in einer Vorlage mit Ersatzwert, zum Beispiel float(10). Ohne Internet laufen sie weiter, aber mit dem Ersatzwert statt dem echten – oft, ohne dass es jemand merkt.",
    advice_substitutes_how:
      "Nimm einen Sensor bei dir zu Hause, wo es einen gibt (zum Beispiel einen eigenen Außensensor statt eines Wetterdienstes). Sonst prüfe in der Vorlage mit has_value(), ob der Wert da ist, und lege fest, was ohne ihn passieren soll.",
    advice_cloud_devices_title:
      "Geräte und Dienste aus der Cloud",
    advice_cloud_devices_why:
      "Bei {entries} kommt alles von Servern im Internet. Ohne Internet, oder wenn der Anbieter den Dienst einstellt, reagiert nichts.",
    advice_cloud_devices_how:
      "Für jede Integration, ob es einen lokalen Weg gibt:",
    advice_local_tts_title: "Durchsagen lokal erzeugen",
    advice_local_tts_why: "Gesprochene Durchsagen erzeugt ein Cloud-Dienst ({entries}).",
    advice_local_tts_how:
      "Zwei Wege, die auch auf kleiner Hardware gehen: Home Assistant hebt jede einmal erzeugte Durchsage auf (Ordner tts) und spielt sie von dort erneut ab, auch ohne Internet – nimm für wichtige Durchsagen also einen festen Satz ohne wechselnde Werte. Oder nutze eine lokale Sprachausgabe wie Piper nur als Ersatz, solange das Internet weg ist; für kurze Sätze ist sie auch auf kleinen Rechnern schnell genug.",
    // Konkrete Schritte mit Links
    stepsLabel: "Direkt zu:",
    link_integration: "{name} einstellen",
    link_people: "Personen",
    link_wyoming: "Wyoming hinzufügen",
    link_piper: "Add-on Piper",
    link_whisper: "Add-on Whisper",
    link_assistants: "Sprachassistenten",
    pushPending: "Unclouded erkennt es von selbst, sobald das Handy mit lokalem Push in deinem WLAN ist; das kann bis zu 10 Minuten dauern.",
    alt_sonoff: "In den Optionen der Integration den Modus „auto“ oder „local“ wählen.",
    alt_xiaomi_miot: "Für diesen Eintrag den Verbindungsmodus „auto“ oder „local“ wählen.",
    alt_tuya: "Tuya Local oder LocalTuya (HACS) steuern viele Tuya-Geräte direkt im WLAN.",
    alt_switchbot_cloud: "Die Integration SwitchBot Bluetooth steuert viele SwitchBot-Geräte lokal.",
    alt_tado: "tado°-Geräte lassen sich auch lokal einbinden: ältere über HomeKit Device, tado° X über Matter.",
    alt_meross_cloud: "Meross LAN (HACS) steuert Meross-Geräte direkt im Netz.",
    alt_weather: "Wetterdaten kommen naturgemäß aus dem Internet. Eine eigene Wetterstation, zum Beispiel über Ecowitt, läuft weiter.",
    alt_none:
      "Für {name} ist kein lokaler Weg bekannt. Bei Geräten beim Austausch solche mit Matter, Zigbee oder lokaler Schnittstelle bevorzugen.",
    say_notify_lost: "Benachrichtigung an {who} kommt nicht an",
    say_notify_home: "Benachrichtigung an {who} kommt nur zu Hause an",
    say_tts: "Durchsage über {who} entfällt",
    say_trigger: "{what} ({who}) kommt aus der Cloud, die Automation löst nicht aus",
    say_presence: "Anwesenheit kommt unterwegs nur über das Internet",
    say_trigger_partial: "{what} ({who}) kommt unterwegs nur über das Internet, die Automation löst dann womöglich nicht aus",
    say_condition: "Bedingung zu {what} ({who}) lässt sich nicht prüfen",
    say_action: "{what} ({who}) wird nicht geschaltet",
    say_substitute: "ohne Internet wird {what} ({who}) durch einen festen Wert ersetzt, die Automation entscheidet dann danach",
    say_alternative: "ohne Internet lässt sich {what} ({who}) nicht prüfen, die anderen Möglichkeiten der Bedingung greifen aber weiter",
    say_unknown: "unklar, wie sich {what} verbindet",
    say_all_local: "nutzt nur Geräte bei dir zu Hause",
    details: "Technische Details",
    howLabel: "So geht's:",
    matchIntro: "In deiner Einrichtung gefunden:",
    matchKnown: "{integration} kennt dieses Handy als „{tracker}“ ({entity}).",
    matchDisabled:
      "Der Eintrag ist noch deaktiviert: Einstellungen → Geräte & Dienste → Entitäten → „{tracker}“ öffnen → Zahnrad → „Aktiviert“ einschalten.",
    matchAssign: "Dann Einstellungen → Personen → {person} → unter „Zu verfolgende Geräte“ {entity} hinzufügen.",
    matchApple:
      "Damit der Router das iPhone immer wiedererkennt: am iPhone Einstellungen → WLAN → ⓘ neben deinem Heim-WLAN → „Private WLAN-Adresse“ → „Fest“.",
    savedOverride: "Gespeichert. Die Automationen wurden neu bewertet.",
    savedImportant: "Als wichtig markiert. Braucht sie Internet, steht sie unter Einstellungen → Reparaturen.",
    savedUnimportant: "Nicht mehr als wichtig markiert.",
    none: "Keine.",
    part_trigger: "Auslöser",
    part_condition: "Bedingung",
    part_action: "Aktion",
    via: "über",
    voice: "Sprachassistent",
    voiceHint: "Jede Assist-Pipeline wandelt Sprache in Text, führt den Befehl aus und antwortet. Braucht ein Schritt das Internet, geht die Sprachsteuerung bei einem Ausfall nicht.",
    voiceOk: "geht ohne Internet",
    voicePartial: "geht ohne Internet nur teilweise",
    voiceFails: "geht ohne Internet nicht",
    voiceUnknown: "unklar",
    voicePreferred: "bevorzugt",
    voiceUsedBy: "Genutzt von: {names}",
    stage_wake_word: "Aktivierungswort",
    stage_stt: "Sprache zu Text",
    stage_conversation: "Gesprächsagent",
    stage_tts: "Text zu Sprache",
    voiceAdvice: "Ein ganz lokaler Sprachassistent braucht viel Rechenleistung, vor allem die Spracherkennung (Whisper); auf kleinen Rechnern ist sie oft zu langsam zum Benutzen. Realistisch: Befehle, die Home Assistant selbst versteht, laufen mit „Befehle bevorzugt lokal verarbeiten“ lokal, und Durchsagen mit festen Sätzen kommen aus dem Zwischenspeicher. Lokale Alternativen, wenn die Hardware reicht: Whisper und Piper über die Wyoming-Integration.",
    integrations: "Integrationen",
    integrationsHint: "Wie sich jede eingerichtete Integration verbindet, so wie Unclouded es ermittelt hat. Darauf beruht die Bewertung der Automationen.",
    reach_cloud: "Cloud",
    reach_partial: "Teilweise lokal",
    reach_unknown: "Unbekannt",
    reach_local: "Lokal",
    reach_internal: "In Home Assistant",
    noAutomations: "Es gibt noch keine Automationen.",
    error: "Fehler",
    reasons: {
      iot_class_local: "spricht mit Geräten im eigenen Netz",
      template_substitute: "in einer Vorlage mit Ersatzwert gelesen; ohne Internet gilt dieser Wert",
      built_in_agent: "eingebauter Agent von Home Assistant",
      agent_local_first: "Cloud-Agent, aber Befehle, die Home Assistant selbst versteht, laufen lokal",
      iot_class_cloud: "spricht mit einem Cloud-Dienst",
      iot_class_calculated: "wird in Home Assistant berechnet",
      iot_class_missing: "die Integration gibt nicht an, wie sie sich verbindet",
      sonoff_local: "im lokalen Modus eingerichtet",
      sonoff_auto: "im Auto-Modus eingerichtet: lokal für Geräte mit LAN-Steuerung, sonst Cloud",
      sonoff_cloud: "im Cloud-Modus eingerichtet",
      xiaomi_miot_local: "im lokalen Modus eingerichtet",
      xiaomi_miot_auto: "im Auto-Modus eingerichtet: je nach Gerät und Wert lokal oder Cloud",
      xiaomi_miot_cloud: "im Cloud-Modus eingerichtet",
      mobile_app: "lokal, solange das Handy zu Hause ist, unterwegs über das Internet",
      mobile_app_presence: "das Handy meldet seinen Standort unterwegs über das Internet",
      mobile_app_push_relay: "Push-Nachrichten laufen über einen Relay-Server im Internet",
      mobile_app_local_push: "kommt per lokalem Push an, solange das Handy zu Hause ist",
      mobile_app_no_push: "das Handy kann keine Push-Nachrichten empfangen",
      known_cloud: "nutzt einen Cloud-Dienst, egal was die Integration angibt",
      notify_unknown: "unklar, welche Integration das verschickt",
      entry_missing: "die Integration dahinter ist nicht mehr eingerichtet",
      device_missing: "das Gerät gibt es nicht mehr",
      user_override: "von dir festgelegt",
      person_local_tracker: "ein Gerät im Heimnetz zeigt, ob die Person zu Hause ist",
    },
  },
};

// The overview and the lists use the same four groups, by what is lost.
const KINDS = ["loss", "notify", "unknown", "works"];
const kindOf = (a) =>
  a.verdict === "works"
    ? "works"
    : a.verdict === "unknown"
      ? "unknown"
      : a.only_notifications
        ? "notify"
        : "loss";
// Known local ways for integrations that go through a cloud, by domain.
const ALTERNATIVES = {
  sonoff: "alt_sonoff",
  xiaomi_miot: "alt_xiaomi_miot",
  tuya: "alt_tuya",
  switchbot_cloud: "alt_switchbot_cloud",
  tado: "alt_tado",
  meross_cloud: "alt_meross_cloud",
  met: "alt_weather",
  openweathermap: "alt_weather",
  accuweather: "alt_weather",
  pirateweather: "alt_weather",
  dwd_weather: "alt_weather",
  dwd_weather_warnings: "alt_weather",
  meteo_france: "alt_weather",
};

const REACHES = ["cloud", "partial", "unknown", "local", "internal"];
const LOCAL = ["local", "internal"];

const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
  );

class UncloudedPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._automations = null;
    this._entries = [];
    this._overrides = {};
    this._error = null;
    this._open = new Set();
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) {
      this._render();
      this._load();
    }
  }

  set narrow(narrow) {
    const changed = this._narrow !== narrow;
    this._narrow = narrow;
    if (changed && this._hass) this._render();
  }

  get _t() {
    const lang = (this._hass?.language || "en").split("-")[0];
    return STRINGS[lang] || STRINGS.en;
  }

  async _load() {
    try {
      const [automations, entries] = await Promise.all([
        this._hass.callWS({ type: "unclouded/automations" }),
        this._hass.callWS({ type: "unclouded/entries" }),
      ]);
      this._automations = automations.automations;
      this._advice = automations.advice || [];
      this._voice = automations.voice || [];
      this._entries = entries.entries;
      this._overrides = entries.overrides || {};
      this._error = null;
    } catch (err) {
      this._error = err.message || String(err);
    }
    this._render();
  }

  _reason(code) {
    return this._t.reasons[code] || code;
  }

  _entry(entryId) {
    return this._entries.find((e) => e.entry_id === entryId);
  }

  _refLabel(dep) {
    if (dep.kind === "device") {
      const d = this._hass.devices?.[dep.ref];
      return d ? d.name_by_user || d.name || dep.ref : dep.ref;
    }
    if (dep.kind === "entity" || dep.kind === "template") {
      const name = this._hass.states[dep.ref]?.attributes.friendly_name;
      return name ? `${name} (${dep.ref})` : dep.ref;
    }
    return dep.ref;
  }

  // One line per thing that needs the internet; the same thing used twice counts once.
  _problems(automation) {
    const seen = new Set();
    return automation.dependencies.filter((d) => {
      const key = `${d.part}|${d.ref}`;
      if (LOCAL.includes(d.reach) || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  _fmt(text, values) {
    return text.replace(/\{(\w+)\}/g, (_, key) => values[key] ?? "");
  }

  _list(items) {
    try {
      return new Intl.ListFormat(this._hass.language || "en", { type: "conjunction" }).format(items);
    } catch (err) {
      return items.join(", ");
    }
  }

  _titles(entryIds, byIntegration = false) {
    // Entry titles can be cryptic, e.g. a station ID; integrations are named for people.
    const name = (e) => (byIntegration ? e.integration_name || e.title : e.title);
    return this._list([...new Set(entryIds.map((id) => this._entry(id)).filter(Boolean).map(name))]);
  }

  _automationLink(automation) {
    if (!automation.config_id) return esc(automation.name);
    return `<a href="/config/automation/edit/${encodeURIComponent(automation.config_id)}">${esc(automation.name)}</a>`;
  }

  _name(entityId) {
    return this._hass.states[entityId]?.attributes.friendly_name || entityId;
  }

  // One plain sentence per automation instead of the technical list.
  _say(automation) {
    const t = this._t;
    const phrases = this._problems(automation).map((d) => {
      const who = this._entry(d.entry_id)?.title || d.ref;
      const what = ["entity", "template"].includes(d.kind) ? this._name(d.ref) : this._refLabel(d);
      if (d.substitute) return this._fmt(t.say_substitute, { what, who });
      if (d.alternative) return this._fmt(t.say_alternative, { what, who });
      if (d.part === "action" && d.notification && d.ref.startsWith("notify."))
        return this._fmt(d.reach === "partial" ? t.say_notify_home : t.say_notify_lost, { who });
      if (d.part === "action" && d.ref.startsWith("tts.")) return this._fmt(t.say_tts, { who });
      if (d.reason === "mobile_app_presence") return t.say_presence;
      if (d.reach === "unknown") return this._fmt(t.say_unknown, { what });
      if (d.part === "trigger")
        return this._fmt(d.reach === "partial" ? t.say_trigger_partial : t.say_trigger, { what, who });
      if (d.part === "condition") return this._fmt(t.say_condition, { what, who });
      return this._fmt(t.say_action, { what, who });
    });
    const unique = [...new Set(phrases)];
    const text = unique.length ? unique.join("; ") : t.say_all_local;
    return text.charAt(0).toUpperCase() + text.slice(1) + ".";
  }

  // The overview: one big number, a bar split by what happens, and a legend that
  // jumps to the first automation of each kind.
  _renderSummary() {
    const t = this._t;
    const all = this._automations;
    if (all.length && all.every((a) => a.verdict === "works"))
      return `<section class="card hero"><p class="hero-good">${esc(t.summaryAllGood)}</p></section>`;
    const parts = ["works", "notify", "loss", "unknown"]
      .map((kind) => ({
        kind,
        items: all
          .filter((a) => kindOf(a) === kind)
          .sort((a, b) => a.name.localeCompare(b.name)),
      }))
      .filter((p) => p.items.length);
    const works = all.filter((a) => kindOf(a) === "works").length;
    const bar = parts
      .map(
        (p) => `<span class="seg ${p.kind}" style="flex: ${p.items.length}"
          title="${p.items.length} ${esc(t[`legend_${p.kind}`])}"></span>`
      )
      .join("");
    const legend = parts
      .map(
        (p) => `
        <button class="legend" data-jump="${esc(p.items[0].entity_id)}">
          <span class="dot ${p.kind}"></span><strong>${p.items.length}</strong>
          ${esc(t[`legend_${p.kind}`])}
        </button>`
      )
      .join("");
    return `
      <section class="card hero">
        <div class="hero-label">${esc(t.heroLabel)}</div>
        <div class="hero-main">
          <span class="big">${works}</span>
          <span class="of">${esc(this._fmt(t.heroOf, { total: all.length }))}</span>
          <span class="text">${esc(t.heroText)}</span>
        </div>
        <div class="bar">${bar}</div>
        <div class="legends">${legend}</div>
      </section>`;
  }

  _whatSeen() {
    try {
      return localStorage.getItem("unclouded-what-seen") === "1";
    } catch (err) {
      return false;
    }
  }

  _renderWhat() {
    const t = this._t;
    return `
      <details class="card what" id="what"${this._whatSeen() ? "" : " open"}>
        <summary><h2>${esc(t.whatTitle)}</h2></summary>
        <p>${esc(t.whatText1)}</p>
        <p>${esc(t.whatText2)}</p>
        <p class="muted">${esc(t.whatText3)}</p>
        <div class="actions"><button id="what-seen">${esc(t.hide)}</button></div>
      </details>`;
  }

  // Concrete steps per phone instead of the general advice.
  _supervisor() {
    return this._hass.config?.components?.includes("hassio");
  }

  _links(links) {
    if (!links.length) return "";
    return `<p class="links"><strong>${esc(this._t.stepsLabel)}</strong> ${links
      .map(([href, text]) => `<a class="chip" href="${esc(href)}">${esc(text)} ›</a>`)
      .join(" ")}</p>`;
  }

  _voiceLinks() {
    const t = this._t;
    const links = [["/config/integrations/dashboard/add?domain=wyoming", t.link_wyoming]];
    if (this._supervisor())
      links.push(["/hassio/addon/core_piper/info", t.link_piper], ["/hassio/addon/core_whisper/info", t.link_whisper]);
    links.push(["/config/voice-assistants/assistants", t.link_assistants]);
    return links;
  }

  _integrationLink(entry) {
    return [
      `/config/integrations/integration/${encodeURIComponent(entry.domain)}`,
      this._fmt(this._t.link_integration, { name: entry.integration_name || entry.domain }),
    ];
  }

  _renderSteps(advice) {
    const t = this._t;
    const entries = advice.entries.map((id) => this._entry(id)).filter(Boolean);
    if (advice.key === "local_push") return `<p class="muted">${esc(t.pushPending)}</p>`;
    if (advice.key === "presence") {
      // Matches bring their own links.
      if (advice.matches?.length) return "";
      const helpers = advice.helpers.map((id) => this._entry(id)).filter(Boolean);
      return this._links([["/config/person", t.link_people], ...helpers.map((e) => this._integrationLink(e))]);
    }
    if (advice.key === "local_tts") return this._links(this._voiceLinks());
    if (advice.key !== "cloud_devices") return "";
    const byDomain = new Map();
    for (const e of entries) byDomain.set(e.domain, [...(byDomain.get(e.domain) || []), e]);
    const rows = [...byDomain.values()]
      .sort((a, b) => (a[0].integration_name || "").localeCompare(b[0].integration_name || ""))
      .map((group) => {
        const e = group[0];
        const name = e.integration_name || e.domain;
        const alt = ALTERNATIVES[e.domain];
        const text = alt ? t[alt] : this._fmt(t.alt_none, { name });
        const [href] = this._integrationLink(e);
        return `<li><a href="${esc(href)}">${esc(name)}</a>: ${esc(text)}</li>`;
      })
      .join("");
    return `<ul class="steps alternatives">${rows}</ul>`;
  }

  _renderMatches(matches) {
    const t = this._t;
    const steps = matches.map((m) => {
      const values = {
        integration: this._entry(m.entry_id)?.integration_name || "",
        tracker: m.tracker_name,
        entity: m.tracker,
        person: m.person_name,
      };
      return `
        <li>
          <strong>${esc(m.phone_name)}</strong> (${esc(m.person_name)}):
          ${esc(this._fmt(t.matchKnown, values))}
          ${m.disabled ? esc(this._fmt(t.matchDisabled, values)) : ""}
          ${esc(this._fmt(t.matchAssign, values))}
        </li>`;
    });
    const apple = matches.some((m) => /iphone|ipad/i.test(m.phone_name));
    return `
      <div class="how">
        <p><strong>${esc(t.howLabel)}</strong> ${esc(t.matchIntro)}</p>
        <ul class="steps">${steps.join("")}</ul>
        ${apple ? `<p class="muted">${esc(t.matchApple)}</p>` : ""}
        ${this._links([
          ["/config/person", t.link_people],
          ...[...new Set(matches.map((m) => m.entry_id))]
            .map((id) => this._entry(id))
            .filter(Boolean)
            .map((e) => this._integrationLink(e)),
        ])}
      </div>`;
  }

  _renderAdvice() {
    const t = this._t;
    if (!this._advice.length) return "";
    const items = this._advice.map((a, i) => {
      const helpers = [
        ...new Set(a.helpers.map((id) => this._entry(id)?.integration_name).filter(Boolean)),
      ];
      // Phones are told apart by their own names, services by their integration.
      const values = {
        entries: this._titles(a.entries, a.key !== "local_push"),
        helpers: this._list(helpers),
      };
      let how = t[`advice_${a.key}_how`];
      if (a.key === "presence" && helpers.length)
        how = helpers.length === 1 ? t.advice_presence_how_helpers1 : t.advice_presence_how_helpers;
      const names = a.automations
        .map((id) => this._automations.find((x) => x.entity_id === id))
        .filter(Boolean)
        .sort((x, y) => x.name.localeCompare(y.name))
        .map((x) => `<li>${this._automationLink(x)}</li>`)
        .join("");
      return `
        <li class="advice">
          <div class="advice-head"><span class="num">${i + 1}</span><h3>${esc(t[`advice_${a.key}_title`])}</h3></div>
          <p>${esc(this._fmt(t[`advice_${a.key}_why`], values))}</p>
          ${
            a.key === "presence" && a.matches?.length
              ? this._renderMatches(a.matches)
              : `<p class="how"><strong>${esc(t.howLabel)}</strong> ${esc(this._fmt(how, values))}</p>`
          }
          ${this._renderSteps(a)}
          <details class="affected">
            <summary>${esc(
              a.automations.length === 1 ? t.affects1 : this._fmt(t.affects, { n: a.automations.length })
            )}</summary>
            <ul class="names">${names}</ul>
          </details>
        </li>`;
    });
    return `
      <section class="card">
        <h2>${esc(t.adviceTitle)}</h2>
        <p class="muted">${esc(t.adviceHint)}</p>
        <ol class="advices">${items.join("")}</ol>
      </section>`;
  }

  _renderDependency(dep) {
    const t = this._t;
    const entry = dep.entry_id && this._entry(dep.entry_id);
    const via = entry ? ` ${esc(t.via)} ${esc(entry.title)}` : "";
    return `
      <li>
        <span class="part">${esc(t[`part_${dep.part}`])}</span>
        <code>${esc(this._refLabel(dep))}</code>${via}
        <span class="badge spaced ${esc(dep.reach)}">${esc(t[`reach_${dep.reach}`])}</span>
        <div class="muted">${esc(this._reason(dep.reason))}</div>
      </li>`;
  }

  _renderAutomation(automation) {
    const t = this._t;
    const problems = this._problems(automation);
    const link = automation.config_id
      ? `<a class="open" href="/config/automation/edit/${encodeURIComponent(automation.config_id)}">${esc(t.open)} ›</a>`
      : "";
    const flag =
      automation.verdict === "fails" && !automation.only_notifications
        ? `<span class="badge cloud">${esc(t.stopsCompletely)}</span>`
        : "";
    const star = `<button class="star${automation.important ? " on" : ""}" data-important="${esc(automation.entity_id)}"
      title="${esc(automation.important ? t.unmarkImportant : t.markImportant)}">${automation.important ? "★" : "☆"}</button>`;
    const row = `${star}<span class="name">${esc(automation.name)}</span>${flag}${link}`;
    const say = `<div class="say">${esc(this._say(automation))}</div>`;
    const id = esc(automation.entity_id);
    if (!problems.length)
      return `<li class="automation" data-entity="${id}"><div class="row">${row}</div>${say}</li>`;
    const open = this._open.has(automation.entity_id) ? " open" : "";
    return `
      <li class="automation" data-entity="${id}">
        <div class="row">${row}</div>
        ${say}
        <details class="tech" data-id="${esc(automation.entity_id)}"${open}>
          <summary>${esc(t.details)}</summary>
          <ul class="deps">${problems.map((d) => this._renderDependency(d)).join("")}</ul>
        </details>
      </li>`;
  }

  _renderVerdicts() {
    const t = this._t;
    if (!this._automations.length) return `<p class="muted">${esc(t.noAutomations)}</p>`;
    const groups = Object.fromEntries(KINDS.map((k) => [k, []]));
    for (const a of this._automations) groups[kindOf(a)].push(a);
    const byName = (a, b) => a.name.localeCompare(b.name);
    const sections = KINDS.filter((k) => groups[k].length)
      .map(
        (v) => `
        <section class="card" id="${v}">
          <h2><span class="dot ${v}"></span>${esc(t[`section_${v}`])} · ${groups[v].length}</h2>
          <p class="muted">${esc(t[`hint_${v}`])}</p>
          <ul class="automations">
            ${groups[v].sort(byName).map((a) => this._renderAutomation(a)).join("")}
          </ul>
        </section>`
      )
      .join("");
    return sections;
  }

  // Only offered where Unclouded could not find out anything by itself.
  _renderChoice(key, chosen) {
    const t = this._t;
    const options = [
      `<option value="">${esc(t.notChosen)}</option>`,
      ...["local", "cloud", "partial"].map(
        (r) => `<option value="${r}"${chosen === r ? " selected" : ""}>${esc(t[`choice_${r}`])}</option>`
      ),
    ];
    return `<select class="choice${chosen ? " chosen" : ""}" data-override="${esc(key)}">${options.join("")}</select>`;
  }

  // Integrations nobody could classify: entries without iot_class and integrations
  // whose entities have no config entry. Ones already chosen stay listed to change them.
  _renderDecide() {
    const t = this._t;
    const rows = this._entries
      .filter((e) => e.automatic === "unknown")
      .map((e) => ({
        key: `entry:${e.entry_id}`,
        label: e.title,
        sub: e.domain,
        chosen: e.overridden ? e.reach : "",
      }));
    const domains = new Set();
    for (const a of this._automations)
      for (const d of a.dependencies)
        if (d.integration && (d.reach === "unknown" || this._overrides[`domain:${d.integration}`]))
          domains.add(d.integration);
    for (const domain of [...domains].sort())
      rows.push({
        key: `domain:${domain}`,
        label: domain,
        sub: t.integrationNoEntry,
        chosen: this._overrides[`domain:${domain}`] || "",
      });
    if (!rows.length) return "";
    const open = rows.filter((r) => !r.chosen).length;
    const title = open ? `${t.decide} · ${open}` : t.decided;
    return `
      <section class="card${open ? " decide" : ""}">
        <h2>${esc(title)}</h2>
        <p class="muted">${esc(open ? t.decideHint : t.decidedHint)}</p>
        <table>${rows
          .map(
            (r) => `
          <tr>
            <td>${esc(r.label)}<div class="muted">${esc(r.sub)}</div></td>
            <td>${this._renderChoice(r.key, r.chosen)}${
              r.chosen ? `<div class="mine">✓ ${esc(t.yourChoice)}</div>` : ""
            }</td>
          </tr>`
          )
          .join("")}</table>
      </section>`;
  }

  async _setOverride(key, reach) {
    await this._send(
      { type: "unclouded/set_override", key, reach: reach || null },
      this._t.savedOverride
    );
  }

  async _setImportant(entityId, important) {
    await this._send(
      { type: "unclouded/set_important", entity_id: entityId, important },
      important ? this._t.savedImportant : this._t.savedUnimportant
    );
  }

  async _send(message, confirmation) {
    try {
      await this._hass.callWS(message);
    } catch (err) {
      this._error = err.message || String(err);
      this._render();
      return;
    }
    await this._load();
    // Home Assistant shows this as a toast at the bottom of the screen.
    this.dispatchEvent(
      new CustomEvent("hass-notification", {
        detail: { message: confirmation },
        bubbles: true,
        composed: true,
      })
    );
  }

  _engineLabel(stage) {
    const entry = stage.entry_id && this._entry(stage.entry_id);
    const state = stage.engine.includes(".") && this._hass.states?.[stage.engine];
    return state?.attributes?.friendly_name || entry?.title || stage.engine;
  }

  _renderVoice() {
    const t = this._t;
    if (!this._voice?.length) return "";
    const verdict = (reach) =>
      LOCAL.includes(reach)
        ? ["works", t.voiceOk]
        : reach === "partial"
          ? ["partial", t.voicePartial]
          : reach === "cloud"
            ? ["cloud", t.voiceFails]
            : ["unknown", t.voiceUnknown];
    const anyCloud = this._voice.some((p) => !LOCAL.includes(p.reach));
    const pipelines = this._voice
      .map((p) => {
        const [cls, text] = verdict(p.reach);
        const stages = p.stages
          .map(
            (s) => `
            <tr>
              <td>${esc(t[`stage_${s.kind}`])}</td>
              <td>${esc(this._engineLabel(s))}</td>
              <td><span class="badge ${esc(s.reach)}">${esc(t[`reach_${s.reach}`])}</span></td>
              <td class="muted">${esc(this._reason(s.reason))}</td>
            </tr>`
          )
          .join("");
        return `
          <div class="pipeline">
            <h3>${esc(p.name)}${p.preferred ? ` <span class="muted">· ${esc(t.voicePreferred)}</span>` : ""}
              <span class="badge ${esc(cls === "works" ? "local" : cls)}">${esc(text)}</span></h3>
            ${p.satellites.length ? `<p class="muted">${esc(this._fmt(t.voiceUsedBy, { names: p.satellites.join(", ") }))}</p>` : ""}
            <table>${stages}</table>
          </div>`;
      })
      .join("");
    return `
      <details class="card" id="voice" ${anyCloud ? "open" : ""}>
        <summary><h2>${esc(t.voice)} · ${this._voice.length}</h2></summary>
        <p class="muted">${esc(t.voiceHint)}</p>
        ${pipelines}
        ${anyCloud ? `<p>${esc(t.voiceAdvice)}</p>${this._links(this._voiceLinks())}` : ""}
      </details>`;
  }

  _renderEntries() {
    const t = this._t;
    const rows = [...this._entries]
      .sort(
        (a, b) =>
          REACHES.indexOf(a.reach) - REACHES.indexOf(b.reach) || a.title.localeCompare(b.title)
      )
      .map(
        (e) => `
        <tr>
          <td>${esc(e.title)}<div class="muted">${esc(e.domain)}</div></td>
          <td><span class="badge ${esc(e.reach)}">${esc(t[`reach_${e.reach}`])}</span>${
            e.overridden ? `<div class="mine">✓ ${esc(t.yourChoice)}</div>` : ""
          }</td>
          <td class="muted">${esc(this._reason(e.reason))}</td>
        </tr>`
      )
      .join("");
    return `
      <details class="card" id="entries">
        <summary><h2>${esc(t.integrations)} · ${this._entries.length}</h2></summary>
        <p class="muted">${esc(t.integrationsHint)}</p>
        <table>${rows}</table>
      </details>`;
  }

  _render() {
    const t = this._t;
    let body = "";
    if (this._error) body = `<p class="error">${esc(t.error)}: ${esc(this._error)}</p>`;
    else if (this._automations)
      body =
        this._renderSummary() +
        this._renderWhat() +
        this._renderDecide() +
        this._renderAdvice() +
        this._renderVerdicts() +
        this._renderVoice() +
        this._renderEntries();
    else body = `<p class="muted">…</p>`;
    this.shadowRoot.innerHTML = `
      <style>${STYLE}</style>
      <header>
        ${this._narrow ? `<button id="menu" class="icon" title="Menu">☰</button>` : ""}
        <h1>Unclouded</h1>
        <button id="refresh" class="icon small" title="${esc(t.refresh)}">⟳</button>
      </header>
      <main>
        <p class="intro">${esc(t.intro)}</p>
        ${body}
      </main>`;
    this._bind();
  }

  _bind() {
    const $ = (sel) => this.shadowRoot.querySelector(sel);
    $("#menu")?.addEventListener("click", () =>
      this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }))
    );
    $("#refresh")?.addEventListener("click", () => {
      this._automations = null;
      this._render();
      this._load();
    });
    // In-page links would change the panel's URL; scroll instead.
    // Jump to the first automation of a kind; in-page links would change the URL.
    this.shadowRoot.querySelectorAll("button[data-jump]").forEach((el) =>
      el.addEventListener("click", () => {
        const row = this.shadowRoot
          .querySelector(`[data-entity="${el.dataset.jump}"]`);
        row?.scrollIntoView({ behavior: "smooth", block: "center" });
        row?.classList.add("flash");
        setTimeout(() => row?.classList.remove("flash"), 1600);
      })
    );
    $("#what-seen")?.addEventListener("click", () => {
      try {
        localStorage.setItem("unclouded-what-seen", "1");
      } catch (err) {
        // Without storage the explanation simply opens again next time.
      }
      $("#what").open = false;
    });
    this.shadowRoot.querySelectorAll("button[data-important]").forEach((el) =>
      el.addEventListener("click", (e) => {
        // The star sits in the summary; keep it from opening the details.
        e.preventDefault();
        e.stopPropagation();
        this._setImportant(el.dataset.important, !el.classList.contains("on"));
      })
    );
    this.shadowRoot.querySelectorAll("select[data-override]").forEach((el) =>
      el.addEventListener("change", () => this._setOverride(el.dataset.override, el.value))
    );
    this.shadowRoot.querySelectorAll("details[data-id]").forEach((el) =>
      el.addEventListener("toggle", () => {
        if (el.open) this._open.add(el.dataset.id);
        else this._open.delete(el.dataset.id);
      })
    );
  }
}

const STYLE = `
  :host { display: block; min-height: 100%; background: var(--primary-background-color);
    color: var(--primary-text-color); font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
    --uc-fails: var(--error-color, #db4437); --uc-degraded: var(--warning-color, #ff9800);
    --uc-unknown: var(--secondary-text-color, #888); --uc-works: var(--success-color, #43a047); }
  header { display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 12px;
    background: var(--app-header-background-color, var(--primary-color));
    color: var(--app-header-text-color, #fff); }
  header h1 { font-size: 20px; font-weight: 400; margin: 0; flex: 1; }
  main { max-width: 860px; margin: 0 auto; padding: 16px; }
  .intro { margin: 0 0 16px; color: var(--secondary-text-color); }
  .card { display: block; background: var(--card-background-color, #fff); border-radius: var(--ha-card-border-radius, 12px);
    border: 1px solid var(--divider-color); padding: 16px; margin-bottom: 16px; }
  h2 { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 500; margin: 0 0 4px; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
  .dot.unknown { background: var(--uc-unknown); }
  .dot.works { background: var(--uc-works); }
  .dot.notify { background: var(--uc-degraded); }
  .dot.loss { background: var(--uc-fails); }
  .card.hero { padding: 20px; }
  .hero-label { font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--secondary-text-color); }
  .hero-main { display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 10px; margin: 4px 0 14px; }
  .hero-main .big { font-size: 48px; font-weight: 500; line-height: 1; color: var(--uc-works); }
  .hero-main .of { font-size: 22px; color: var(--secondary-text-color); }
  .hero-main .text { font-size: 20px; }
  .hero-good { font-size: 18px; margin: 0; }
  .bar { display: flex; gap: 3px; height: 14px; border-radius: 7px; overflow: hidden; }
  .seg.works { background: var(--uc-works); }
  .seg.notify { background: var(--uc-degraded); }
  .seg.loss { background: var(--uc-fails); }
  .seg.unknown { background: var(--uc-unknown); }
  .legends { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 12px; }
  button.legend { font: inherit; font-size: 14px; display: inline-flex; align-items: center; gap: 6px;
    border: 0; padding: 2px 0; background: transparent; color: var(--primary-text-color); cursor: pointer; }
  button.legend:hover { text-decoration: underline; }
  li.automation.flash { animation: flash 1.6s ease-out; }
  @keyframes flash { from { background: var(--secondary-background-color); } to { background: transparent; } }
  ul { list-style: none; padding: 0; margin: 8px 0 0; }
  li.automation { padding: 8px 0; border-top: 1px solid var(--divider-color); }
  .row { display: flex; align-items: baseline; gap: 6px 8px; flex-wrap: wrap; }
  .row .name { flex: 1 1 200px; }
  div.row { padding-left: 0; }
  a.open { font-size: 13px; white-space: nowrap; margin-left: auto; }
  summary { cursor: pointer; list-style: none; }
  summary::-webkit-details-marker { display: none; }
  details.tech > summary::before { content: "▸ "; }
  details.tech[open] > summary::before { content: "▾ "; }
  button.star { font: inherit; font-size: 18px; line-height: 1; border: 0; background: transparent;
    padding: 0 2px; cursor: pointer; color: var(--secondary-text-color); align-self: center; }
  button.star.on { color: var(--warning-color, #ff9800); }
  select.choice { font: inherit; font-size: 13px; padding: 4px 6px; color: inherit; max-width: 100%;
    background: var(--secondary-background-color); border: 1px solid var(--divider-color); border-radius: 6px; }
  select.choice.chosen { border-color: var(--primary-color); }
  .mine { font-size: 12px; color: var(--primary-color); margin-top: 2px; }
  .card.decide { border-color: var(--warning-color, #ff9800); }
  .summary { font-size: 17px; line-height: 1.5; margin: 0; }
  .what p { line-height: 1.5; margin: 8px 0; }
  .what > summary h2::before, .card > summary h2::before { content: "▸"; color: var(--secondary-text-color); }
  .what[open] > summary h2::before { content: "▾"; }
  .actions { display: flex; justify-content: flex-end; }
  .actions button { font: inherit; padding: 6px 14px; border-radius: 6px; cursor: pointer;
    border: 1px solid var(--divider-color); background: transparent; color: var(--primary-color); }
  ol.advices { list-style: none; padding: 0; margin: 8px 0 0; counter-reset: none; }
  li.advice { padding: 12px 0; border-top: 1px solid var(--divider-color); }
  li.advice p { margin: 6px 0 6px 34px; line-height: 1.5; }
  .advice-head { display: flex; align-items: center; gap: 10px; }
  .advice-head h3 { font-size: 16px; font-weight: 500; margin: 0; }
  .num { flex: none; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center;
    justify-content: center; font-size: 13px; font-weight: 500; color: var(--text-primary-color, #fff);
    background: var(--primary-color); }
  .how { color: var(--primary-text-color); }
  ul.steps { margin: 4px 0 6px 34px; padding-left: 18px; list-style: disc; line-height: 1.5; }
  ul.steps li { padding: 3px 0; }
  div.how p.muted { font-size: 13px; }
  details.affected { margin-left: 34px; font-size: 14px; }
  details.affected summary { color: var(--primary-color); }
  ul.names { list-style: disc; padding-left: 20px; margin: 4px 0 0; }
  ul.names li { padding: 1px 0; }
  .say { margin: 2px 0 0 26px; font-size: 14px; color: var(--secondary-text-color); line-height: 1.4; }
  details.tech { margin: 4px 0 0 26px; font-size: 13px; }
  details.tech > summary { color: var(--secondary-text-color); }
  details.tech ul.deps { margin-left: 0; }
  #entries > summary h2::before { content: "▸"; color: var(--secondary-text-color); }
  #entries[open] > summary h2::before { content: "▾"; }
  ul.deps { margin: 6px 0 0 18px; font-size: 14px; }
  ul.deps li { padding: 4px 0; }
  .part { display: inline-block; min-width: 76px; color: var(--secondary-text-color); }
  .badge { display: inline-block; font-size: 12px; padding: 1px 8px; border-radius: 10px;
    border: 1px solid var(--divider-color); color: var(--secondary-text-color); white-space: nowrap; }
  .badge.spaced { margin-left: 4px; }
  .pipeline { margin: 12px 0; }
  .links { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 14px; }
  a.chip { border: 1px solid var(--divider-color); border-radius: 14px; padding: 2px 10px; text-decoration: none; }
  ul.alternatives li { margin: 4px 0; }
  .pipeline h3 { font-size: 15px; margin: 0 0 4px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .badge.cloud { color: var(--uc-fails); border-color: var(--uc-fails); }
  .badge.partial { color: var(--uc-degraded); border-color: var(--uc-degraded); }
  .badge.local, .badge.internal { color: var(--uc-works); border-color: var(--uc-works); }
  .badge.note { color: var(--primary-color); border-color: var(--primary-color); }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  td { padding: 6px 4px; border-top: 1px solid var(--divider-color); vertical-align: top; }
  td:nth-child(2) { white-space: nowrap; }
  .muted { color: var(--secondary-text-color); font-size: 13px; }
  p.muted { margin: 0 0 4px; }
  a { color: var(--primary-color); text-decoration: none; }
  a:hover { text-decoration: underline; }
  code { font-size: 13px; word-break: break-word; }
  button.icon { font: inherit; border: 0; background: transparent; color: inherit; font-size: 20px;
    padding: 4px 8px; cursor: pointer; }
  .error { color: var(--uc-fails); }
  @media (max-width: 600px) {
    main { padding: 8px; }
      .part { min-width: 0; margin-right: 4px; }
  }
`;

// After an update the browser may load the new module next to the old one.
if (!customElements.get("unclouded-panel")) customElements.define("unclouded-panel", UncloudedPanel);
