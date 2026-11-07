"""Notice internet outages and compare them with the classification.

Unclouded checks once a minute whether two public DNS servers accept a connection;
nothing is sent. When neither does twice in a row, the internet counts as down until
one answers again. Each outage is remembered, and afterwards the recorder shows which
entities really became unavailable in that time.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .classify import EntryReach, Reach
from .const import DOMAIN

STORAGE_VERSION = 1
CHECK_INTERVAL = timedelta(minutes=1)
# Only a connection is opened, so no request reaches anyone.
TARGETS = (("1.1.1.1", 53), ("9.9.9.9", 53))
TIMEOUT = 3
# Failed checks in a row before the internet counts as down.
FAILURES = 2
# Shorter outages say nothing about integrations that poll every few minutes.
MIN_OUTAGE = timedelta(minutes=2)
# Integrations notice an outage at their next update, often a few minutes late.
GRACE = timedelta(minutes=5)
# A cloud integration that kept working through an outage this long is suspicious.
LONG_OUTAGE = timedelta(minutes=30)
KEEP = 10
# Entities are unavailable for a while around a restart of Home Assistant.
RESTART_BEFORE = timedelta(minutes=2)
RESTART_AFTER = timedelta(minutes=10)
_GONE = ("unavailable", "unknown")


async def _reachable(host: str, port: int) -> bool:
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), TIMEOUT)
    except OSError, TimeoutError:
        return False
    writer.close()
    return True


class Watcher:
    """Checks the internet connection and remembers outages."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.outages"
        )
        self.outages: list[dict[str, str | None]] = []
        self.online: bool | None = None
        self._failures = 0
        self._first_failure: datetime | None = None
        self._listeners: list[Callable[[], None]] = []
        self._results: dict[str, dict[str, Any]] = {}

    async def async_start(self) -> Callable[[], None]:
        """Load the outages and start checking; returns the function that stops it."""
        stored = await self._store.async_load() or {}
        self.outages = stored.get("outages", [])
        # An outage still open when Home Assistant stopped ends at the next check.
        self.hass.async_create_task(self.async_check())
        return async_track_time_interval(self.hass, self.async_check, CHECK_INTERVAL)

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Call the listener when the connection state changes."""
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    async def async_check(self, _: Any = None) -> None:
        """Check the connection once."""
        results = await asyncio.gather(*(_reachable(h, p) for h, p in TARGETS))
        now = dt_util.utcnow()
        if any(results):
            self._failures = 0
            self._first_failure = None
            await self._set_online(True, now)
            return
        self._failures += 1
        self._first_failure = self._first_failure or now
        if self._failures >= FAILURES:
            await self._set_online(False, self._first_failure)

    async def _set_online(self, online: bool, when: datetime) -> None:
        open_outage = self.outages[-1] if self.outages else None
        if open_outage and open_outage["end"] is not None:
            open_outage = None
        if online and open_outage:
            start = dt_util.parse_datetime(open_outage["start"])
            if start and when - start < MIN_OUTAGE:
                self.outages.pop()
            else:
                open_outage["end"] = when.isoformat()
            await self._save()
        elif not online and not open_outage:
            self.outages.append({"start": when.isoformat(), "end": None})
            self.outages = self.outages[-KEEP:]
            await self._save()
        if online != self.online:
            self.online = online
            for listener in list(self._listeners):
                listener()

    async def _save(self) -> None:
        await self._store.async_save({"outages": self.outages})

    async def async_evaluate(
        self, start: datetime, end: datetime, entries: list[EntryReach]
    ) -> dict[str, Any]:
        """What happened to each config entry's entities during a period."""
        key = f"{start.isoformat()}|{end.isoformat()}"
        if key not in self._results:
            self._results[key] = await async_evaluate(self.hass, start, end, entries)
        return self._results[key]

    async def async_remove(self) -> None:
        """Forget the outages when Unclouded is removed."""
        await self._store.async_remove()


def _naive(when: datetime) -> datetime:
    return dt_util.as_utc(when).replace(tzinfo=None)


def _read(
    hass: HomeAssistant, start: datetime, end: datetime, entity_ids: list[str]
) -> tuple[dict[str, list[Any]], list[datetime]]:
    """States during the period and the times Home Assistant started in it."""
    from homeassistant.components.recorder import history
    from homeassistant.components.recorder.db_schema import RecorderRuns
    from homeassistant.components.recorder.util import session_scope
    from sqlalchemy import select

    states = history.get_significant_states(
        hass,
        start,
        end + GRACE,
        entity_ids,
        include_start_time_state=True,
        significant_changes_only=False,
        no_attributes=True,
    )
    with session_scope(hass=hass, read_only=True) as session:
        restarts = [
            run.replace(tzinfo=dt_util.UTC)
            for run in session.execute(
                # The table keeps times in UTC without a time zone.
                select(RecorderRuns.start).where(
                    RecorderRuns.start >= _naive(start - RESTART_AFTER),
                    RecorderRuns.start <= _naive(end + GRACE),
                )
            ).scalars()
        ]
    return states, restarts


@dataclass(slots=True)
class _Count:
    total: int = 0
    gone: int = 0


async def async_evaluate(
    hass: HomeAssistant, start: datetime, end: datetime, entries: list[EntryReach]
) -> dict[str, Any]:
    """Compare what became unavailable with how each entry was classified."""
    from homeassistant.components.recorder import get_instance

    ent_reg = er.async_get(hass)
    by_entry: dict[str, list[str]] = {}
    for entity in ent_reg.entities.values():
        if entity.config_entry_id and not entity.disabled_by:
            by_entry.setdefault(entity.config_entry_id, []).append(entity.entity_id)
    entity_ids = [e for ids in by_entry.values() for e in ids]
    if not entity_ids:
        return {"entries": [], "restarts": []}
    states, restarts = await get_instance(hass).async_add_executor_job(
        partial(_read, hass, start, end, entity_ids)
    )

    def restarting(when: datetime) -> bool:
        return any(r - RESTART_BEFORE <= when <= r + RESTART_AFTER for r in restarts)

    long = end - start >= LONG_OUTAGE
    result = []
    for entry in entries:
        count = _Count()
        for entity_id in by_entry.get(entry.entry_id, []):
            history_states = states.get(entity_id, [])
            if not history_states:
                continue
            # Entities that were already gone before the outage tell nothing.
            first = history_states[0]
            if first.state in _GONE and first.last_changed <= start:
                continue
            count.total += 1
            if any(
                s.state in _GONE and not restarting(s.last_changed)
                for s in history_states
            ):
                count.gone += 1
        if not count.total:
            continue
        local = entry.reach in (Reach.LOCAL, Reach.INTERNAL)
        if count.gone and local:
            outcome = "surprise"
        elif count.gone:
            outcome = "confirmed"
        elif entry.reach is Reach.CLOUD and long:
            outcome = "kept"
        else:
            outcome = "unchanged"
        result.append(
            {
                "entry_id": entry.entry_id,
                "reach": entry.reach,
                "total": count.total,
                "gone": count.gone,
                "outcome": outcome,
            }
        )
    return {"entries": result, "restarts": [r.isoformat() for r in restarts]}
