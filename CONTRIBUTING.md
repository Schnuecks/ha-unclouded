# Contributing to Unclouded

Thanks for your interest! Bug reports, ideas and pull requests are welcome.

## Reporting problems

Use the issue forms: **Bug report** or **Feature request**. For bugs, please add the
technical details the panel shows for the automation in question (see the bug report
form). German is fine too.

Security problems go to **Security → Report a vulnerability** instead, see
[SECURITY.md](SECURITY.md).

## An integration is classified wrongly

Unclouded starts from what an integration declares about itself (its `iot_class`) and
corrects it where that is not enough, for example when an integration can run locally or
through the cloud depending on how it was set up. If an integration is classified wrongly,
please open an issue with the integration and how it is set up; the fix is a rule in
`classify.py`, so that it is right for everyone.

## Pull requests

1. Open an issue first for larger changes, so we can agree on the approach.
2. Set up the development environment and make sure all checks pass:

   ```bash
   python -m venv .venv && . .venv/bin/activate
   pip install -r requirements-dev.txt
   ruff check . && ruff format --check . && pytest
   ```

3. Unclouded only reads: it must not change automations, devices or integrations.
4. Update README.md and README.de.md if needed and add a line under "Unreleased" in
   `CHANGELOG.md` if users will notice the change.

The pull request template has a short checklist for this.

## Code layout

| Path | Contents |
|---|---|
| `custom_components/unclouded/classify.py` | How each config entry connects; rules for integrations whose `iot_class` is not enough |
| `custom_components/unclouded/analyze.py` | Following automations, scripts, scenes and helpers to the integrations behind them |
| `custom_components/unclouded/advice.py` | What the user can do about it |
| `custom_components/unclouded/repairs.py` | Repair issues for important automations |
| `custom_components/unclouded/changes.py` | Noticing integrations that need more of the internet than before |
| `custom_components/unclouded/settings.py` | The user's choices, stored in the config entry |
| `custom_components/unclouded/websocket.py` | WebSocket commands for the panel |
| `custom_components/unclouded/frontend/` | The sidebar panel (plain JavaScript, no build step) |
| `tests/` | Tests |

## License

By contributing you agree that your contribution is released under the
[MIT License](LICENSE).
