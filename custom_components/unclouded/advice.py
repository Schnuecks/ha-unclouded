"""Turn the analysis into things the user can do about it.

Each piece of advice names the automations and integrations it is about; the panel
explains why it matters and what to do.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .analyze import AutomationReport, Part, Verdict
from .classify import EntryReach, Reach

# Most important first; the panel shows them in this order.
ORDER = (
    "local_push",
    "local_fallback",
    "presence",
    "cloud_devices",
    "local_tts",
)


@dataclass(slots=True)
class Advice:
    """One thing the user can do."""

    key: str
    # Automations it would help, by entity ID.
    automations: list[str] = field(default_factory=list)
    # Config entries it is about, e.g. the phones or the cloud integrations.
    entries: list[str] = field(default_factory=list)
    # Config entries that could help, e.g. local device trackers.
    helpers: list[str] = field(default_factory=list)


def _sorted(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def build_advice(
    hass: HomeAssistant, reports: list[AutomationReport], entries: list[EntryReach]
) -> list[Advice]:
    """Work out what would make this instance less dependent on the internet."""
    by_id = {e.entry_id: e for e in entries}
    found: dict[str, Advice] = {key: Advice(key) for key in ORDER}

    for report in reports:
        for dep in report.dependencies:
            entry = by_id.get(dep.entry_id or "")
            # Push through the relay while local push is off.
            if dep.reason == "mobile_app_push_relay":
                found["local_push"].automations.append(report.entity_id)
                found["local_push"].entries.append(dep.entry_id)
            # Presence from phones only arrives over the internet while away.
            elif dep.reason == "mobile_app_presence":
                found["presence"].automations.append(report.entity_id)
                found["presence"].entries.append(dep.entry_id)
            # Spoken announcements through a cloud service.
            elif (
                dep.part is Part.ACTION
                and dep.reach is Reach.CLOUD
                and dep.ref.startswith("tts.")
            ):
                found["local_tts"].automations.append(report.entity_id)
                found["local_tts"].entries.append(dep.entry_id or "")
            # Devices and services behind a vendor cloud, apart from notifications.
            elif (
                dep.reach is Reach.CLOUD
                and not dep.notification
                and entry is not None
                and entry.domain != "mobile_app"
            ):
                found["cloud_devices"].automations.append(report.entity_id)
                found["cloud_devices"].entries.append(entry.entry_id)

        # Automations that only tell someone, and only through the internet.
        if report.only_notifications and report.verdict is Verdict.FAILS:
            found["local_fallback"].automations.append(report.entity_id)

    # Integrations that already see devices in the home network.
    trackers = {
        e.config_entry_id
        for e in er.async_get(hass).entities.values()
        if e.domain == "device_tracker" and e.config_entry_id
    }
    found["presence"].helpers = [
        entry_id
        for entry_id in trackers
        if (e := by_id.get(entry_id)) and e.reach is Reach.LOCAL
    ]

    result = []
    for key in ORDER:
        advice = found[key]
        if not advice.automations:
            continue
        advice.automations = _sorted(advice.automations)
        advice.entries = _sorted(e for e in advice.entries if e)
        advice.helpers = _sorted(advice.helpers)
        result.append(advice)
    return result
