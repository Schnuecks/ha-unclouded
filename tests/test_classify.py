"""Tests for the classification of config entries."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.classify import (
    Reach,
    async_classify_entries,
    reach_from_iot_class,
)


@pytest.mark.parametrize(
    ("iot_class", "reach"),
    [
        ("local_push", Reach.LOCAL),
        ("local_polling", Reach.LOCAL),
        ("cloud_push", Reach.CLOUD),
        ("cloud_polling", Reach.CLOUD),
        ("calculated", Reach.INTERNAL),
        ("assumed_state", Reach.UNKNOWN),
        (None, Reach.UNKNOWN),
    ],
)
def test_reach_from_iot_class(iot_class: str | None, reach: Reach) -> None:
    """Every iot_class maps to a reach."""
    assert reach_from_iot_class(iot_class)[0] is reach


async def _classify(hass: HomeAssistant, entry: MockConfigEntry):
    entry.add_to_hass(hass)
    return {r.entry_id: r for r in await async_classify_entries(hass)}[entry.entry_id]


async def test_built_in_integration_uses_iot_class(hass: HomeAssistant) -> None:
    """A core integration without a rule is classified by its manifest."""
    result = await _classify(hass, MockConfigEntry(domain="met", title="Home"))
    assert result.iot_class == "cloud_polling"
    assert result.reach is Reach.CLOUD
    assert result.reason == "iot_class_cloud"


async def test_missing_integration_is_unknown(hass: HomeAssistant) -> None:
    """An entry whose integration is not installed does not break the report."""
    result = await _classify(hass, MockConfigEntry(domain="not_installed_anywhere"))
    assert result.iot_class is None
    assert result.reach is Reach.UNKNOWN


@pytest.mark.parametrize(
    ("options", "reach", "reason"),
    [
        ({"mode": "local"}, Reach.LOCAL, "sonoff_local"),
        ({"mode": "auto"}, Reach.LOCAL, "sonoff_auto"),
        ({}, Reach.LOCAL, "sonoff_auto"),
        ({"mode": "cloud"}, Reach.CLOUD, "sonoff_cloud"),
    ],
)
async def test_sonoff_mode(
    hass: HomeAssistant, options: dict, reach: Reach, reason: str
) -> None:
    """Sonoff is classified by the connection mode of the entry."""
    result = await _classify(hass, MockConfigEntry(domain="sonoff", options=options))
    assert (result.reach, result.reason) == (reach, reason)


@pytest.mark.parametrize(
    ("data", "reach"),
    [
        ({"conn_mode": "local"}, Reach.LOCAL),
        ({"conn_mode": "auto"}, Reach.PARTIAL),
        ({"conn_mode": "cloud"}, Reach.CLOUD),
    ],
)
async def test_xiaomi_miot_mode(hass: HomeAssistant, data: dict, reach: Reach) -> None:
    """Xiaomi Miot is classified by the connection mode of the entry."""
    result = await _classify(hass, MockConfigEntry(domain="xiaomi_miot", data=data))
    assert result.reach is reach


async def test_rule_overrides_iot_class(hass: HomeAssistant) -> None:
    """mobile_app declares local_push, but a phone away from home needs the internet."""
    result = await _classify(hass, MockConfigEntry(domain="mobile_app"))
    assert result.iot_class == "local_push"
    assert result.reach is Reach.PARTIAL


async def test_built_in_hardware_is_local(hass: HomeAssistant) -> None:
    """A USB adapter declares no iot_class but sits in the host."""
    result = await _classify(hass, MockConfigEntry(domain="homeassistant_connect_zbt2"))
    assert result.iot_class == "local_polling"
    assert result.reach is Reach.LOCAL
