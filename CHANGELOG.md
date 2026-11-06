# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## Unreleased

### Added
- Sidebar panel that shows what in Home Assistant still works without the internet: an
  overview with a bar split by what happens, one sentence per automation, technical
  details and the classification of every integration, in English and German.
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
- The voice assistant: every Assist pipeline with its wake word, speech-to-text, conversation
  agent and text-to-speech, whether each works without the internet, and the voice
  satellites using it.
- Local push on iPhones and iPads: their config entry does not say whether it is on, so
  Unclouded looks for the push channel the app keeps open at home and remembers the device.
- Automations named in suggestions and repair issues link to their editor; repair issues
  link to the panel.
- Suggestions come with direct links to the right settings page and, for integrations that
  go through a cloud, a known local way where there is one.
- Advice on announcements and the voice assistant takes small hardware into account: fixed
  sentences are played from the TTS cache without the internet, local TTS as a fallback.
- Templates are read for the entities they use. A cloud value read with a fallback, such as
  `float(10)`, is reported separately: the automation keeps running, but on the fallback.
- A cloud value in an "or" condition no longer counts as a failure when another branch of
  that condition works locally.
- Suggestions name integrations instead of entry titles such as station IDs, and cloud
  services like weather are no longer called devices.
