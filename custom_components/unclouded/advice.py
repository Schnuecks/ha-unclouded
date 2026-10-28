"""Turn the analysis into things the user can do about it.

Each piece of advice names the automations and integrations it is about; the panel
explains why it matters and what to do.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
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
    # Concrete steps found in the setup, e.g. a local tracker for a person's phone.
    matches: list[dict[str, Any]] = field(default_factory=list)


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
    if found["presence"].automations:
        found["presence"].matches = _local_trackers_for_phones(hass, by_id)

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


# Words that do not tell phones apart: "iPhone von Andrea" is "iphone-andrea".
_FILLER = {"von", "de", "der", "of", "the", "my", "mein", "meine", "la", "le", "di"}


def _split(name: str | None) -> list[str]:
    # Host names drop the apostrophe: "Sam's phone" is "sams-phone".
    return re.findall(r"[a-z0-9]+", re.sub(r"['’]", "", (name or "").lower()))


def _words(name: str | None) -> frozenset[str]:
    return frozenset(w for w in _split(name) if w not in _FILLER)


def _local_trackers_for_phones(
    hass: HomeAssistant, by_id: dict[str, EntryReach]
) -> list[dict[str, Any]]:
    """Find a local tracker for each phone that is a person's only presence source.

    Routers name a phone after its host name, e.g. "iphone-andreas" for the phone
    "iPhone Andreas"; a tracker matches when its name has the same words as the
    phone, or as the phone's first word plus the person's name.
    """
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)
    local = [
        e
        for e in ent_reg.entities.values()
        if e.domain == "device_tracker"
        and e.config_entry_id
        and (entry := by_id.get(e.config_entry_id))
        and entry.reach is Reach.LOCAL
    ]
    local_ids = {e.entity_id for e in local}

    def device_name(entry: er.RegistryEntry) -> str | None:
        device = dev_reg.async_get(entry.device_id) if entry.device_id else None
        return device and (device.name_by_user or device.name)

    matches = []
    for person in hass.states.async_all("person"):
        trackers = person.attributes.get("device_trackers", [])
        if any(t in local_ids for t in trackers):
            continue
        for tracker in trackers:
            phone = ent_reg.async_get(tracker)
            if phone is None or phone.platform != "mobile_app":
                continue
            phone_name = device_name(phone) or phone.original_name or tracker
            phone_words = _words(phone_name)
            wanted = {phone_words}
            if phone_words:
                wanted.add(frozenset({_split(phone_name)[0]}) | _words(person.name))
            for candidate in local:
                names = (
                    candidate.name,
                    candidate.original_name,
                    device_name(candidate),
                )
                if not any(_words(n) in wanted for n in names if n):
                    continue
                matches.append(
                    {
                        "person": person.entity_id,
                        "person_name": person.name,
                        "phone": tracker,
                        "phone_name": phone_name,
                        "tracker": candidate.entity_id,
                        "tracker_name": (
                            candidate.name
                            or candidate.original_name
                            or device_name(candidate)
                            or candidate.entity_id
                        ).strip(),
                        "entry_id": candidate.config_entry_id,
                        "disabled": candidate.disabled_by is not None,
                    }
                )
    return matches
