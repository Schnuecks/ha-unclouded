"""WebSocket commands for the Unclouded panel."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .classify import async_classify_entries
from .const import DOMAIN

_REGISTERED = f"{DOMAIN}_websocket_registered"


@callback
def async_register(hass: HomeAssistant) -> None:
    """Register the commands once per run; they cannot be removed again."""
    if hass.data.get(_REGISTERED):
        return
    websocket_api.async_register_command(hass, ws_entries)
    hass.data[_REGISTERED] = True


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/entries"})
@websocket_api.async_response
async def ws_entries(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Return the classification of all config entries."""
    entries = await async_classify_entries(hass)
    connection.send_result(msg["id"], {"entries": [asdict(e) for e in entries]})
