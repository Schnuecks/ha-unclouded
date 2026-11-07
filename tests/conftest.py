"""Shared fixtures."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load integrations from custom_components in every test."""
    return


@pytest.fixture(autouse=True)
def no_internet_check():
    """Tests do not open connections; the internet counts as reachable."""
    with patch(
        "custom_components.unclouded.outages._reachable", AsyncMock(return_value=True)
    ):
        yield
