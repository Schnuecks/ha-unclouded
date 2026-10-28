"""Notice when an integration needs more of the internet than it used to.

Unclouded remembers how each config entry connected. When that gets worse, typically
after an update of the integration, a repair issue says so until the user confirms it.
Improvements and newly added integrations are not reported.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.storage import Store

from .classify import EntryReach, Reach
from .const import DOMAIN

STORAGE_VERSION = 1
PREFIX = "changed_"
# Unknown has no rank: going to or from unknown says nothing about the internet.
_RANK = {Reach.LOCAL: 0, Reach.INTERNAL: 0, Reach.PARTIAL: 1, Reach.CLOUD: 2}


class Baseline:
    """How each config entry connected when Unclouded last looked."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store[dict[str, str]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.baseline"
        )
        self._known: dict[str, str] | None = None

    async def async_check(self, entries: list[EntryReach]) -> None:
        """Compare with the last look, raise issues and remember the new state."""
        first_look = False
        if self._known is None:
            stored = await self._store.async_load()
            first_look = stored is None
            self._known = stored or {}

        current = {e.entry_id: e for e in entries}
        for entry in entries:
            before = self._known.get(entry.entry_id)
            if (
                not first_look
                and before is not None
                and entry.reach in _RANK
                and _RANK[entry.reach] > _RANK[Reach(before)]
            ):
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    PREFIX + entry.entry_id,
                    is_fixable=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key=f"now_{entry.reach}",
                    translation_placeholders={
                        "title": entry.title,
                        "domain": entry.domain,
                    },
                )

        # Issues of removed entries go with them.
        for domain, issue_id in list(ir.async_get(self.hass).issues):
            if (
                domain == DOMAIN
                and issue_id.startswith(PREFIX)
                and issue_id.removeprefix(PREFIX) not in current
            ):
                ir.async_delete_issue(self.hass, DOMAIN, issue_id)

        # An entry that became unknown keeps its last known state.
        known = {
            entry_id: str(e.reach) if e.reach in _RANK else self._known.get(entry_id)
            for entry_id, e in current.items()
        }
        known = {k: v for k, v in known.items() if v is not None}
        if known != self._known:
            self._known = known
            await self._store.async_save(known)

    async def async_remove(self) -> None:
        """Forget everything, when Unclouded is removed."""
        await self._store.async_remove()
