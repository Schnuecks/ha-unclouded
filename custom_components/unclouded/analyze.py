"""Work out which automations keep working without the internet.

Every automation is walked through its triggers, conditions and actions. Each entity,
device and action it uses is traced back to the config entries behind it, and the
reach of those entries (see classify.py) decides the verdict. Scripts called from an
action are followed into their own configuration.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from homeassistant.components.automation import DATA_COMPONENT as AUTOMATIONS
from homeassistant.components.notify.legacy import NOTIFY_SERVICES
from homeassistant.core import HomeAssistant, split_entity_id
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integrations
from homeassistant.util import slugify

from .classify import (
    EntryReach,
    Reach,
    async_classify_entries,
    effective_iot_class,
    reach_from_iot_class,
)


class Part(StrEnum):
    """Where in an automation a dependency is used."""

    TRIGGER = "trigger"
    CONDITION = "condition"
    ACTION = "action"


class Verdict(StrEnum):
    """What happens to an automation without the internet."""

    WORKS = "works"
    # Runs, but some of its actions do not get through.
    DEGRADED = "degraded"
    FAILS = "fails"
    # Nothing known to need the internet, but some parts could not be classified.
    UNKNOWN = "unknown"


# Higher is worse; used to combine several sources into one reach.
_SEVERITY = {
    Reach.LOCAL: 0,
    Reach.INTERNAL: 0,
    Reach.UNKNOWN: 1,
    Reach.PARTIAL: 2,
    Reach.CLOUD: 3,
}
_NEEDS_INTERNET = (Reach.CLOUD, Reach.PARTIAL)
# Actions that only tell someone something.
_NOTIFY_DOMAINS = ("notify", "tts")
# Script actions that start other scripts given as target.
_SCRIPT_STARTERS = ("script.turn_on", "script.toggle")
# The script component keeps its entities under its domain, without a typed key.
SCRIPTS = "script"
_TOP_LEVEL = {
    "trigger": Part.TRIGGER,
    "triggers": Part.TRIGGER,
    "condition": Part.CONDITION,
    "conditions": Part.CONDITION,
    "action": Part.ACTION,
    "actions": Part.ACTION,
}


# Reach, reason and config entry of whatever an automation uses.
type Source = tuple[Reach, str, str | None]


@dataclass(frozen=True, slots=True)
class Dependency:
    """One thing an automation relies on."""

    part: Part
    # "entity", "device" or "action".
    kind: str
    ref: str
    reach: Reach
    # Stable key of the reason; the panel turns it into text.
    reason: str
    entry_id: str | None = None
    notification: bool = False


@dataclass(slots=True)
class AutomationReport:
    """Verdict for one automation."""

    entity_id: str
    name: str
    verdict: Verdict
    # True when everything that needs the internet only sends notifications.
    only_notifications: bool
    dependencies: list[Dependency] = field(default_factory=list)


def _worst(reaches: Iterable[Source]) -> Source:
    result: Source | None = None
    for item in reaches:
        if result is None or _SEVERITY[item[0]] > _SEVERITY[result[0]]:
            result = item
    return result or (Reach.LOCAL, "iot_class_local", None)


def _as_list(value: Any) -> list[str]:
    """Entity or device references as a list, without templates."""
    if isinstance(value, str):
        value = [v.strip() for v in value.split(",")]
    if not isinstance(value, list):
        return []
    return [v for v in value if isinstance(v, str) and v and "{" not in v]


class Analyzer:
    """Trace automations back to config entries. Build one per analysis run."""

    def __init__(
        self,
        hass: HomeAssistant,
        entries: list[EntryReach],
        iot_classes: dict[str, str | None],
    ) -> None:
        self.hass = hass
        self.entries = {e.entry_id: e for e in entries}
        self.iot_classes = iot_classes
        self.ent_reg = er.async_get(hass)
        self.dev_reg = dr.async_get(hass)
        self.area_reg = ar.async_get(hass)

    # --- entities and devices -------------------------------------------------

    def _entry(self, entry_id: str) -> Source:
        if (entry := self.entries.get(entry_id)) is None:
            return Reach.UNKNOWN, "entry_missing", entry_id
        return entry.reach, entry.reason, entry_id

    def entity_reach(
        self, entity_id: str, seen: frozenset[str] = frozenset()
    ) -> Source:
        """Reach of an entity, following groups, persons and zones to their sources."""
        if entity_id in seen:
            return Reach.LOCAL, "iot_class_local", None
        seen = seen | {entity_id}
        domain = split_entity_id(entity_id)[0]
        state = self.hass.states.get(entity_id)

        if domain == "zone":
            # A zone counts the persons in it.
            persons = self.hass.states.async_entity_ids("person")
            return _worst(self.entity_reach(p, seen) for p in persons)
        if domain == "person":
            trackers = state.attributes.get("device_trackers", []) if state else []
            return _worst(self._tracker_reach(t, seen) for t in trackers)

        if entry := self.ent_reg.async_get(entity_id):
            if entry.config_entry_id:
                result = self._entry(entry.config_entry_id)
            else:
                reach, reason = reach_from_iot_class(
                    self.iot_classes.get(entry.platform)
                )
                result = (reach, reason, None)
        else:
            reach, reason = reach_from_iot_class(self.iot_classes.get(domain))
            result = (reach, reason, None)

        # Groups and similar helpers list their members.
        if result[0] is Reach.INTERNAL and state:
            members = _as_list(state.attributes.get("entity_id"))
            if members:
                return _worst(self.entity_reach(m, seen) for m in members)
        return result

    def _tracker_reach(self, entity_id: str, seen: frozenset[str]) -> Source:
        reach, reason, entry_id = self.entity_reach(entity_id, seen)
        if entry_id and self.entries[entry_id].domain == "mobile_app":
            # The phone reports its position over the internet while away.
            return Reach.PARTIAL, "mobile_app_presence", entry_id
        return reach, reason, entry_id

    def device_reach(self, device_id: str) -> Source:
        """Reach of a device through the config entry it belongs to."""
        if (device := self.dev_reg.async_get(device_id)) is None:
            return Reach.UNKNOWN, "device_missing", None
        if device.config_entry_id is None:
            return Reach.UNKNOWN, "entry_missing", None
        return self._entry(device.config_entry_id)

    def area_entities(self, area_id: str) -> set[str]:
        """Entities in an area, directly or through their device."""
        result = {e.entity_id for e in er.async_entries_for_area(self.ent_reg, area_id)}
        for device in dr.async_entries_for_area(self.dev_reg, area_id):
            for entry in er.async_entries_for_device(self.ent_reg, device.id):
                if entry.area_id is None:
                    result.add(entry.entity_id)
        return result

    # --- actions --------------------------------------------------------------

    def action_reach(self, action: str) -> tuple[Reach, str, str | None, bool] | None:
        """Reach of an action itself, apart from the entities it targets."""
        domain, _, name = action.partition(".")
        notification = domain in _NOTIFY_DOMAINS
        if domain == "notify":
            reach, reason, entry_id = self._notify_reach(name)
            return reach, reason, entry_id, True
        # Actions of integrations with config entries, e.g. pushover or a cloud AI.
        if entries := self.hass.config_entries.async_entries(domain):
            reach, reason, entry_id = _worst(self._entry(e.entry_id) for e in entries)
            return reach, reason, entry_id, notification
        return None

    def _notify_reach(self, name: str) -> Source:
        for entry in self.hass.config_entries.async_entries("mobile_app"):
            if name == f"mobile_app_{slugify(entry.data.get('device_name', ''))}":
                app_data = entry.data.get("app_data", {})
                if app_data.get("push_websocket_channel"):
                    # Local push while the phone is in the home network.
                    return Reach.PARTIAL, "mobile_app_local_push", entry.entry_id
                if "push_url" in app_data:
                    return Reach.CLOUD, "mobile_app_push_relay", entry.entry_id
                return Reach.UNKNOWN, "mobile_app_no_push", entry.entry_id
        if domain := self._legacy_notify_owner(name):
            if entries := self.hass.config_entries.async_entries(domain):
                return _worst(self._entry(e.entry_id) for e in entries)
            reach, reason = reach_from_iot_class(self.iot_classes.get(domain))
            return reach, reason, None
        # Newer integrations offer notify entities.
        if entry := self.ent_reg.async_get(f"notify.{name}"):
            return self.entity_reach(entry.entity_id)
        # Legacy notify services are usually named after their integration.
        for entry in self.hass.config_entries.async_entries():
            if name == entry.domain or name.startswith(f"{entry.domain}_"):
                return self._entry(entry.entry_id)
        return Reach.UNKNOWN, "notify_unknown", None

    def _legacy_notify_owner(self, name: str) -> str | None:
        """The integration that registered a legacy notify service.

        Their names come from the device or the configuration (e.g. the name of a
        TV), so they are looked up where the notify component keeps them.
        """
        for domain, services in self.hass.data.get(NOTIFY_SERVICES, {}).items():
            for service in services:
                if name == getattr(service, "_service_name", None) or name in getattr(
                    service, "registered_targets", {}
                ):
                    return domain
        return None

    # --- walking the configuration --------------------------------------------

    def walk_config(self, config: dict[str, Any]) -> list[Dependency]:
        """Collect the dependencies of an automation configuration."""
        deps: list[Dependency] = []
        for key, part in _TOP_LEVEL.items():
            if key in config:
                self._walk(config[key], part, deps, set())
        return deps

    def _walk(
        self, node: Any, part: Part, deps: list[Dependency], scripts: set[str]
    ) -> None:
        if isinstance(node, list):
            for item in node:
                self._walk(item, part, deps, scripts)
            return
        if not isinstance(node, dict):
            return

        action = node.get("action", node.get("service"))
        if isinstance(action, str) and "{" not in action:
            self._add_action(action, node, part, deps, scripts)

        for key, value in node.items():
            if key == "entity_id":
                for entity_id in _as_list(value):
                    self._add_entity(entity_id, part, deps, scripts)
            elif key == "device_id":
                for device_id in _as_list(value):
                    reach, reason, entry_id = self.device_reach(device_id)
                    deps.append(
                        Dependency(part, "device", device_id, reach, reason, entry_id)
                    )
            elif key == "area_id":
                for area_id in _as_list(value):
                    for entity_id in sorted(self.area_entities(area_id)):
                        self._add_entity(entity_id, part, deps, scripts)
            elif isinstance(value, (dict, list)):
                self._walk(value, part, deps, scripts)

    def _add_entity(
        self, entity_id: str, part: Part, deps: list[Dependency], scripts: set[str]
    ) -> None:
        if "." not in entity_id:
            return
        reach, reason, entry_id = self.entity_reach(entity_id)
        deps.append(Dependency(part, "entity", entity_id, reach, reason, entry_id))
        if entity_id.startswith("script."):
            self._follow_script(entity_id, part, deps, scripts)

    def _add_action(
        self,
        action: str,
        node: dict[str, Any],
        part: Part,
        deps: list[Dependency],
        scripts: set[str],
    ) -> None:
        if action.startswith("script.") and action not in _SCRIPT_STARTERS:
            self._follow_script(action, part, deps, scripts)
            return
        if (result := self.action_reach(action)) is None:
            return
        reach, reason, entry_id, notification = result
        deps.append(
            Dependency(part, "action", action, reach, reason, entry_id, notification)
        )

    def _follow_script(
        self, entity_id: str, part: Part, deps: list[Dependency], scripts: set[str]
    ) -> None:
        if entity_id in scripts or SCRIPTS not in self.hass.data:
            return
        scripts.add(entity_id)
        script = self.hass.data[SCRIPTS].get_entity(entity_id)
        if script is not None and script.raw_config:
            self._walk(script.raw_config.get("sequence", []), part, deps, scripts)


def judge(deps: list[Dependency]) -> tuple[Verdict, bool]:
    """Combine the dependencies of one automation into a verdict."""
    triggers = [d for d in deps if d.part is Part.TRIGGER]
    conditions = [d for d in deps if d.part is Part.CONDITION]
    actions = [d for d in deps if d.part is Part.ACTION]
    affected = [d for d in deps if d.reach in _NEEDS_INTERNET]
    only_notifications = bool(affected) and all(
        d.part is Part.ACTION and d.notification for d in affected
    )

    # Triggers are alternatives: the automation is only lost when every one of them is.
    if triggers and all(d.reach is Reach.CLOUD for d in triggers):
        return Verdict.FAILS, False
    # An unavailable entity in a condition usually blocks the run.
    if any(d.reach is Reach.CLOUD for d in conditions):
        return Verdict.FAILS, False
    if actions and all(d.reach is Reach.CLOUD for d in actions):
        return Verdict.FAILS, only_notifications
    if affected:
        return Verdict.DEGRADED, only_notifications
    if any(d.reach is Reach.UNKNOWN for d in deps):
        return Verdict.UNKNOWN, False
    return Verdict.WORKS, False


async def async_analyze_automations(hass: HomeAssistant) -> list[AutomationReport]:
    """Analyze every automation of this instance."""
    if AUTOMATIONS not in hass.data:
        return []
    entries = await async_classify_entries(hass)
    domains = {e.platform for e in er.async_get(hass).entities.values()}
    domains |= {split_entity_id(s)[0] for s in hass.states.async_entity_ids()}
    # Loaded integrations cover entities that do not exist yet, e.g. from scene.create.
    domains |= {c.partition(".")[0] for c in hass.config.components}
    integrations = await async_get_integrations(hass, domains)
    iot_classes = {d: effective_iot_class(i) for d, i in integrations.items()}
    analyzer = Analyzer(hass, entries, iot_classes)

    reports = []
    for automation in hass.data[AUTOMATIONS].entities:
        deps = analyzer.walk_config(automation.raw_config or {})
        verdict, only_notifications = judge(deps)
        state = hass.states.get(automation.entity_id)
        reports.append(
            AutomationReport(
                entity_id=automation.entity_id,
                name=state.name if state else automation.entity_id,
                verdict=verdict,
                only_notifications=only_notifications,
                dependencies=deps,
            )
        )
    return sorted(reports, key=lambda r: r.entity_id)
