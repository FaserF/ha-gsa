"""Sensor platform for the Microsoft Global Secure Access Version integration."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MACOS_URL, MANUFACTURER, WINDOWS_URL
from .coordinator import GlobalSecureAccessDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        GlobalSecureAccessVersionSensor(coordinator, "windows"),
        GlobalSecureAccessVersionSensor(coordinator, "macos"),
    ]

    async_add_entities(sensors)


class GlobalSecureAccessVersionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Global Secure Access Version sensor."""

    def __init__(
        self,
        coordinator: GlobalSecureAccessDataUpdateCoordinator,
        platform_type: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._platform_type = platform_type
        self._attr_translation_key = platform_type
        self._attr_unique_id = f"gsa_latest_version_{platform_type}"
        self._attr_icon = (
            "mdi:microsoft-windows" if platform_type == "windows" else "mdi:apple"
        )
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, "global_secure_access_client")},
            name="Global Secure Access Client",
            manufacturer=MANUFACTURER,
            model="Global Secure Access Client",
            configuration_url=WINDOWS_URL,
        )

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        url = WINDOWS_URL if self._platform_type == "windows" else MACOS_URL
        attributes = {"data_provided_by": url}

        if self.coordinator.data and (
            platform_data := self.coordinator.data.get(self._platform_type)
        ):
            if release_date := platform_data.get("release_date"):
                attributes["release_day"] = release_date
            if changelog := platform_data.get("changelog"):
                attributes["changelog"] = changelog

        return attributes

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data and (
            platform_data := self.coordinator.data.get(self._platform_type)
        ):
            return platform_data.get("version")
        return None

    @property
    def available(self) -> bool:
        """Return True if coordinator data is available."""
        return (
            self.coordinator.last_update_success and self.coordinator.data is not None
        )
