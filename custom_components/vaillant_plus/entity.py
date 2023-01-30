"""Vaillant vSMART entity classes."""
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .client import VaillantDeviceApiClient
from .const import DOMAIN, EVT_DEVICE_UPDATED

UPDATE_INTERVAL = timedelta(minutes=1)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class VaillantEntity(Entity):
    """Base class for Vaillant entities."""

    def __init__(
        self,
        client: VaillantDeviceApiClient,
    ):
        """Initialize."""
        self._client = client

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def update(data: dict[str, Any]) -> None:
            """Update the state."""
            _LOGGER.debug("write ha state: %s", data)
            self.update_from_latest_data(data)
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, EVT_DEVICE_UPDATED.format(self._client._device.id), update
            )
        )

        if len(self._client._device_attrs) > 0:
            self.update_from_latest_data(self._client._device_attrs)

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> dict[str, Any]:
        """Return all device info available for this entity."""

        return {
            "identifiers": {(DOMAIN, self._client._device.id)},
            "name": self._client._device.model,
            "sw_version": self._client._device.mcu_soft_version,
            "manufacturer": "Vaillant",
            "via_device": (DOMAIN, self._client._device.id),
        }

    @callback
    def update_from_latest_data(self, data: dict[str, Any]) -> None:
        """Update the entity from the latest data."""