"""Classify config entries by whether they need the internet.

The starting point is the integration's iot_class. It describes the integration as a
whole, though, and some integrations run locally or through a cloud depending on how an
entry was set up. Those get a rule that reads the entry itself.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integrations

from .settings import entry_key


class Reach(StrEnum):
    """What an entry needs to keep working."""

    LOCAL = "local"
    CLOUD = "cloud"
    # Works locally in some situations only, e.g. a phone that is at home.
    PARTIAL = "partial"
    # Computed inside Home Assistant; depends on its sources.
    INTERNAL = "internal"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class EntryReach:
    """Classification of one config entry."""

    entry_id: str
    domain: str
    title: str
    iot_class: str | None
    reach: Reach
    # Stable key of the reason; the panel turns it into text.
    reason: str
    # What Unclouded found out by itself, before a choice of the user.
    automatic: Reach
    overridden: bool


def reach_from_iot_class(iot_class: str | None) -> tuple[Reach, str]:
    """Map an integration's iot_class to a reach."""
    if iot_class in ("local_push", "local_polling"):
        return Reach.LOCAL, "iot_class_local"
    if iot_class in ("cloud_push", "cloud_polling"):
        return Reach.CLOUD, "iot_class_cloud"
    if iot_class == "calculated":
        return Reach.INTERNAL, "iot_class_calculated"
    return Reach.UNKNOWN, "iot_class_missing"


def effective_iot_class(integration: object) -> str | None:
    """The iot_class of an integration, if it could be loaded.

    Built-in helpers like script, scene or input_boolean declare none; they only work
    with what is inside Home Assistant. Neither do built-in hardware integrations for
    adapters plugged into the host.
    """
    iot_class = getattr(integration, "iot_class", None)
    if iot_class is not None or not getattr(integration, "is_built_in", False):
        return iot_class
    if getattr(integration, "quality_scale", None) == "internal":
        return "calculated"
    # Adapters plugged into the host, e.g. Zigbee or Thread sticks.
    if getattr(integration, "integration_type", None) == "hardware":
        return "local_polling"
    return None


def _sonoff(entry: ConfigEntry) -> tuple[Reach, str]:
    # "auto" talks to devices in the LAN first and only falls back to the cloud for
    # devices without LAN control, which the entry does not record.
    mode = entry.options.get("mode", "auto")
    if mode == "cloud":
        return Reach.CLOUD, "sonoff_cloud"
    if mode == "local":
        return Reach.LOCAL, "sonoff_local"
    return Reach.LOCAL, "sonoff_auto"


def _xiaomi_miot(entry: ConfigEntry) -> tuple[Reach, str]:
    # "auto" decides per device and property, so the entry alone cannot tell.
    mode = entry.data.get("conn_mode", "auto")
    if mode == "cloud":
        return Reach.CLOUD, "xiaomi_miot_cloud"
    if mode == "local":
        return Reach.LOCAL, "xiaomi_miot_local"
    return Reach.PARTIAL, "xiaomi_miot_auto"


def _mobile_app(entry: ConfigEntry) -> tuple[Reach, str]:
    # The phone reports over the LAN at home and over the internet when away.
    return Reach.PARTIAL, "mobile_app"


def _cloud_only(entry: ConfigEntry) -> tuple[Reach, str]:
    return Reach.CLOUD, "known_cloud"


# Integrations whose iot_class does not tell the whole story.
ENTRY_RULES: dict[str, Callable[[ConfigEntry], tuple[Reach, str]]] = {
    "mobile_app": _mobile_app,
    "sonoff": _sonoff,
    # Declares local_polling but polls a cloud API.
    "tronity": _cloud_only,
    "xiaomi_miot": _xiaomi_miot,
}


async def async_classify_entries(
    hass: HomeAssistant, overrides: Mapping[str, str] | None = None
) -> list[EntryReach]:
    """Classify every config entry of this instance."""
    overrides = overrides or {}
    entries = hass.config_entries.async_entries()
    integrations = await async_get_integrations(hass, {e.domain for e in entries})
    result = []
    for entry in entries:
        # A missing custom integration comes back as an exception.
        iot_class = effective_iot_class(integrations.get(entry.domain))
        if rule := ENTRY_RULES.get(entry.domain):
            reach, reason = rule(entry)
        else:
            reach, reason = reach_from_iot_class(iot_class)
        automatic = reach
        # The user only fills gaps: a choice counts while nothing else is known.
        chosen = overrides.get(entry_key(entry.entry_id))
        if chosen and automatic is Reach.UNKNOWN:
            reach, reason = Reach(chosen), "user_override"
        result.append(
            EntryReach(
                entry_id=entry.entry_id,
                domain=entry.domain,
                title=entry.title,
                iot_class=iot_class,
                reach=reach,
                reason=reason,
                automatic=automatic,
                overridden=reason == "user_override",
            )
        )
    return sorted(result, key=lambda r: (r.domain, r.title))


async def async_can_override(hass: HomeAssistant, key: str) -> bool:
    """Whether the user may classify this entry or integration: only when unknown."""
    kind, _, ref = key.partition(":")
    if kind == "entry":
        entry = hass.config_entries.async_get_entry(ref)
        if entry is None:
            return False
        (result,) = [r for r in await async_classify_entries(hass) if r.entry_id == ref]
        return result.automatic is Reach.UNKNOWN
    integrations = await async_get_integrations(hass, {ref})
    iot_class = effective_iot_class(integrations.get(ref))
    return reach_from_iot_class(iot_class)[0] is Reach.UNKNOWN
