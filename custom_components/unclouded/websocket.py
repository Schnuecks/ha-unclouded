"""WebSocket commands for the Unclouded panel."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .advice import build_advice
from .analyze import async_analyze_automations
from .classify import async_can_override, async_classify_entries
from .const import DOMAIN
from .repairs import async_update_issues
from .settings import (
    Settings,
    async_get_settings,
    async_save_settings,
    entry_key,
    prune,
)

_REGISTERED = f"{DOMAIN}_websocket_registered"


@callback
def async_register(hass: HomeAssistant) -> None:
    """Register the commands once per run; they cannot be removed again."""
    if hass.data.get(_REGISTERED):
        return
    websocket_api.async_register_command(hass, ws_entries)
    websocket_api.async_register_command(hass, ws_automations)
    websocket_api.async_register_command(hass, ws_set_override)
    websocket_api.async_register_command(hass, ws_set_important)
    hass.data[_REGISTERED] = True


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/entries"})
@websocket_api.async_response
async def ws_entries(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return the classification of all config entries."""
    overrides = async_get_settings(hass).overrides
    entries = await async_classify_entries(hass, overrides)
    connection.send_result(
        msg["id"], {"entries": [asdict(e) for e in entries], "overrides": overrides}
    )


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/automations"})
@websocket_api.async_response
async def ws_automations(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return the verdict for every automation and what the user can do."""
    reports = await async_analyze_automations(hass)
    entries = await async_classify_entries(hass, async_get_settings(hass).overrides)
    connection.send_result(
        msg["id"],
        {
            "automations": [asdict(r) for r in reports],
            "advice": [asdict(a) for a in build_advice(hass, reports, entries)],
        },
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/set_override",
        vol.Required("key"): vol.Match(r"^(entry|domain):[\w.-]+$"),
        # None returns to what Unclouded found out by itself.
        vol.Required("reach"): vol.Any(None, vol.In(["local", "cloud", "partial"])),
    }
)
@websocket_api.async_response
async def ws_set_override(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Classify a config entry or an integration that Unclouded cannot classify."""
    settings = async_get_settings(hass)
    if msg["reach"] is None:
        settings.overrides.pop(msg["key"], None)
    elif await async_can_override(hass, msg["key"]):
        settings.overrides[msg["key"]] = msg["reach"]
    else:
        connection.send_error(
            msg["id"], "not_unknown", "Only unknown integrations can be classified"
        )
        return
    prune(
        settings, (entry_key(e.entry_id) for e in hass.config_entries.async_entries())
    )
    await _save(hass, connection, msg, settings)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/set_important",
        vol.Required("entity_id"): vol.Match(r"^automation\.\w+$"),
        vol.Required("important"): bool,
    }
)
@websocket_api.async_response
async def ws_set_important(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Mark an automation as one the user wants to be told about."""
    settings = async_get_settings(hass)
    if msg["important"]:
        settings.important.add(msg["entity_id"])
    else:
        settings.important.discard(msg["entity_id"])
    await _save(hass, connection, msg, settings)


async def _save(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
    settings: Settings,
) -> None:
    if not hass.config_entries.async_entries(DOMAIN):
        connection.send_error(msg["id"], "not_set_up", "Unclouded is not set up")
        return
    async_save_settings(hass, settings)
    await async_update_issues(hass)
    connection.send_result(msg["id"])
