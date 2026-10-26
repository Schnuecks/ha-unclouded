"""What the user decided: own classifications and automations that matter.

Both live in the options of the Unclouded config entry, so they survive restarts
and go with backups.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from homeassistant.core import HomeAssistant

from .const import DOMAIN

OVERRIDES = "overrides"
IMPORTANT = "important"


def entry_key(entry_id: str) -> str:
    """Key of an override for one config entry."""
    return f"entry:{entry_id}"


def domain_key(domain: str) -> str:
    """Key of an override for entities of an integration without config entry."""
    return f"domain:{domain}"


@dataclass(slots=True)
class Settings:
    """User settings of this instance."""

    # Override key → reach chosen by the user.
    overrides: dict[str, str] = field(default_factory=dict)
    # Entity IDs of automations the user wants to be told about.
    important: set[str] = field(default_factory=set)


def async_get_settings(hass: HomeAssistant) -> Settings:
    """Read the settings; empty while Unclouded is not set up."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return Settings()
    options = entries[0].options
    return Settings(
        overrides=dict(options.get(OVERRIDES, {})),
        important=set(options.get(IMPORTANT, [])),
    )


def async_save_settings(hass: HomeAssistant, settings: Settings) -> None:
    """Store the settings in the config entry."""
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    hass.config_entries.async_update_entry(
        entry,
        options={
            **entry.options,
            OVERRIDES: dict(sorted(settings.overrides.items())),
            IMPORTANT: sorted(settings.important),
        },
    )


def prune(settings: Settings, keys: Iterable[str]) -> None:
    """Drop overrides whose config entry no longer exists."""
    known = set(keys)
    for key in list(settings.overrides):
        if key.startswith("entry:") and key not in known:
            del settings.overrides[key]
