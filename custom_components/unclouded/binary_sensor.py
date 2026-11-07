"""A sensor that shows whether Home Assistant reaches the internet."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, WATCHER
from .outages import Watcher


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the internet sensor."""
    async_add_entities([InternetSensor(entry, hass.data[WATCHER])])


class InternetSensor(BinarySensorEntity):
    """On while the internet is reachable."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True
    _attr_translation_key = "internet"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, watcher: Watcher) -> None:
        self._watcher = watcher
        self._attr_unique_id = f"{entry.entry_id}_internet"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Unclouded",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        return self._watcher.online is not None

    @property
    def is_on(self) -> bool | None:
        return self._watcher.online

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._watcher.async_add_listener(self.async_write_ha_state)
        )
