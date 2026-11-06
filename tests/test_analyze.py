"""Tests for the analysis of automations."""

from typing import Any

import pytest
from homeassistant.components.notify.legacy import NOTIFY_SERVICES
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
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
from custom_components.unclouded.push import async_record_local_push
from custom_components.unclouded.settings import async_get_settings


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
    assert report.config_id == "test"
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


async def test_legacy_notify_service_named_after_device(
    hass: HomeAssistant, setup
) -> None:
    """A legacy notify service is matched to the integration that registered it."""

    class Service:
        _service_name = "living_room_tv"
        registered_targets: dict = {}

    hass.data.setdefault(NOTIFY_SERVICES, {})["esphome"] = [Service()]
    report = await _analyze(
        hass,
        {"triggers": [LOCAL_TRIGGER], "actions": [{"action": "notify.living_room_tv"}]},
    )
    assert report.verdict is Verdict.WORKS
    (notify,) = [d for d in report.dependencies if d.kind == "action"]
    assert notify.entry_id == setup["local"].entry_id


async def test_scene_created_at_runtime_is_internal(hass: HomeAssistant, setup) -> None:
    """A scene that only exists after scene.create is not an unknown dependency."""
    assert await async_setup_component(hass, "scene", {})
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [
                {"action": "scene.turn_on", "target": {"entity_id": "scene.before"}}
            ],
        },
    )
    assert report.verdict is Verdict.WORKS


async def test_device_trigger_uses_its_entry(hass: HomeAssistant, setup) -> None:
    """A device trigger depends on the config entry of the device."""
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=setup["cloud"].entry_id, identifiers={("met", "home")}
    )
    report = await _analyze(
        hass,
        {
            "triggers": [
                {
                    "trigger": "device",
                    "device_id": device.id,
                    "domain": "met",
                    "type": "anything",
                }
            ],
            "actions": [LOCAL_ACTION],
        },
    )
    (dep,) = [d for d in report.dependencies if d.kind == "device"]
    assert (dep.reach, dep.entry_id) == (Reach.CLOUD, setup["cloud"].entry_id)


async def _template_sensor(hass: HomeAssistant, state: str, **extra) -> None:
    assert await async_setup_component(
        hass,
        "template",
        {"template": [{"sensor": [{"name": "Mix", "state": state, **extra}]}]},
    )
    await hass.async_block_till_done()


