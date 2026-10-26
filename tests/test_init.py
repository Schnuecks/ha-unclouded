"""Tests for setting up and unloading Unclouded."""

from homeassistant.components.frontend import DATA_PANELS
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.const import DOMAIN


async def test_panel_is_registered_and_removed(
    hass: HomeAssistant, hass_client
) -> None:
    """The sidebar panel comes with the entry and goes with it."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    panel = hass.data[DATA_PANELS]["unclouded"]
    assert panel.require_admin
    module_url = panel.config["_panel_custom"]["module_url"]
    client = await hass_client()
    response = await client.get(module_url)
    assert response.status == 200
    assert "customElements.define" in await response.text()

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert "unclouded" not in hass.data[DATA_PANELS]


async def test_reload_keeps_static_path(hass: HomeAssistant) -> None:
    """Setting up a second time does not register the static path again."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert await hass.config_entries.async_reload(entry.entry_id)
    assert "unclouded" in hass.data[DATA_PANELS]
