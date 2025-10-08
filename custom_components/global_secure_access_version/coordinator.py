"""DataUpdateCoordinator for the Microsoft Global Secure Access Version integration."""
import logging
import re
from datetime import timedelta

import async_timeout
from bs4 import BeautifulSoup

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MACOS_URL, WINDOWS_URL

_LOGGER = logging.getLogger(__name__)


class GlobalSecureAccessDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Microsoft release notes."""

    def __init__(self, hass):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(days=1),
        )
        self.websession = async_get_clientsession(hass)

    async def _async_update_data(self):
        """Fetch data from the release notes pages."""
        try:
            async with async_timeout.timeout(30):
                windows_version = await self._scrape_version(WINDOWS_URL)
                macos_version = await self._scrape_version(MACOS_URL)

                if windows_version is None or macos_version is None:
                    raise UpdateFailed("Could not scrape version information.")

                _LOGGER.debug(f"Latest Windows version: {windows_version}")
                _LOGGER.debug(f"Latest macOS version: {macos_version}")

                return {
                    "windows": windows_version,
                    "macos": macos_version,
                }
        except Exception as err:
            _LOGGER.error("Error communicating with Microsoft Learn: %s", err)
            raise UpdateFailed(f"Error communicating with Microsoft Learn: {err}") from err

    async def _scrape_version(self, url: str) -> str | None:
        """Scrape the latest version from a given URL."""
        _LOGGER.debug(f"Scraping version from {url}")
        response = await self.websession.get(url)
        response.raise_for_status()

        html_content = await response.text()
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the main content area to avoid grabbing versions from sidebars etc.
        main_content = soup.find("main", id="main")
        if not main_content:
            _LOGGER.warning(f"Could not find main content area on {url}")
            return None

        # Find all H2 tags and iterate to find the first one with a version number
        all_h2_tags = main_content.find_all("h2")
        for h2_tag in all_h2_tags:
            # Use regex to find the version number, e.g., "Version 2.20.56"
            match = re.search(r"Version ([\d\.]+)", h2_tag.text)
            if match:
                version = match.group(1)
                _LOGGER.debug(f"Found version {version} on {url}")
                return version

        _LOGGER.warning(f"Could not find any version pattern in H2 tags on {url}")
        return None

