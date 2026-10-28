"""Tests for the advice worked out from the analysis."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.advice import build_advice
from custom_components.unclouded.analyze import async_analyze_automations
from custom_components.unclouded.classify import async_classify_entries
from custom_components.unclouded.const import DOMAIN

LAMP = {"action": "light.turn_on", "target": {"entity_id": "light.lamp"}}
LOCAL = {"trigger": "state", "entity_id": "light.lamp"}


async def _advice(
    hass: HomeAssistant, automations: list[dict]
) -> tuple[dict, dict[str, str]]:
    """Entries for a phone, a local node, a cloud service and the cloud TTS."""
    phone = MockConfigEntry(
        domain="mobile_app",
        title="Phone",
        data={"device_name": "Phone", "app_data": {"push_url": "https://x"}},
    )
    local = MockConfigEntry(domain="esphome", title="Node")
    cloud = MockConfigEntry(domain="met", title="Weather")
    tts = MockConfigEntry(domain="cloud", title="Cloud")
    for entry in (phone, local, cloud, tts):
        entry.add_to_hass(hass)
    reg = er.async_get(hass)
    for domain, object_id, entry in (
        ("light", "lamp", local),
        ("device_tracker", "phone", phone),
        ("device_tracker", "router_phone", local),
        ("sensor", "forecast", cloud),
        ("tts", "speech", tts),
    ):
        reg.async_get_or_create(
            domain,
            entry.domain,
            object_id,
            suggested_object_id=object_id,
            config_entry=entry,
        )
    hass.states.async_set(
        "person.a", "home", {"device_trackers": ["device_tracker.phone"]}
    )
    hass.states.async_set("zone.home", "1")
    configs = [
        {"id": str(i), "alias": f"A{i}", **config}
        for i, config in enumerate(automations)
    ]
    assert await async_setup_component(hass, "automation", {"automation": configs})
    await hass.async_block_till_done()
    reports = await async_analyze_automations(hass)
    entries = await async_classify_entries(hass)
    advice = {a.key: a for a in build_advice(hass, reports, entries)}
    ids = {"phone": phone, "local": local, "cloud": cloud, "tts": tts}
    return advice, {name: entry.entry_id for name, entry in ids.items()}


async def test_push_only_automation(hass: HomeAssistant) -> None:
    """A push through the relay suggests local push and a local second way."""
    advice, ids = await _advice(
        hass,
        [{"triggers": [LOCAL], "actions": [{"action": "notify.mobile_app_phone"}]}],
    )
    assert advice["local_push"].automations == ["automation.a0"]
    assert advice["local_push"].entries == [ids["phone"]]
    assert advice["local_fallback"].automations == ["automation.a0"]


async def test_push_next_to_local_action(hass: HomeAssistant) -> None:
    """An automation that also does something locally needs no second way."""
    advice, ids = await _advice(
        hass,
        [
            {
                "triggers": [LOCAL],
                "actions": [LAMP, {"action": "notify.mobile_app_phone"}],
            }
        ],
    )
    assert "local_push" in advice
    assert "local_fallback" not in advice


async def test_presence_with_local_tracker(hass: HomeAssistant) -> None:
    """Presence from the phone suggests a local tracker that already exists."""
    advice, ids = await _advice(
        hass,
        [
            {
                "triggers": [
                    {"trigger": "numeric_state", "entity_id": "zone.home", "below": 1}
                ],
                "actions": [LAMP],
            }
        ],
    )
    assert advice["presence"].entries == [ids["phone"]]
    assert advice["presence"].helpers == [ids["local"]]


async def test_cloud_device_and_tts(hass: HomeAssistant) -> None:
    """Cloud devices and cloud speech are named with their integrations."""
    advice, ids = await _advice(
        hass,
        [
            {
                "triggers": [{"trigger": "state", "entity_id": "sensor.forecast"}],
                "actions": [
                    LAMP,
                    {"action": "tts.speak", "target": {"entity_id": "tts.speech"}},
                ],
            }
        ],
    )
    assert advice["cloud_devices"].entries == [ids["cloud"]]
    assert advice["local_tts"].entries == [ids["tts"]]


async def test_nothing_to_do(hass: HomeAssistant) -> None:
    """A local automation gets no advice."""
    advice, ids = await _advice(hass, [{"triggers": [LOCAL], "actions": [LAMP]}])
    assert advice == {}


async def test_websocket_includes_advice(hass: HomeAssistant, hass_ws_client) -> None:
    """The panel gets the advice together with the automations."""
    await _advice(
        hass,
        [{"triggers": [LOCAL], "actions": [{"action": "notify.mobile_app_phone"}]}],
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": f"{DOMAIN}/automations"})
    msg = await client.receive_json()
    assert [a["key"] for a in msg["result"]["advice"]] == [
        "local_push",
        "local_fallback",
    ]


async def _presence_setup(hass: HomeAssistant, local_names: list[str]) -> None:
    """A person tracked by the phone "Phone von Alex" and local trackers by name."""
    phone = MockConfigEntry(domain="mobile_app", title="Phone von Alex")
    router = MockConfigEntry(domain="esphome", title="Router")
    for entry in (phone, router):
        entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=phone.entry_id,
        identifiers={("mobile_app", "alex")},
        name="Phone von Alex",
    )
    reg = er.async_get(hass)
    reg.async_get_or_create(
        "device_tracker",
        "mobile_app",
        "alex",
        suggested_object_id="phone_alex",
        config_entry=phone,
        device_id=device.id,
    )
    for i, name in enumerate(local_names):
        reg.async_get_or_create(
            "device_tracker",
            "esphome",
            f"client{i}",
            suggested_object_id=f"client{i}",
            config_entry=router,
            original_name=name,
            disabled_by=er.RegistryEntryDisabler.INTEGRATION,
        )
    hass.states.async_set(
        "person.alex",
        "home",
        {"device_trackers": ["device_tracker.phone_alex"], "friendly_name": "Alex"},
    )
    hass.states.async_set("zone.home", "1")
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": [
                {
                    "id": "p",
                    "alias": "Presence",
                    "triggers": [
                        {
                            "trigger": "numeric_state",
                            "entity_id": "zone.home",
                            "below": 1,
                        }
                    ],
                    "actions": [],
                }
            ]
        },
    )
    await hass.async_block_till_done()


async def _presence(hass: HomeAssistant):
    reports = await async_analyze_automations(hass)
    entries = await async_classify_entries(hass)
    return {a.key: a for a in build_advice(hass, reports, entries)}["presence"]


async def test_local_tracker_found_for_phone(hass: HomeAssistant) -> None:
    """The router's entry for the phone is named, even while it is disabled."""
    await _presence_setup(hass, ["phone-alex ", "phone-alexa", "laptop"])
    (match,) = (await _presence(hass)).matches
    assert match["person"] == "person.alex"
    assert match["phone_name"] == "Phone von Alex"
    assert match["tracker"] == "device_tracker.client0"
    assert match["tracker_name"] == "phone-alex"
    assert match["disabled"]


