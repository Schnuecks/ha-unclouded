"""Unclouded: shows what in Home Assistant still works without the internet."""

from __future__ import annotations

import hashlib
from datetime import timedelta
from pathlib import Path
from typing import Any

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.start import async_at_started

from . import websocket
from .const import DOMAIN
from .repairs import async_remove_issues, async_update_issues

PANEL_URL = "unclouded"
STATIC_URL = "/unclouded_static"
PANEL_JS = Path(__file__).parent / "frontend" / "unclouded-panel.js"
_STATIC_REGISTERED = f"{DOMAIN}_static_registered"
# Integrations can change how they connect without a reload being noticed.
REFRESH_INTERVAL = timedelta(hours=1)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Unclouded from a config entry."""
    websocket.async_register(hass)

    # Static paths cannot be removed again, so they are registered once per run.
    if not hass.data.get(_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(PANEL_JS.parent), cache_headers=False)]
        )
        hass.data[_STATIC_REGISTERED] = True
    # The hash makes browsers load a changed panel after an update.
    digest = await hass.async_add_executor_job(
        lambda: hashlib.sha256(PANEL_JS.read_bytes()).hexdigest()[:12]
    )
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL,
        webcomponent_name="unclouded-panel",
        module_url=f"{STATIC_URL}/{PANEL_JS.name}?v={digest}",
        sidebar_title="Unclouded",
        sidebar_icon="mdi:cloud-off-outline",
        require_admin=True,
    )

    async def refresh(_: Any = None) -> None:
        await async_update_issues(hass)

    async def at_started(_: HomeAssistant) -> None:
        await refresh()

    # Automations are only all loaded once Home Assistant has started.
    entry.async_on_unload(async_at_started(hass, at_started))
    entry.async_on_unload(hass.bus.async_listen("automation_reloaded", refresh))
    entry.async_on_unload(async_track_time_interval(hass, refresh, REFRESH_INTERVAL))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    frontend.async_remove_panel(hass, PANEL_URL, warn_if_unknown=False)
    async_remove_issues(hass)
    return True
