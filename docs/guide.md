# Unclouded guide

**English** · [Deutsch](anleitung.md)

This guide explains the panel step by step and how Unclouded comes to its results. For a
short overview and the installation see the [README](../README.md).

- [The panel](#the-panel)
- [What the groups mean](#what-the-groups-mean)
- [How Unclouded classifies integrations](#how-unclouded-classifies-integrations)
- [How automations are followed](#how-automations-are-followed)
- [Important automations and repairs](#important-automations-and-repairs)
- [The suggestions](#the-suggestions)
- [Questions](#questions)

## The panel

Open **Unclouded** in the sidebar. Only admins see it. From top to bottom:

1. **Overview:** how many automations keep working without the internet, as a big number
   and a bar split into keep working, only lose their notifications, lose function or stop,
   and not sure. A click on an entry of the legend jumps to the first automation of that
   kind.
2. **What is this about?** A short explanation, open on the first visit. **Got it** closes it
   for good in this browser.
3. **Please decide** (only if needed): integrations that do not say how they connect. If you
   know it, choose local, cloud or partly local. Once everything is decided, the card is
   called **Decided by you** and stays, so that you can change it again.
4. **What you can do:** suggestions worked out from your setup, the most useful first. Each
   says why it matters and how to do it; **Concerns … automations** lists the automations it
   would help.
5. **Lists of automations**, grouped by what happens to them without the internet.
   Each automation has one sentence that says why, **Open ›** goes to the automation editor
   and **Technical details** lists every trigger, condition and action that needs the
   internet, with the integration behind it and the reason.
6. **Voice assistant:** every Assist pipeline with its wake word, speech-to-text,
   conversation agent and text-to-speech, whether each works without the internet, and the
   voice satellites using it.
7. **Real outages:** what really became unavailable during the last outages, compared with
   Unclouded's assessment (see below).
8. **Integrations:** every set-up integration with how Unclouded classified it and why.

Every change you make in the panel is confirmed at the bottom of the screen.

## What the groups mean

The overview and the lists below it use the same four groups and colours:

| Group | Meaning |
|---|---|
| **Lose function or stop** (red) | Without the internet the automation is not triggered, a condition cannot be checked or something is not switched. **stops completely** marks those that then do nothing at all. |
| **Only lose their notifications** (orange) | What the automation switches keeps working; only its notifications do not arrive. Automations that do nothing but notify are counted here too. |
| **Not sure** (grey) | Nothing is known to need the internet, but some part could not be classified. |
| **Keep working** (green) | Everything it uses is in your home or inside Home Assistant. |

## How Unclouded classifies integrations

Every integration declares how it connects (its `iot_class`): local, cloud, or computed
inside Home Assistant. Unclouded starts from that and corrects it where it is not enough:

- **Depends on the set-up:** some integrations run locally or through the cloud depending on
  how they were set up. Unclouded reads the mode from the integration's settings.
- **Phones (Companion App):** local while the phone is at home, over the internet while it
  is away – shown as partly local.
- **Push notifications:** they look local but go through a relay server on the internet,
  unless local push is turned on in the app.
- **Hardware adapters** such as Zigbee or Thread sticks count as local, **helpers** such as
  groups, templates or derivatives as dependent as the entities they are computed from.
- **Unknown:** an integration that declares nothing is shown as unknown. You can classify it
  under **Please decide**. Unclouded only lets you fill such gaps: what it found out by itself
  cannot be overruled, and a choice stops counting once the integration declares itself.

Is an integration classified wrongly? Please open an issue, so that a rule fixes it for
everyone.

## How automations are followed

Unclouded walks through each automation's triggers, conditions and actions and follows:

- **entities, devices and areas** to the integration behind them,
- **scripts** an automation calls, into their own actions,
- **scenes**, both stored ones and those set with `scene.apply` or `scene.create`,
- **helpers** (groups, templates, derivatives, utility meters …) to their sources,
- **zones and persons** to the trackers behind them. A person with at least one tracker in
  the home network, for example from the router, counts as local,
- **notifications** to the integration and the way they are delivered.

Templates are searched for the entities they read (`states()`, `state_attr()`,
`is_state()`, `states.sensor.x` …). If a template reads a cloud value with a fallback, such as
`float(10)` or `default(0)`, the automation keeps running without the internet but decides on
the fallback; Unclouded reports this separately. Entity IDs that a template builds only at
run time cannot be followed and are left out.

In an **or** condition, a cloud value does not stop the automation as long as another branch
of the condition works locally.

## Important automations and repairs

Mark an automation with **★** if it matters, for example an alarm. While it needs the
internet, Home Assistant lists it under **Settings → Repairs**, saying whether it stops
working, works only partly or only loses its notifications. Remove the star, or make the
automation work locally, and the issue disappears.

Unclouded also remembers how each integration connected. If one needs more of the internet
after an update than before, for example local before and cloud now, a repair issue names
it. Confirm it with **OK**; it is only reported again if it changes once more. New
integrations and improvements are not reported.

Unclouded checks this after Home Assistant has started, when automations are reloaded,
every hour and after every change in the panel.

## The suggestions

| Suggestion | When it appears |
|---|---|
| **Turn on local push** | Notifications to a phone go through the relay server. |
| **Give important alerts a second, local way** | An automation only sends push notifications. |
| **Detect presence locally as well** | Coming home or leaving only comes from phones. If a router integration already sees the phone, its entry is named, also when it is still disabled. |
| **Check values that are replaced without the internet** | A template reads a cloud value with a fallback. |
| **Devices and services in the cloud** | An automation relies on a cloud integration. Each one is listed with a known local way, if there is one. |
| **Make announcements locally** | Spoken announcements are created by a cloud service. Fixed sentences are played from Home Assistant's cache, also without the internet. |

Every suggestion links to the page where you can act on it, and the automations it concerns
link to their editor. Unclouded itself changes nothing.

## Real outages

The sensor **Internet** (`binary_sensor.unclouded_internet`) shows whether Home Assistant
reaches the internet. Once a minute Unclouded opens a connection to the public DNS servers
1.1.1.1 and 9.9.9.9 on port 53 and closes it again; nothing is sent. Only when neither answers
twice in a row does the internet count as down. Outages under two minutes are not kept.

After an outage, the panel shows what really became unavailable in that time, from the start
of the outage until five minutes after its end:

- **failed as expected:** cloud integrations whose entities went away,
- **classified as local, but failed:** a hint that something else was involved, for example
  a cloud login or a bridge,
- **classified as cloud, but kept working:** only after outages of 30 minutes or more;
  it may work locally after all, or show stored values.

What was unavailable around a restart of Home Assistant is left out.

## Questions

**Does Unclouded cut the internet to test this?** No. It works from how integrations connect
and never changes anything. The result is an estimate; after a real outage the panel shows
how well it matched.

**An alarm that only sends a notification is listed under "Only lose their notifications",
although it then does nothing. Why?** Because the notification is all it loses. For an alarm
that is exactly the important part: mark it with ★ and give it a second, local way, as the
suggestions describe.

**An integration runs locally, but Unclouded says cloud.** Please open an issue with the
integration and how it is set up.

**What does Unclouded store?** Your choices for unknown integrations and the important
automations in its config entry, together with the phones seen with local push; the last
known state of each integration in `.storage/unclouded.baseline`; the last ten outages in
`.storage/unclouded.outages`. Removing Unclouded removes all of it and its repair issues.
