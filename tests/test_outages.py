"""Tests for the internet watcher and the comparison with real outages."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unclouded.classify import async_classify_entries
from custom_components.unclouded.outages import Watcher

REACHABLE = "custom_components.unclouded.outages._reachable"


async def test_outage_is_recorded(hass: HomeAssistant) -> None:
    """Two failed checks start an outage; the next success ends it."""
    watcher = Watcher(hass)
    changes = []
    watcher.async_add_listener(lambda: changes.append(watcher.online))
    start = dt_util.utcnow()
    with patch(REACHABLE, AsyncMock(return_value=False)):
        with patch("homeassistant.util.dt.utcnow", return_value=start):
            await watcher.async_check()
        # One failure is not enough.
        assert watcher.outages == []
        with patch(
            "homeassistant.util.dt.utcnow", return_value=start + timedelta(minutes=1)
        ):
            await watcher.async_check()
    assert watcher.online is False
    assert watcher.outages == [{"start": start.isoformat(), "end": None}]

    end = start + timedelta(minutes=10)
    with (
        patch(REACHABLE, AsyncMock(return_value=True)),
        patch("homeassistant.util.dt.utcnow", return_value=end),
    ):
        await watcher.async_check()
    assert watcher.online is True
    assert watcher.outages == [{"start": start.isoformat(), "end": end.isoformat()}]
    assert changes == [False, True]


async def test_short_outage_is_dropped(hass: HomeAssistant) -> None:
    """An outage under two minutes is not kept."""
    watcher = Watcher(hass)
    start = dt_util.utcnow()
    with patch(REACHABLE, AsyncMock(return_value=False)):
        await watcher.async_check()
        await watcher.async_check()
    with (
        patch(REACHABLE, AsyncMock(return_value=True)),
        patch(
            "homeassistant.util.dt.utcnow", return_value=start + timedelta(seconds=90)
        ),
    ):
        await watcher.async_check()
    assert watcher.outages == []


async def test_evaluate_compares_with_classification(hass: HomeAssistant) -> None:
    """Cloud entities that went away confirm; local ones that went away surprise."""
    cloud = MockConfigEntry(domain="met", title="Weather")
    local = MockConfigEntry(domain="esphome", title="Node")
    quiet = MockConfigEntry(domain="withings", title="Scale")
    for entry in (cloud, local, quiet):
        entry.add_to_hass(hass)
    reg = er.async_get(hass)
    ids = {}
    for name, entry in (("w", cloud), ("n", local), ("s", quiet)):
        ids[name] = reg.async_get_or_create(
            "sensor", entry.domain, name, suggested_object_id=name, config_entry=entry
        ).entity_id
    start = dt_util.utcnow() - timedelta(hours=1)
    end = start + timedelta(minutes=45)
    before = start - timedelta(minutes=1)

    def state(entity_id: str, value: str, when):
        return State(entity_id, value, last_changed=when, last_updated=when)

    history = {
        ids["w"]: [state(ids["w"], "10", before), state(ids["w"], "unavailable", end)],
        ids["n"]: [state(ids["n"], "1", before), state(ids["n"], "unavailable", start)],
        ids["s"]: [state(ids["s"], "70", before)],
    }
    recorder = MagicMock()
    # Home Assistant started once during the outage; the node went away with it.
    restart = start + timedelta(minutes=20)
    history[ids["n"]].append(state(ids["n"], "unavailable", restart))
    recorder.async_add_executor_job = AsyncMock(return_value=(history, [restart]))
    entries = await async_classify_entries(hass)
    with patch("homeassistant.components.recorder.get_instance", return_value=recorder):
        result = await Watcher(hass).async_evaluate(start, end, entries)

    assert result["restarts"] == [restart.isoformat()]
    outcomes = {
        r["entry_id"]: (r["outcome"], r["gone"], r["total"]) for r in result["entries"]
    }
    assert outcomes[cloud.entry_id] == ("confirmed", 1, 1)
    assert outcomes[local.entry_id] == ("surprise", 1, 1)
    # A cloud integration that kept working through a long outage.
    assert outcomes[quiet.entry_id] == ("kept", 0, 1)
