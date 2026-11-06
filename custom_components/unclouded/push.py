"""Notice phones that receive notifications over the home network.

The Android app records in its config entry that it supports local push. The iOS app
does not: local push is switched on in the app, per network. While it is on and the
phone is at home, the app keeps a push channel to Home Assistant open, so Unclouded
looks for open channels from time to time and remembers the phones it saw.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .settings import async_get_settings, async_save_settings

# Where the mobile app integration keeps open push channels, by webhook ID.
MOBILE_APP = "mobile_app"
PUSH_CHANNEL = "push_channel"


def async_record_local_push(hass: HomeAssistant) -> bool:
    """Remember phones with an open push channel; True if one was new."""
    if not hass.config_entries.async_entries(DOMAIN):
        return False
    channels = hass.data.get(MOBILE_APP, {}).get(PUSH_CHANNEL, {})
    if not channels:
        return False
    settings = async_get_settings(hass)
    seen = {
        entry.entry_id
        for entry in hass.config_entries.async_entries(MOBILE_APP)
        if entry.data.get("webhook_id") in channels
    }
    if seen <= settings.local_push:
        return False
    settings.local_push |= seen
    async_save_settings(hass, settings)
    return True
