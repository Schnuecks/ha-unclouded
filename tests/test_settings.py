"""Tests for own classifications, important automations and their repair issues."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.analyze import Verdict, async_analyze_automations
from custom_components.unclouded.classify import Reach, async_classify_entries
from custom_components.unclouded.const import DOMAIN
from custom_components.unclouded.settings import async_get_settings

LAMP = {"action": "light.turn_on", "target": {"entity_id": "light.lamp"}}


async def _setup(hass: HomeAssistant, actions: list, trigger_entity: str) -> None:
    """Unclouded, a cloud and a local integration, and one automation."""
    cloud = MockConfigEntry(domain="met", title="Weather")
    local = MockConfigEntry(domain="esphome", title="Node")
    for entry in (cloud, local):
        entry.add_to_hass(hass)
    reg = er.async_get(hass)
    reg.async_get_or_create(
        "sensor", "met", "w", suggested_object_id="w", config_entry=cloud
    )
    reg.async_get_or_create(
        "light", "esphome", "lamp", suggested_object_id="lamp", config_entry=local
    )
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": [
                {
                    "id": "a",
                    "alias": "Alarm",
                    "triggers": [{"trigger": "state", "entity_id": trigger_entity}],
                    "actions": actions,
                }
            ]
        },
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def _send(hass_ws_client, hass: HomeAssistant, message: dict) -> dict:
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(message)
    return await client.receive_json()


async def test_override_of_an_entry(hass: HomeAssistant, hass_ws_client) -> None:
    """A cloud integration the user knows to be local counts as local."""
    await _setup(hass, [LAMP], "sensor.w")
    cloud = hass.config_entries.async_entries("met")[0]
    (report,) = await async_analyze_automations(hass)
    assert report.verdict is Verdict.FAILS

    msg = await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_override",
            "key": f"entry:{cloud.entry_id}",
            "reach": "local",
        },
    )
    assert msg["success"]
    (report,) = await async_analyze_automations(hass)
    assert report.verdict is Verdict.WORKS
    entries = {e.entry_id: e for e in await async_classify_entries(hass, {})}
    assert entries[cloud.entry_id].reach is Reach.CLOUD

    settings = async_get_settings(hass)
    entries = await async_classify_entries(hass, settings.overrides)
    (row,) = [e for e in entries if e.entry_id == cloud.entry_id]
    assert (row.reach, row.automatic, row.overridden) == (
        Reach.LOCAL,
        Reach.CLOUD,
        True,
    )
    assert row.reason == "user_override"

    # Back to automatic.
    await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_override",
            "key": f"entry:{cloud.entry_id}",
            "reach": None,
        },
    )
    assert async_get_settings(hass).overrides == {}


async def test_override_of_an_integration_without_entry(
    hass: HomeAssistant, hass_ws_client
) -> None:
    """Entities from YAML can be classified through their integration."""
    er.async_get(hass).async_get_or_create(
        "sensor", "custom_thing", "x", suggested_object_id="moisture"
    )
    await _setup(hass, [LAMP], "sensor.moisture")
    (report,) = await async_analyze_automations(hass)
    assert report.verdict is Verdict.UNKNOWN
    (dep,) = [d for d in report.dependencies if d.ref == "sensor.moisture"]
    assert (dep.integration, dep.entry_id) == ("custom_thing", None)

    await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_override",
            "key": "domain:custom_thing",
            "reach": "cloud",
        },
    )
    (report,) = await async_analyze_automations(hass)
    assert report.verdict is Verdict.FAILS


async def test_invalid_override_is_refused(hass: HomeAssistant, hass_ws_client) -> None:
    """Only the offered choices can be stored."""
    await _setup(hass, [LAMP], "sensor.w")
    msg = await _send(
        hass_ws_client,
        hass,
        {"type": f"{DOMAIN}/set_override", "key": "entry:x", "reach": "internal"},
    )
    assert not msg["success"]


async def test_overrides_of_removed_entries_are_dropped(
    hass: HomeAssistant, hass_ws_client
) -> None:
    """Saving forgets overrides of config entries that no longer exist."""
    await _setup(hass, [LAMP], "sensor.w")
    for key in ("entry:gone", "domain:custom_thing"):
        await _send(
            hass_ws_client,
            hass,
            {"type": f"{DOMAIN}/set_override", "key": key, "reach": "local"},
        )
    assert async_get_settings(hass).overrides == {"domain:custom_thing": "local"}


async def test_important_automation_raises_issue(
    hass: HomeAssistant, hass_ws_client
) -> None:
    """Marking an automation as important raises a repair issue, unmarking clears it."""
    await _setup(hass, [LAMP], "sensor.w")
    issues = ir.async_get(hass)

    msg = await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_important",
            "entity_id": "automation.alarm",
            "important": True,
        },
    )
    assert msg["success"]
    issue = issues.async_get_issue(DOMAIN, "important_alarm")
    assert issue is not None
    assert issue.translation_key == "important_fails"
    assert issue.translation_placeholders == {"name": "Alarm"}
    (report,) = await async_analyze_automations(hass)
    assert report.important

    await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_important",
            "entity_id": "automation.alarm",
            "important": False,
        },
    )
    assert issues.async_get_issue(DOMAIN, "important_alarm") is None


async def test_important_but_local_raises_nothing(
    hass: HomeAssistant, hass_ws_client
) -> None:
    """An important automation that works without internet needs no issue."""
    hass.states.async_set("sensor.local", "1")
    await _setup(hass, [LAMP], "light.lamp")
    await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_important",
            "entity_id": "automation.alarm",
            "important": True,
        },
    )
    assert ir.async_get(hass).async_get_issue(DOMAIN, "important_alarm") is None


async def test_issue_for_lost_notifications(
    hass: HomeAssistant, hass_ws_client
) -> None:
    """When only notifications are lost, the issue says so."""
    MockConfigEntry(domain="pushover", title="Pushover").add_to_hass(hass)
    await _setup(hass, [LAMP, {"action": "notify.pushover"}], "light.lamp")
    await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_important",
            "entity_id": "automation.alarm",
            "important": True,
        },
    )
    issue = ir.async_get(hass).async_get_issue(DOMAIN, "important_alarm")
    assert issue.translation_key == "important_notifications"


async def test_issues_removed_on_unload(hass: HomeAssistant, hass_ws_client) -> None:
    """Unloading Unclouded takes its issues along."""
    await _setup(hass, [LAMP], "sensor.w")
    await _send(
        hass_ws_client,
        hass,
        {
            "type": f"{DOMAIN}/set_important",
            "entity_id": "automation.alarm",
            "important": True,
        },
    )
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert ir.async_get(hass).async_get_issue(DOMAIN, "important_alarm") is None


async def test_issues_follow_automation_reload(hass: HomeAssistant) -> None:
    """Issues are checked again when automations are reloaded."""
    entry = MockConfigEntry(domain=DOMAIN, options={"important": ["automation.alarm"]})
    cloud = MockConfigEntry(domain="met")
    cloud.add_to_hass(hass)
    er.async_get(hass).async_get_or_create(
        "sensor", "met", "w", suggested_object_id="w", config_entry=cloud
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": [
                {
                    "id": "a",
                    "alias": "Alarm",
                    "triggers": [{"trigger": "state", "entity_id": "sensor.w"}],
                    "actions": [],
                }
            ]
        },
    )
    hass.bus.async_fire("automation_reloaded")
    await hass.async_block_till_done()
    assert ir.async_get(hass).async_get_issue(DOMAIN, "important_alarm") is not None
