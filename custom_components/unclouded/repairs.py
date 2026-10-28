"""Repair issues: important automations that need the internet, and integrations
that need more of it than before (see changes.py)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant, split_entity_id
from homeassistant.helpers import issue_registry as ir

from .analyze import Verdict, async_analyze_automations
from .classify import async_classify_entries
from .const import DOMAIN
from .settings import async_get_settings

_PREFIX = "important_"


def _issue_id(entity_id: str) -> str:
    return _PREFIX + split_entity_id(entity_id)[1]


async def async_update_issues(hass: HomeAssistant) -> None:
    """Bring all issues of Unclouded up to date."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if entries and (baseline := getattr(entries[0], "runtime_data", None)):
        overrides = async_get_settings(hass).overrides
        await baseline.async_check(await async_classify_entries(hass, overrides))

    wanted = {}
    for report in await async_analyze_automations(hass):
        if not report.important or report.verdict not in (
            Verdict.FAILS,
            Verdict.DEGRADED,
        ):
            continue
        if report.only_notifications:
            key = "important_notifications"
        else:
            key = f"important_{report.verdict}"
        wanted[_issue_id(report.entity_id)] = (key, report.name)

    for issue_id in _own_issues(hass) - wanted.keys():
        ir.async_delete_issue(hass, DOMAIN, issue_id)
    for issue_id, (key, name) in wanted.items():
        ir.async_create_issue(
            hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=key,
            translation_placeholders={"name": name},
        )


def async_remove_issues(hass: HomeAssistant) -> None:
    """Remove all issues of Unclouded."""
    for domain, issue_id in list(ir.async_get(hass).issues):
        if domain == DOMAIN:
            ir.async_delete_issue(hass, DOMAIN, issue_id)


def _own_issues(hass: HomeAssistant) -> set[str]:
    return {
        issue_id
        for domain, issue_id in ir.async_get(hass).issues
        if domain == DOMAIN and issue_id.startswith(_PREFIX)
    }


async def async_create_fix_flow(
    hass: HomeAssistant, issue_id: str, data: dict[str, Any] | None
) -> RepairsFlow:
    """Changed integrations are fixed by confirming that the user has seen it."""
    return ConfirmRepairFlow()
