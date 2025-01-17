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
    
    def __init__(self, client):
        self._client = client  # 保存 client 参数
        self._cache = {}  # 初始化缓存字典

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
        return self._get_cached_value("Flow_Temperature_Setpoint", default=35.0)

    @property
    def target_temperature(self) -> float:
        """Return the targeted room temperature."""
        return self._get_cached_value("Flow_Temperature_Setpoint", default=35.0)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC operation modes."""
        return SUPPORTED_HVAC_MODES

    @property
    def hvac_mode(self) -> HVACMode:
        """
        Return currently selected HVAC operation mode.
        If Heating_Enable is not available, return the last known value.
        """
        try:
            enable = self._get_cached_value("Heating_Enable",HVACMode.OFF)
            if enable == 1:
                self._cache["hvac_mode"] = HVACMode.HEAT
            else:
                self._cache["hvac_mode"] = HVACMode.OFF
        except (AttributeError, KeyError):
            pass  # 如果获取失败，保持上一次的值

        return self._cache.get("hvac_mode", HVACMode.OFF)

    @property
    def hvac_action(self) -> HVACAction:
        """
        Return the currently running HVAC action.
        If Heating_Enable is not available, return the last known value.
        """
        try:
            enable = self._get_cached_value("Heating_Enable",False)
            _LOGGER.debug("enable===%s",enable)
            if enable == 0:
                self._cache["hvac_action"] = HVACAction.OFF
            elif enable == 1:
                self._cache["hvac_action"] = HVACAction.HEATING
            else:
                self._cache["hvac_action"] = HVACAction.IDLE
        except (AttributeError, KeyError):
            pass  # 如果获取失败，保持上一次的值

        return self._cache.get("hvac_action", HVACAction.IDLE)
    

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

        try:
            if hvac_mode == HVACMode.OFF:
                await self._client.control_device({"Heating_Enable": False})
                self.set_device_attr("Heating_Enable", False)
                self._cache["hvac_mode"] = HVACMode.OFF
                self._cache["hvac_action"] = HVACAction.OFF
            elif hvac_mode == HVACMode.HEAT:
                await self._client.control_device({"Heating_Enable": True})
                self.set_device_attr("Heating_Enable", True)
                self._cache["hvac_mode"] = HVACMode.HEAT
                self._cache["hvac_action"] = HVACAction.HEATING
        except Exception as e:
            _LOGGER.error("Failed to set HVAC mode: %s", e)

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
       
        self._cache["Flow_Temperature_Setpoint"] = new_temperature
        self.set_device_attr("Flow_Temperature_Setpoint", new_temperature)

    async def async_turn_off(self):
        """
        Turn off the climate device.
        This method sets `Heating_Enable` to False and updates the cached values.
        """
        try:
            # 关闭设备
            await self._client.control_device({"Heating_Enable": False})
            self.set_device_attr("Heating_Enable", False)

            # 更新缓存
            self._cache["hvac_mode"] = HVACMode.OFF
            self._cache["hvac_action"] = HVACAction.OFF
        except Exception as e:
            _LOGGER.error("Failed to turn off the device: %s", e)
 
    @property
    def min_temp(self) -> float | None:
        """Return the minimum temperature."""
        return self._get_cached_value("Lower_Limitation_of_CH_Setpoint", default=30.0)

    @property
    def max_temp(self) -> float | None:
        """Return the maximum temperature."""
        return self._get_cached_value("Upper_Limitation_of_CH_Setpoint", default=75.0)
    

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach."""
        return self._get_cached_value("Upper_Limitation_of_CH_Setpoint", default=75.0)

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach."""
        return self._get_cached_value("Lower_Limitation_of_CH_Setpoint", default=30.0)
    
    def _get_cached_value(self, attr_name: str, default: float) -> float:
        """
        Get a cached value for a device attribute.
        If the value is not available, return the last known value or a default value.
        """
        try:
            value = self.get_device_attr(attr_name)
            if value is not None:
                self._cache[attr_name] = value  # 更新缓存
        except (AttributeError, KeyError) as e:
            _LOGGER.debug("Failed to get device attribute %s: %s", attr_name, e)
            value = None  # 如果获取失败，保持上一次的值

        # 如果当前值为 None 且缓存值不为 None，则返回缓存值
        if value is None and attr_name in self._cache:
            return self._cache[attr_name]

        # 如果当前值和缓存值都为 None，则返回默认值
        return value if value is not None else default
