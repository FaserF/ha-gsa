"""DataUpdateCoordinator for the Microsoft Global Secure Access Version integration."""

import logging
import re
from datetime import timedelta

import async_timeout
from bs4 import BeautifulSoup

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.helpers.issue_registry import (
    IssueSeverity,
    async_create_issue,
    async_delete_issue,
)
from homeassistant.util import dt as dt_util

from .const import DOMAIN, HEADERS, MACOS_URL, WINDOWS_URL

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
        self.last_success = dt_util.utcnow()

    async def _async_update_data(self):
        """Fetch data from the release notes pages."""
        try:
            async with async_timeout.timeout(30):
                windows_data = await self._scrape_release_info(WINDOWS_URL)
                macos_data = await self._scrape_release_info(MACOS_URL)

                if windows_data is None or macos_data is None:
                    raise UpdateFailed(
                        f"Could not scrape version information. Windows: {windows_data}, macOS: {macos_data}"
                    )

                _LOGGER.debug("Latest Windows version: %s", windows_data["version"])
                _LOGGER.debug("Latest macOS version: %s", macos_data["version"])

                # Update last success and clear any existing issues
                self.last_success = dt_util.utcnow()
                async_delete_issue(self.hass, DOMAIN, "scraping_failure")

                return {
                    "windows": windows_data,
                    "macos": macos_data,
                }
        except Exception as err:
            _LOGGER.error("Error communicating with Microsoft Learn: %s", err)

            # Check if we should create a repair issue (failed for > 24 hours)
            if dt_util.utcnow() - self.last_success > timedelta(hours=24):
                _LOGGER.warning(
                    "Scraping has failed for over 24 hours. Creating repair issue."
                )
                async_create_issue(
                    self.hass,
                    DOMAIN,
                    "scraping_failure",
                    is_fixable=False,
                    severity=IssueSeverity.WARNING,
                    translation_key="scraping_failure",
                    learn_more_url="https://github.com/FaserF/ha-gsa/issues",
                )

            raise UpdateFailed(f"Error communicating with Microsoft Learn: {err}") from err

    async def _scrape_release_info(self, url: str) -> dict[str, str | None] | None:
        """Scrape the latest release information from a given URL."""
        _LOGGER.debug("Scraping release info from %s", url)
        try:
            async with self.websession.get(url, headers=HEADERS) as response:
                response.raise_for_status()
                html_content = await response.text()
        except Exception as err:
            _LOGGER.warning("Could not fetch %s: %s", url, err)
            return None

        soup = BeautifulSoup(html_content, "html.parser")

        # Find the main content area to avoid grabbing versions from sidebars etc.
        # Fallback to the whole soup if main is not found
        search_area = soup.find("main", id="main")
        if not search_area:
            _LOGGER.debug(
                "Could not find main content area on %s, falling back to body", url
            )
            search_area = soup

        # Find version in headers (h1-h4)
        # Regex explanation:
        # (?i) - case insensitive
        # Version - literal string
        # [:\s]* - zero or more colons or whitespace characters
        # ([\d\.]+) - one or more digits and dots (the version number)
        version_pattern = re.compile(r"(?i)Version[:\s]*([\d\.]+)")

        for tag_name in ["h1", "h2", "h3", "h4"]:
            tags = search_area.find_all(tag_name)
            for tag in tags:
                text = tag.get_text(strip=True)
                match = version_pattern.search(text)
                if match:
                    version = match.group(1)
                    _LOGGER.debug(
                        "Found version %s in %s tag on %s", version, tag_name, url
                    )

                    # Try to extract release date and changelog from siblings
                    release_date = None
                    changelog_parts = []

                    for sibling in tag.next_siblings:
                        if sibling.name in ["h1", "h2"]:
                            # Next major version starts
                            break

                        if sibling.name == "p" and not release_date:
                            stext = sibling.get_text(strip=True)
                            if "Released for download" in stext:
                                release_date = stext.replace(
                                    "Released for download on", ""
                                ).strip(" .")

                        if sibling.name in ["h3", "h4", "ul"]:
                            changelog_parts.append(
                                sibling.get_text(strip=True, separator="\n")
                            )

                    return {
                        "version": version,
                        "release_date": release_date,
                        "changelog": "\n".join(changelog_parts).strip()
                        if changelog_parts
                        else None,
                    }

        # If not found in headers, try to find in paragraphs but be more specific
        # We look for "Version X.Y.Z" in any text, but only return the first match
        # which is likely the latest version as it's at the top.
        _LOGGER.debug(
            "Could not find version in headers on %s, trying general search", url
        )
        match = version_pattern.search(search_area.get_text())
        if match:
            version = match.group(1)
            _LOGGER.debug("Found version %s via general search on %s", version, url)
            return {"version": version, "release_date": None, "changelog": None}

        _LOGGER.warning("Could not find any version pattern on %s", url)
        return None
