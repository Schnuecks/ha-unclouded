# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## Unreleased

### Added
- Sidebar panel that shows what in Home Assistant still works without the internet: a
  summary, one sentence per automation, technical details and the classification of every
  integration, in English and German.
- Suggestions worked out from the setup: local push, a second local way for push-only
  alerts, local presence detection with the matching router entry for each phone, devices
  behind a manufacturer's cloud and local text-to-speech.
- Automations are followed through scripts, scenes (also `scene.apply` and `scene.create`),
  groups, template sensors and other helpers, persons and zones, and notifications.
- Rules for integrations whose declaration is not enough, such as phones, push notifications
  through the relay and integrations that run locally or through the cloud depending on
  their set-up.
- Unknown integrations can be classified by the user; what Unclouded found out itself cannot
  be overruled.
- Important automations (★) get a repair issue while they depend on the internet.
- A repair issue when an integration needs more of the internet after an update than before.