async def test_tracker_named_after_person(hass: HomeAssistant) -> None:
    """A router entry named after the phone type and the person also matches."""
    await _presence_setup(hass, ["Phone Alex"])
    (match,) = (await _presence(hass)).matches
    assert match["tracker"] == "device_tracker.client0"


async def test_person_with_local_tracker_needs_nothing(hass: HomeAssistant) -> None:
    """A person who already has a local tracker needs no presence advice at all."""
    await _presence_setup(hass, ["phone-alex"])
    hass.states.async_set(
        "person.alex",
        "home",
        {"device_trackers": ["device_tracker.phone_alex", "device_tracker.client0"]},
    )
    reports = await async_analyze_automations(hass)
    entries = await async_classify_entries(hass)
    assert "presence" not in {a.key for a in build_advice(hass, reports, entries)}


async def test_apostrophe_is_dropped_like_in_host_names(hass: HomeAssistant) -> None:
    """ "Sam's phone" shows up in routers as "sams-phone"."""
    await _presence_setup(hass, ["sams-phone"])
    dr.async_get(hass).async_update_device(
        er.async_get(hass).async_get("device_tracker.phone_alex").device_id,
        name="Sam's phone",
    )
    (match,) = (await _presence(hass)).matches
    assert match["tracker_name"] == "sams-phone"
