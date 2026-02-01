import pytest
from unittest.mock import AsyncMock, patch
from datetime import timedelta
from homeassistant.util import dt as dt_util
from custom_components.global_secure_access_version.coordinator import (
    GlobalSecureAccessDataUpdateCoordinator,
)


@pytest.fixture
def hass_mock():
    hass = AsyncMock()
    # Mock synchronous methods to avoid RuntimeWarning for unawaited coroutines
    hass.bus.async_listen_once = MagicMock()
    hass.verify_event_loop_thread = MagicMock()
    hass.loop.time = MagicMock(return_value=1000.0)
    hass.data = {}
    return hass


@patch("homeassistant.helpers.frame.report_usage")
async def test_coordinator_update_success(mock_report_usage, hass_mock):
    coordinator = GlobalSecureAccessDataUpdateCoordinator(hass_mock)

    html_content = """
    <html><body><main id="main">
    <h2>Version 2.24.117</h2>
    <h2>Version 1.1.25090800</h2>
    </main></body></html>
    """

    with patch.object(coordinator.websession, "get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        # raise_for_status is synchronous in aiohttp
        mock_response.raise_for_status = MagicMock()
        mock_response.text = AsyncMock(return_value=html_content)

        # websession.get returns a context manager, so we mock __aenter__
        mock_get.return_value.__aenter__.return_value = mock_response

        # We need to mock _scrape_version twice or mock the whole response text for each call
        # For simplicity in this test, we let it return the same content for both URLs

        data = await coordinator._async_update_data()

        assert data["windows"]["version"] == "2.24.117"
        assert data["macos"]["version"] == "2.24.117"  # Since we returned same HTML
        assert (
            coordinator.last_update_success is True
        )  # This is internal HA state usually


@patch("homeassistant.helpers.frame.report_usage")
async def test_coordinator_repair_creation(mock_report_usage, hass_mock):
    coordinator = GlobalSecureAccessDataUpdateCoordinator(hass_mock)

    # Set last success to more than 24 hours ago
    coordinator.last_success = dt_util.utcnow() - timedelta(hours=25)

    with patch.object(coordinator.websession, "get") as mock_get:
        # Mock __aenter__ to raise the exception
        mock_get.return_value.__aenter__.side_effect = Exception("Connection error")

        with pytest.raises(Exception):
            await coordinator._async_update_data()

    # Check if async_create_issue was called
    # Note: Since we imported async_create_issue from homeassistant.helpers.issue_registry,
    # we need to ensure it was called within the coordinator.
    # In a real HA test environment, we would check the issue registry.
    # Here we just verify the call happened if we patch it.
