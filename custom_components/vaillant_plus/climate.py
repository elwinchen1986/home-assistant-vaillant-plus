"""The Vaillant Plus climate platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    PRESET_COMFORT,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import VaillantClient
from .const import CONF_DID, DISPATCHERS, DOMAIN, EVT_DEVICE_CONNECTED, API_CLIENT
from .entity import VaillantEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_TEMPERATURE_INCREASE = 0.5

PRESET_SUMMER = "Summer"
PRESET_WINTER = "Winter"

SUPPORTED_FEATURES = (
    ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.TURN_OFF
)
SUPPORTED_HVAC_MODES = [HVACMode.HEAT, HVACMode.OFF]
SUPPORTED_PRESET_MODES = [PRESET_COMFORT]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback
) -> bool:
    """Set up Vaillant devices from a config entry."""

    device_id = entry.data.get(CONF_DID)
    client: VaillantClient = hass.data[DOMAIN][API_CLIENT][
        entry.entry_id
    ]

    added_entities = []

    @callback
    def async_new_climate(device_attrs: dict[str, Any]):
        _LOGGER.debug("New climate found device_attrs == %s",device_attrs)

        if "climate" not in added_entities:
            if device_attrs.get("Heating_Enable") is not None:
                new_devices = [VaillantClimate(client)]
                async_add_devices(new_devices)
                added_entities.append("climate")
            else:
                _LOGGER.warning(
                    "Missing required attribute to setup Vaillant Climate. skip."
                )
        else:
            _LOGGER.debug("Already added climate device. skip.")

    unsub = async_dispatcher_connect(
        hass, EVT_DEVICE_CONNECTED.format(device_id), async_new_climate
    )

    hass.data[DOMAIN][DISPATCHERS][device_id].append(unsub)

    return True


class VaillantClimate(VaillantEntity, ClimateEntity):
    """Vaillant vSMART Climate."""

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""

        return f"{self.device.id}_climate"

    @property
    def name(self) -> str | None:
        """Return the name of the climate."""

        return None

    @property
    def supported_features(self) -> int:
        """Return the flag of supported features for the climate."""

        return SUPPORTED_FEATURES

    @property
    def temperature_unit(self) -> str:
        """Return the measurement unit for all temperature values."""

        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self) -> float:
        """Return the current room temperature."""

        return self.get_device_attr("Flow_Temperature_Setpoint")

    @property
    def target_temperature(self) -> float:
        """Return the targeted room temperature."""

        return self.get_device_attr("Flow_Temperature_Setpoint")

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC operation modes."""

        return SUPPORTED_HVAC_MODES

    @property
    def hvac_mode(self) -> HVACMode:
        """
        Return currently selected HVAC operation mode.
        """

        # TODO whether support HVACMode.AUTO
        if self.get_device_attr("Heating_Enable") == 1:
            return HVACMode.HEAT

        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        """
        Return the currently running HVAC action.
        """

        if self.get_device_attr("Heating_Enable") == 0:
            return HVACAction.OFF

        try:
            if self.get_device_attr("Heating_Enable") == 1:
                return HVACAction.HEATING
        except TypeError:
            pass

        return HVACAction.IDLE

    @property
    def preset_modes(self) -> list[str]:
        """Return the list of available HVAC preset modes."""

        return SUPPORTED_PRESET_MODES

    @property
    def preset_mode(self) -> str:
        """Return the currently selected HVAC preset mode."""

        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Select new HVAC operation mode."""

        _LOGGER.debug("Setting HVAC mode to: %s", hvac_mode)

        if hvac_mode == HVACMode.OFF:
            await self._client.control_device({
                "Heating_Enable": False,
            })
            self.set_device_attr("Heating_Enable", False)
        elif hvac_mode == HVACMode.HEAT:
            await self._client.control_device({
                "Heating_Enable": True,
                "Mode_Setting_CH": "Cruising",
            })
            self.set_device_attr("Heating_Enable", False)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Select new HVAC preset mode."""

        _LOGGER.debug("Setting HVAC preset mode to: %s", preset_mode)
        return None
    

    async def async_set_temperature(self, **kwargs) -> None:
        """Update target room temperature value."""

        new_temperature = kwargs.get(ATTR_TEMPERATURE)
        if new_temperature is None:
            return

        _LOGGER.debug("Setting target temperature to: %s", new_temperature)

        await self._client.control_device({
            "Flow_Temperature_Setpoint": new_temperature,
        })
        self.set_device_attr("Flow_Temperature_Setpoint", new_temperature)

    async def async_turn_off(self):
	 # Implement one of these methods.
	    # The `turn_off` method should set `hvac_mode` to `HVACMode.OFF` by
	    # optimistically setting it from the service action handler or with the
	    # next state update
        self.set_device_attr("Heating_Enable", False)
        return  None
 
    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.get_device_attr("Lower_Limitation_of_CH_Setpoint")

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.get_device_attr("Upper_Limitation_of_CH_Setpoint")


    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach."""
        return self.get_device_attr("Upper_Limitation_of_CH_Setpoint")

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach."""
        return self.get_device_attr("Lower_Limitation_of_CH_Setpoint")
