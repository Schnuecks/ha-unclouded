<p align="center"><img src="docs/logo.svg" width="96" alt="Unclouded"></p>

# Unclouded

**English** · [Deutsch](README.de.md)

<p align="center">
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.10%2B-41BDF5?logo=homeassistant&logoColor=white" alt="Home Assistant 2026.10+">
  <img src="https://img.shields.io/badge/HACS-custom-41BDF5" alt="HACS custom repository">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-4C9A2A" alt="License MIT"></a>
  <img src="https://img.shields.io/badge/maintained-yes-4C9A2A" alt="Maintained">
</p>

Find out what in your Home Assistant still works when the internet is down – and what you
can do so that the important things keep working.

**New here?** The [guide](docs/guide.md) explains the panel step by step and how Unclouded
comes to its results.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/overview-dark.png"><img src="docs/screenshots/overview.png" width="720" alt="Overview and suggestions"></picture></p>

## Why

Many devices and services in Home Assistant work through servers on the internet: those of
the manufacturer, of Apple or Google, or of a cloud service. If the internet is down, the
provider has an outage or switches its service off, something at home stops working too –
often something you would not expect. A water leak alarm that only sends a push
notification is silent without internet. "Everyone left" never fires when the phones cannot
report their location. A sensor behind a manufacturer's cloud simply stops.

Home Assistant shows for each integration whether it needs the internet, but not what that
means for your automations. Unclouded works that out for your setup and tells you, in plain
words, what you can change.

## Features

- **One sentence per automation:** whether it keeps working, only loses its notifications
  or loses function, and why – for example "Notification to Alex's phone does not arrive".
- **Suggestions from your setup:** turn on local push, give important alerts a second, local
  way, detect presence through your router as well (it names the exact entry for each
  phone), devices behind a manufacturer's cloud, local text-to-speech.
- **Looks deeper than the integration list:** follows scripts, scenes, groups, template
  sensors and other helpers to their sources, persons and zones to the phones behind them,
  and notifications to the way they are delivered.
- **Knows where the declaration is not enough:** integrations that run locally or through
  the cloud depending on how they were set up, phones that are local at home and remote
  when away, push notifications that look local but go through a relay.
- **Important automations:** mark them with a star, and Home Assistant lists them under
  Repairs while they depend on the internet.
- **Notices changes:** if an integration needs the internet after an update when it did not
  before, a repair issue tells you.
- **Fills gaps with you:** an integration that does not say how it connects can be classified
  by you. What Unclouded found out by itself cannot be overruled.
- **Only reads:** Unclouded changes nothing in your setup and does not talk to anything
  outside Home Assistant.

## How it works

1. Open **Unclouded** in the sidebar. The overview at the top shows how many automations
   keep working without the internet and what happens to the others.
2. **What you can do** lists suggestions, the most useful first, each with why it matters
   and how to do it.
3. Below, every automation is listed by what happens to it, with one sentence that says
   why. **Technical details** shows each trigger, condition and action that needs the
   internet and the integration behind it.

   <picture><source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/automations-dark.png"><img src="docs/screenshots/automations.png" width="640" alt="Automations that work only partly"></picture>

4. Mark the automations that matter with ★. Home Assistant then reminds you under
   **Settings → Repairs** while they depend on the internet.

## Installation

Unclouded needs Home Assistant 2026.10 or newer.

**HACS:** in HACS open the menu → **Custom repositories**, add
`https://github.com/Schnuecks/ha-unclouded` with the type **Integration**, then install
**Unclouded** and restart Home Assistant.

**Manually:** copy `custom_components/unclouded` into the `custom_components` folder of
your Home Assistant configuration and restart.

Then add the integration under **Settings → Devices & services → Add integration →
Unclouded**. The panel appears in the sidebar for admins.

## Good to know

- **It is an estimate, not a test:** Unclouded works from how integrations connect, not by
  cutting the internet. An integration that declares nothing is shown as unknown until you
  classify it.
- **Templates in actions:** entity IDs built by a template at run time cannot be followed and
  are left out.
- **Notifications:** with local push turned on in the Companion App, notifications arrive at
  home without the internet. Unclouded sees that from the phone's registration.
- **Wrong classification?** Please open an issue with the integration and how it is set up,
  so it can be fixed for everyone; see [CONTRIBUTING](CONTRIBUTING.md).

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
ruff check . && ruff format --check . && pytest
```

See [CONTRIBUTING](CONTRIBUTING.md).

## How it's built

Unclouded is developed with the help of an AI coding assistant. I define the features and
behaviour, review the changes and test them in my own Home Assistant. Nothing is released
without passing the automated checks: the test suite, Home Assistant's hassfest and the
HACS validation.

## Support

Unclouded is free and stays free. If it helps you, you can buy me a coffee on Ko-fi; it
keeps the project going. Thank you!

<p>
  <a href="https://ko-fi.com/schnuecks"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Support me on Ko-fi"></a>
</p>

## Feedback

Bug reports and ideas are welcome as
[GitHub issues](https://github.com/Schnuecks/ha-unclouded/issues). See also
[CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md).

What changed in each version is listed in the [CHANGELOG](CHANGELOG.md).

**What to expect:** Unclouded is a hobby project that I use in my own Home Assistant. I look
at issues and pull requests as time allows, without a guaranteed response time.

## License

Copyright (c) 2026 Schnuecks. Released under the [MIT License](LICENSE).