@pytest.mark.parametrize("unique_id", [{}, {"unique_id": "mix"}])
async def test_yaml_template_follows_its_sources(
    hass: HomeAssistant, setup, unique_id: dict
) -> None:
    """A template sensor from YAML is as dependent as the entities it reads."""
    await _template_sensor(
        hass,
        "{{ states('sensor.local_temp') }} {{ states('sensor.cloud_temp') }}",
        **unique_id,
    )
    report = await _analyze(
        hass,
        {
            "triggers": [{"trigger": "state", "entity_id": "sensor.mix"}],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.FAILS
    (dep,) = [d for d in report.dependencies if d.ref == "sensor.mix"]
    assert dep.entry_id == setup["cloud"].entry_id


async def test_local_template_stays_local(hass: HomeAssistant, setup) -> None:
    """A template over local entities does not need the internet."""
    await _template_sensor(hass, "{{ states('sensor.local_temp') | float(0) * 2 }}")
    report = await _analyze(
        hass,
        {
            "triggers": [{"trigger": "state", "entity_id": "sensor.mix"}],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.WORKS


async def test_ui_helper_reads_its_entry(hass: HomeAssistant, setup) -> None:
    """A helper set up in the UI names its source in the config entry."""
    helper = MockConfigEntry(
        domain="derivative", options={"source": "sensor.cloud_temp", "round": 2}
    )
    helper.add_to_hass(hass)
    er.async_get(hass).async_get_or_create(
        "sensor", "derivative", "rate", suggested_object_id="rate", config_entry=helper
    )
    hass.states.async_set("sensor.rate", "0")
    report = await _analyze(
        hass,
        {
            "triggers": [{"trigger": "state", "entity_id": "sensor.rate"}],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.FAILS


async def test_ui_template_helper_renders_its_template(
    hass: HomeAssistant, setup
) -> None:
    """A template helper from the UI keeps its template in the entry options."""
    helper = MockConfigEntry(
        domain="template",
        options={
            "template_type": "sensor",
            "state": "{{ states('sensor.cloud_temp') }}",
        },
    )
    helper.add_to_hass(hass)
    er.async_get(hass).async_get_or_create(
        "sensor", "template", "ui", suggested_object_id="ui", config_entry=helper
    )
    hass.states.async_set("sensor.ui", "1")
    report = await _analyze(
        hass,
        {
            "triggers": [{"trigger": "state", "entity_id": "sensor.ui"}],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.FAILS


async def test_helpers_referring_to_each_other_terminate(
    hass: HomeAssistant, setup
) -> None:
    """Two helpers reading each other do not loop forever."""
    reg = er.async_get(hass)
    for name, other in (("a", "b"), ("b", "a")):
        reg.async_get_or_create("sensor", "group", name, suggested_object_id=name)
        hass.states.async_set(f"sensor.{name}", "1", {"entity_id": [f"sensor.{other}"]})
    report = await _analyze(
        hass,
        {
            "triggers": [{"trigger": "state", "entity_id": "sensor.a"}],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.WORKS


async def test_person_with_local_tracker_is_local(hass: HomeAssistant, setup) -> None:
    """A tracker in the home network next to the phone is enough for presence."""
    er.async_get(hass).async_get_or_create(
        "device_tracker",
        "esphome",
        "router_phone",
        suggested_object_id="router_phone",
        config_entry=setup["local"],
    )
    hass.states.async_set(
        "person.someone",
        "home",
        {"device_trackers": ["device_tracker.phone", "device_tracker.router_phone"]},
    )
    report = await _analyze(
        hass,
        {
            "triggers": [
                {"trigger": "numeric_state", "entity_id": "zone.home", "below": 1}
            ],
            "actions": [LOCAL_ACTION],
        },
    )
    assert report.verdict is Verdict.WORKS
    (zone,) = [d for d in report.dependencies if d.ref == "zone.home"]
    assert zone.reason == "person_local_tracker"


async def test_scene_apply_names_its_entities(hass: HomeAssistant, setup) -> None:
    """Entities set by scene.apply count like targets."""
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [
                {
                    "action": "scene.apply",
                    "data": {
                        "entities": {
                            "light.local_lamp": "on",
                            "sensor.cloud_temp": {"state": "1"},
                        }
                    },
                }
            ],
        },
    )
    assert report.verdict is Verdict.DEGRADED
    assert {"light.local_lamp", "sensor.cloud_temp"} <= {
        d.ref for d in report.dependencies
    }


async def test_scene_create_snapshot(hass: HomeAssistant, setup) -> None:
    """Entities saved by scene.create are part of the automation too."""
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [
                {
                    "action": "scene.create",
                    "data": {
                        "scene_id": "before",
                        "snapshot_entities": [
                            "light.local_lamp",
                            "weather.cloud_forecast",
                        ],
                    },
                }
            ],
        },
    )
    assert "weather.cloud_forecast" in {d.ref for d in report.dependencies}


async def test_stored_scene_follows_its_entities(hass: HomeAssistant, setup) -> None:
    """A scene from scenes.yaml is as dependent as the entities it sets."""
    assert await async_setup_component(
        hass,
        "scene",
        {"scene": [{"name": "Evening", "entities": {"sensor.cloud_temp": "1"}}]},
    )
    await hass.async_block_till_done()
    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [
                {"action": "scene.turn_on", "target": {"entity_id": "scene.evening"}}
            ],
        },
    )
    (scene,) = [d for d in report.dependencies if d.ref == "scene.evening"]
    assert scene.reach is Reach.CLOUD


async def test_open_push_channel_is_remembered(hass: HomeAssistant, setup) -> None:
    """An iPhone with local push keeps a channel open; that is remembered."""
    unclouded = MockConfigEntry(domain=DOMAIN)
    unclouded.add_to_hass(hass)
    phone = setup["phone"]
    hass.config_entries.async_update_entry(
        phone, data={**phone.data, "webhook_id": "hook"}
    )
    hass.data["mobile_app"] = {"push_channel": {"hook": object()}}

    assert async_record_local_push(hass)
    # Nothing new the second time.
    assert not async_record_local_push(hass)
    # The phone has left home: the channel is closed, but it stays remembered.
    hass.data["mobile_app"]["push_channel"] = {}

    report = await _analyze(
        hass,
        {
            "triggers": [LOCAL_TRIGGER],
            "actions": [LOCAL_ACTION, {"action": "notify.mobile_app_phone"}],
        },
    )
    (push,) = [d for d in report.dependencies if d.kind == "action"]
    assert (push.reach, push.reason) == (Reach.PARTIAL, "mobile_app_local_push")
    assert async_get_settings(hass).local_push == {phone.entry_id}
