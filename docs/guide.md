# Unclouded guide

**English** · [Deutsch](anleitung.md)

This guide explains the panel step by step and how Unclouded comes to its results. For a
short overview and the installation see the [README](../README.md).

- [The panel](#the-panel)
- [What the verdicts mean](#what-the-verdicts-mean)
- [How Unclouded classifies integrations](#how-unclouded-classifies-integrations)
- [How automations are followed](#how-automations-are-followed)
- [Important automations and repairs](#important-automations-and-repairs)
- [The suggestions](#the-suggestions)
- [Questions](#questions)

## The panel

Open **Unclouded** in the sidebar. Only admins see it. From top to bottom:

1. **Summary:** one sentence on how many automations keep working without the internet,
   how many only lose their notifications and how many lose real function.
2. **What is this about?** A short explanation, open on the first visit. **Got it** closes it
   for good in this browser.
3. **Please decide** (only if needed): integrations that do not say how they connect. If you
   know it, choose local, cloud or partly local. Once everything is decided, the card is
   called **Decided by you** and stays, so that you can change it again.
4. **What you can do:** suggestions worked out from your setup, the most useful first. Each
   says why it matters and how to do it; **Concerns … automations** lists the automations it
   would help.
5. **Tiles and lists of automations**, grouped by what happens to them without the internet.
   Each automation has one sentence that says why, **Open ›** goes to the automation editor
   and **Technical details** lists every trigger, condition and action that needs the
   internet, with the integration behind it and the reason.
6. **Integrations:** every set-up integration with how Unclouded classified it and why.

Every change you make in the panel is confirmed at the bottom of the screen.

## What the verdicts mean

| Verdict | Meaning |
|---|---|
| **Keeps working** | Everything it uses is in your home or inside Home Assistant. |
| **Works partly** | It runs, but some of its parts do not get through, for example a notification, or one of several triggers. |
| **Stops working** | Without the internet it does nothing: its only trigger, a condition or all its actions need the internet. |
| **Not sure** | Nothing is known to need the internet, but some part could not be classified. |

**only notifications** marks automations where nothing but notifications is lost.

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

Entity IDs that a template builds only at run time cannot be followed and are left out.

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
| **Devices behind a manufacturer's cloud** | An automation relies on a cloud integration. |
| **Make announcements locally** | Spoken announcements are created by a cloud service. |

## Questions

**Does Unclouded cut the internet to test this?** No. It works from how integrations connect
and never changes anything. The result is a careful estimate, not a measurement.

**Why does an automation count as "works partly" although its notification is the only thing
that matters to me?** Unclouded cannot know which part matters most. Mark it with ★ and the
repair issue says that only the notification is lost.

**An integration runs locally, but Unclouded says cloud.** Please open an issue with the
integration and how it is set up.

**What does Unclouded store?** Your choices for unknown integrations and the important
automations in its config entry, and the last known state of each integration in
`.storage/unclouded.baseline`. Removing Unclouded removes both and its repair issues.
