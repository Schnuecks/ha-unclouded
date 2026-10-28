"""Tests for reporting integrations that need more of the internet than before."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    mock_integration,
)

from custom_components.unclouded.const import DOMAIN
from custom_components.unclouded.repairs import async_update_issues

KEY = f"{DOMAIN}.baseline"


def _remember(hass_storage: dict[str, Any], known: dict[str, str]) -> None:
    hass_storage[KEY] = {"version": 1, "minor_version": 1, "key": KEY, "data": known}


async def _setup(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    await async_update_issues(hass)


def _issue(hass: HomeAssistant, entry: MockConfigEntry) -> ir.IssueEntry | None:
    return ir.async_get(hass).async_get_issue(DOMAIN, f"changed_{entry.entry_id}")


async def test_first_look_only_remembers(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """Without anything remembered there is nothing to compare."""
    met = MockConfigEntry(domain="met")
    met.add_to_hass(hass)
    await _setup(hass)
    assert _issue(hass, met) is None
    assert hass_storage[KEY]["data"][met.entry_id] == "cloud"


@pytest.mark.parametrize(
    ("before", "key"), [("local", "now_cloud"), ("partial", "now_cloud")]
)
async def test_worse_reach_raises_issue(
    hass: HomeAssistant, hass_storage: dict[str, Any], before: str, key: str
) -> None:
    """An integration that used to work locally and now needs the cloud is reported."""
    met = MockConfigEntry(domain="met", title="Weather")
    met.add_to_hass(hass)
    _remember(hass_storage, {met.entry_id: before})
    await _setup(hass)
    issue = _issue(hass, met)
    assert issue is not None
    assert issue.translation_key == key
    assert issue.translation_placeholders == {"title": "Weather", "domain": "met"}
    assert issue.is_fixable


async def test_local_to_partial(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """Partly local is worse than local."""
    phone = MockConfigEntry(domain="mobile_app")
    phone.add_to_hass(hass)
    _remember(hass_storage, {phone.entry_id: "local"})
    await _setup(hass)
    assert _issue(hass, phone).translation_key == "now_partial"


async def test_better_reach_is_not_reported(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """Going local is good news and needs no issue; it is remembered, though."""
    node = MockConfigEntry(domain="esphome")
    node.add_to_hass(hass)
    _remember(hass_storage, {node.entry_id: "cloud"})
    await _setup(hass)
    assert _issue(hass, node) is None
    assert hass_storage[KEY]["data"][node.entry_id] == "local"


async def test_new_integration_is_not_reported(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """A newly added cloud integration did not change; it is just new."""
    _remember(hass_storage, {"some_other_entry": "local"})
    met = MockConfigEntry(domain="met")
    met.add_to_hass(hass)
    await _setup(hass)
    assert _issue(hass, met) is None


async def test_unknown_keeps_last_known_state(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """An entry that cannot be classified any more keeps what was known."""
    thing = MockConfigEntry(domain="custom_thing")
    thing.add_to_hass(hass)
    _remember(hass_storage, {thing.entry_id: "local"})
    await _setup(hass)
    assert _issue(hass, thing) is None
    assert hass_storage[KEY]["data"][thing.entry_id] == "local"


async def test_confirming_removes_issue(
    hass: HomeAssistant, hass_storage: dict[str, Any], hass_client
) -> None:
    """The issue is fixed by confirming it, and is not raised again."""
    met = MockConfigEntry(domain="met")
    met.add_to_hass(hass)
    _remember(hass_storage, {met.entry_id: "local"})
    assert await async_setup_component(hass, "repairs", {})
    await _setup(hass)

    client = await hass_client()
    resp = await client.post(
        "/api/repairs/issues/fix",
        json={"handler": DOMAIN, "issue_id": f"changed_{met.entry_id}"},
    )
    flow = await resp.json()
    assert flow["step_id"] == "confirm"
    resp = await client.post(f"/api/repairs/issues/fix/{flow['flow_id']}", json={})
    assert (await resp.json())["type"] == "create_entry"
    assert _issue(hass, met) is None

    await async_update_issues(hass)
    assert _issue(hass, met) is None


async def test_issue_of_removed_entry_goes(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """When the integration is removed, its issue goes too."""
    # A stand-in without requirements, so that removing it imports nothing.
    mock_integration(
        hass, MockModule("cloudy", partial_manifest={"iot_class": "cloud_polling"})
    )
    met = MockConfigEntry(domain="cloudy")
    met.add_to_hass(hass)
    _remember(hass_storage, {met.entry_id: "local"})
    await _setup(hass)
    assert _issue(hass, met) is not None
    await hass.config_entries.async_remove(met.entry_id)
    await async_update_issues(hass)
    assert _issue(hass, met) is None
    assert met.entry_id not in hass_storage[KEY]["data"]


async def test_removing_unclouded_forgets(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    """Removing Unclouded removes what it remembered and its issues."""
    met = MockConfigEntry(domain="met")
    met.add_to_hass(hass)
    _remember(hass_storage, {met.entry_id: "local"})
    await _setup(hass)
    own = hass.config_entries.async_entries(DOMAIN)[0]
    await hass.config_entries.async_remove(own.entry_id)
    await hass.async_block_till_done()
    assert KEY not in hass_storage
    assert _issue(hass, met) is None
