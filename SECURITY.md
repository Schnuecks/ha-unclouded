# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems. Report them privately through
GitHub instead: on the repository page open **Security → Report a vulnerability**. You will
get an answer within a few days, and a fix is released as soon as possible.

If that option is not shown, contact the maintainer [@Schnuecks](https://github.com/Schnuecks)
through GitHub and ask for a private channel, without describing the problem publicly.

Helpful details: the Unclouded and Home Assistant versions and the steps to reproduce.

## What Unclouded can change

Unclouded runs inside Home Assistant and only admins can use it. It reads the configuration
of automations, scripts, scenes, helpers and integrations and changes none of them. It only
writes its own data: its settings (your classification of unknown integrations and the
automations marked as important) in its config entry, the last known state of each
integration in `.storage/unclouded.baseline`, and its own repair issues. It does not talk to
anything outside Home Assistant.
