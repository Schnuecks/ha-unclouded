<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg"><img src="docs/logo.svg" width="96" alt="Unclouded"></picture></p>

# Unclouded

**English** · [Deutsch](README.de.md)

<p align="center">
  <img src="https://img.shields.io/badge/Home%20Assistant-2026.10%2B-41BDF5?logo=homeassistant&logoColor=white" alt="Home Assistant 2026.10+">
  <img src="https://img.shields.io/badge/HACS-default-41BDF5" alt="Available in HACS">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-4C9A2A" alt="License MIT"></a>
  <img src="https://img.shields.io/badge/maintained-yes-4C9A2A" alt="Maintained">
</p>

Unclouded shows what in your Home Assistant still works when the internet is gone, and
what you can do about the rest.

<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/overview-dark.png"><img src="docs/screenshots/overview.png" width="720" alt="Overview and suggestions"></picture></p>

## Why I built it

My Home Assistant runs at home, so I figured it would keep going without the internet. When
I actually checked, a lot of it didn't:

- Notifications to my phone went through a server on the internet.
- Whether anyone was home only came from the phones' location.
- The reminder to close the bathroom window got the outside temperature from an online
  weather service. Without the internet it would have used a fixed 10 °C instead and never
  reminded me on a cold day.

Home Assistant shows for every integration whether it uses the cloud. What that means for
your own automations, it doesn't show. That's where Unclouded comes in.

## What it does

Unclouded goes through all your automations and follows them through scripts, scenes,
helpers, persons and templates down to the integrations behind them. Then it sorts them into
groups:

- keep working
- still run, but their notifications don't arrive
- stop working, completely or in part

Each automation gets a short reason, for example "Notification to Anna's phone won't
arrive".

You also get suggestions that fit your setup, for example:

- turn on local push for the companion app
- give important alerts a second way that works without the internet
- detect presence through your router as well – Unclouded names the matching router entry
  for each phone
- use a local alternative where a cloud integration has one

Each suggestion links straight to the page where you change it.

On top of that, Unclouded checks your voice assistant, tells you when an integration relies
more on the internet after an update than before, and lets you star important automations
so they show up under Repairs. A small sensor watches your connection. After a real outage
the panel shows what actually failed, so you can see how close the estimate was.

Unclouded only reads. It never changes your setup.

## How it works

1. Open **Unclouded** in the sidebar. The top shows how many automations keep working
   without the internet.
2. **What you can do** lists the suggestions, most useful first.
3. Below, every automation is listed by what happens to it. **Technical details** shows
   which trigger, condition or action needs the internet and why.

   <picture><source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/automations-dark.png"><img src="docs/screenshots/automations.png" width="640" alt="Automations that only lose their notifications"></picture>

4. Star the automations that matter. Home Assistant then lists them under
   **Settings → Repairs** while they depend on the internet.

The [guide](docs/guide.md) goes through the panel in detail and explains how Unclouded comes
to its results.

## Installation

Unclouded needs Home Assistant 2026.10 or newer.

**HACS:** use the button or search for **Unclouded** in HACS, then download it and restart
Home Assistant.

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Schnuecks&repository=ha-unclouded&category=integration)

**Manually:** copy `custom_components/unclouded` into the `custom_components` folder of
your Home Assistant configuration and restart.

Then add the integration under **Settings → Devices & services → Add integration →
Unclouded**. The panel appears in the sidebar for admins.

## Good to know

It's an estimate, not a test. Unclouded never cuts your internet – it looks at how each
integration connects. Some integrations run locally or through the cloud depending on how
they are set up, and Unclouded knows many of them. If it can't tell for one of your
integrations, you can set it yourself.

To notice real outages, Unclouded briefly connects to the public DNS servers 1.1.1.1 and
9.9.9.9 on port 53 once a minute. It sends no data. This is the only connection it makes
itself.

If a template only puts together an entity ID while the automation is running, Unclouded
can't follow it and leaves it out.

If something is classified wrong, please open an issue with the integration and how it is
set up, so it gets fixed for everyone. See [CONTRIBUTING](CONTRIBUTING.md).

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
