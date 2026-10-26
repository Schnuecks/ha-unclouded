"""Tests for the analysis of automations."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.analyze import (
    Part,
    Verdict,
    async_analyze_automations,
)
from custom_components.unclouded.classify import Reach
from custom_components.unclouded.const import DOMAIN


@pytest.fixture
def setup(hass: HomeAssistant) -> dict[str, MockConfigEntry]:
    """A local and a cloud integration, a phone and pushover, each with entities."""
    entries = {
        "local": MockConfigEntry(domain="esphome", title="Node"),
        "cloud": MockConfigEntry(domain="met", title="Home"),
        "pushover": MockConfigEntry(domain="pushover", title="Pushover"),
        "phone": MockConfigEntry(
            domain="mobile_app",
            title="Phone",
            data={"device_name": "Phone", "app_data": {"push_url": "https://x"}},
        ),
        "tablet": MockConfigEntry(
            domain="mobile_app",
            title="Tablet",
            data={
                "device_name": "Tablet",
                "app_data": {"push_url": "https://x", "push_websocket_channel": True},
            },
        ),
    }
    for entry in entries.values():
        entry.add_to_hass(hass)

    reg = er.async_get(hass)
    for domain, object_id, entry in (
        ("sensor", "local_temp", "local"),
        ("light", "local_lamp", "local"),
        ("weather", "cloud_forecast", "cloud"),
        ("sensor", "cloud_temp", "cloud"),
        ("device_tracker", "phone", "phone"),
    ):
        reg.async_get_or_create(
            domain,
            entries[entry].domain,
            object_id,
            suggested_object_id=object_id,
            config_entry=entries[entry],
        )
        hass.states.async_set(f"{domain}.{object_id}", "1")
    hass.states.async_set(
        "person.someone", "home", {"device_trackers": ["device_tracker.phone"]}
    )
    hass.states.async_set("zone.home", "1")
    return entries


async def _analyze(
    hass: HomeAssistant, config: dict[str, Any], scripts: dict | None = None
):
    if scripts:
        assert await async_setup_component(hass, "script", {"script": scripts})
    config = {"id": "test", "alias": "Test", **config}
    assert await async_setup_component(hass, "automation", {"automation": [config]})
    await hass.async_block_till_done()
    (report,) = await async_analyze_automations(hass)
    return report


LOCAL_TRIGGER = {"trigger": "state", "entity_id": "sensor.local_temp"}
LOCAL_ACTION = {"action": "light.turn_on", "target": {"entity_id": "light.local_lamp"}}


async def test_local_automation_works(hass: HomeAssistant, setup) -> None:
    """Local trigger and local action."""
    report = await _analyze(
        hass, {"triggers": [LOCAL_TRIGGER], "actions": [LOCAL_ACTION]}
    )
    assert report.verdict is Verdict.WORKS
    assert report.name == "Test"
    assert {d.ref for d in report.dependencies} == {
        "sensor.local_temp",
        "light.local_lamp",
    }


async def test_push_via_relay_is_lost(hass: HomeAssistant, setup) -> None:
    """The local action runs, the push to the phone does not arrive."""
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [LOCAL_ACTION, {"action": "notify.mobile_app_phone"}],
        },
    )
    assert report.verdict is Verdict.DEGRADED
    assert report.only_notifications
    (push,) = [d for d in report.dependencies if d.kind == "action"]
    assert (push.reach, push.reason) == (Reach.CLOUD, "mobile_app_push_relay")
    assert push.entry_id == setup["phone"].entry_id


async def test_notification_only_automation_fails(hass: HomeAssistant, setup) -> None:
    """An automation that only notifies does nothing without the internet."""
    report = await _analyze(
        hass,
        {"triggers": [LOCAL_TRIGGER], "actions": [{"action": "notify.pushover"}]},
    )
    assert report.verdict is Verdict.FAILS
    assert report.only_notifications


async def test_local_push_is_partial(hass: HomeAssistant, setup) -> None:
    """With local push, the phone still gets the message at home."""
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [{"action": "notify.mobile_app_tablet"}],
        },
    )
    assert report.verdict is Verdict.DEGRADED
    assert report.dependencies[-1].reason == "mobile_app_local_push"


async def test_cloud_trigger_fails(hass: HomeAssistant, setup) -> None:
    """A cloud entity as the only trigger never fires."""
    report = await _analyze(
        hass,
        {
            "triggers": [{"trigger": "state", "entity_id": "weather.cloud_forecast"}],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.FAILS


async def test_one_cloud_trigger_of_two_degrades(hass: HomeAssistant, setup) -> None:
    """Triggers are alternatives: the local one still fires."""
    report = await _analyze(
        hass,
        {
            "triggers": [
                LOCAL_TRIGGER,
                {"trigger": "state", "entity_id": "weather.cloud_forecast"},
            ],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.DEGRADED
    assert not report.only_notifications


async def test_cloud_condition_fails(hass: HomeAssistant, setup) -> None:
    """A condition on an unavailable cloud entity blocks the run."""
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "conditions": [
                {"condition": "state", "entity_id": "sensor.cloud_temp", "state": "1"}
            ],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.FAILS
    (cond,) = [d for d in report.dependencies if d.part is Part.CONDITION]
    assert cond.reach is Reach.CLOUD


async def test_presence_through_phone_is_partial(hass: HomeAssistant, setup) -> None:
    """Counting persons in a zone relies on phones reporting from outside."""
    report = await _analyze(
        hass,
        {
            "triggers": [
                {"trigger": "numeric_state", "entity_id": "zone.home", "below": 1}
            ],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.DEGRADED
    (zone,) = [d for d in report.dependencies if d.ref == "zone.home"]
    assert (zone.reach, zone.reason) == (Reach.PARTIAL, "mobile_app_presence")


async def test_script_is_followed(hass: HomeAssistant, setup) -> None:
    """Actions inside a called script count for the automation."""
    report = await _analyze(
        hass,
        {"triggers": [LOCAL_TRIGGER], "actions": [{"action": "script.tell"}]},
        scripts={"tell": {"sequence": [{"action": "notify.pushover"}]}},
    )
    assert report.verdict is Verdict.FAILS
    assert [d.ref for d in report.dependencies if d.kind == "action"] == [
        "notify.pushover"
    ]


async def test_recursive_script_terminates(hass: HomeAssistant, setup) -> None:
    """A script that starts itself is followed only once."""
    report = await _analyze(
        hass,
        {"triggers": [LOCAL_TRIGGER], "actions": [{"action": "script.loop"}]},
        scripts={
            "loop": {
                "sequence": [
                    LOCAL_ACTION,
                    {
                        "action": "script.turn_on",
                        "target": {"entity_id": "script.loop"},
                    },
                ]
            }
        },
    )
    assert report.verdict is Verdict.WORKS


async def test_group_members_are_resolved(hass: HomeAssistant, setup) -> None:
    """A helper is as dependent as its members."""
    er.async_get(hass).async_get_or_create(
        "sensor", "group", "mix", suggested_object_id="mix"
    )
    hass.states.async_set(
        "sensor.mix", "1", {"entity_id": ["sensor.local_temp", "sensor.cloud_temp"]}
    )
    report = await _analyze(
        hass,
        {
            "triggers": [{"trigger": "state", "entity_id": "sensor.mix"}],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.FAILS


async def test_area_target_is_expanded(hass: HomeAssistant, setup) -> None:
    """Targeting an area means targeting the entities in it."""
    area = ar.async_get(hass).async_create("Office")
    er.async_get(hass).async_update_entity("sensor.cloud_temp", area_id=area.id)
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [
                LOCAL_ACTION,
                {
                    "action": "homeassistant.update_entity",
                    "target": {"area_id": area.id},
                },
            ],
        },
    )
    assert report.verdict is Verdict.DEGRADED
    assert "sensor.cloud_temp" in {d.ref for d in report.dependencies}


async def test_templates_are_skipped(hass: HomeAssistant, setup) -> None:
    """Templated references cannot be resolved and are left out."""
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [
                {
                    "action": "light.turn_on",
                    "target": {"entity_id": "{{ 'light.' ~ 'x' }}"},
                }
            ],
        },
    )
    assert report.verdict is Verdict.WORKS
    assert [d.ref for d in report.dependencies] == ["sensor.local_temp"]


async def test_websocket_automations(
    hass: HomeAssistant, setup, hass_ws_client
) -> None:
    """The panel gets the verdict of every automation."""
    await _analyze(
        hass,
        {"triggers": [LOCAL_TRIGGER], "actions": [{"action": "notify.pushover"}]},
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)

    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/automations"})
    msg = await client.receive_json()
    assert msg["success"]
    (row,) = msg["result"]["automations"]
    assert row["verdict"] == "fails"
    assert row["dependencies"][-1]["reach"] == "cloud"
