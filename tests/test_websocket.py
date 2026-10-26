"""Tests for the WebSocket commands."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.const import DOMAIN


async def test_entries_command(hass: HomeAssistant, hass_ws_client) -> None:
    """The panel gets one classified row per config entry."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    MockConfigEntry(domain="met", title="Home").add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/entries"})
    msg = await client.receive_json()
    assert msg["success"]
    rows = {row["domain"]: row for row in msg["result"]["entries"]}
    assert rows["met"]["reach"] == "cloud"
    assert rows[DOMAIN]["reach"] == "internal"
