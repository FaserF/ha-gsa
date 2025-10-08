"""Sensor platform for the Microsoft Global Secure Access Version integration."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MACOS_SENSOR_NAME, WINDOWS_SENSOR_NAME
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
        GlobalSecureAccessVersionSensor(coordinator, "windows", WINDOWS_SENSOR_NAME),
        GlobalSecureAccessVersionSensor(coordinator, "macos", MACOS_SENSOR_NAME),
    ]

    async_add_entities(sensors)


class GlobalSecureAccessVersionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Global Secure Access Version sensor."""

    def __init__(
        self,
        coordinator: GlobalSecureAccessDataUpdateCoordinator,
        platform_type: str,
        sensor_name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._platform_type = platform_type
        self._attr_name = sensor_name
        self._attr_unique_id = f"gsa_latest_version_{platform_type}"
        self._attr_icon = "mdi:microsoft-windows" if platform_type == "windows" else "mdi:apple"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, "global_secure_access_client")},
            name="Global Secure Access Client",
            manufacturer=MANUFACTURER,
            model="Global Secure Access Client",
        )

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._platform_type)
        return None

    @property
    def available(self) -> bool:
        """Return True if coordinator data is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
