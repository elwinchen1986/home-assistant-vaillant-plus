"""The Vaillant Plus climate platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_HALVES, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import VaillantClient
from .const import (
    CONF_DID,
    DISPATCHERS,
    DOMAIN,
    EVT_DEVICE_CONNECTED,
    WATER_HEATER_OFF,
    WATER_HEATER_ON,
    API_CLIENT,
)
from .entity import VaillantEntity

# from .entity import VaillantCoordinator, VaillantEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_TEMPERATURE_INCREASE = 0.5

SUPPORTED_FEATURES = (
    WaterHeaterEntityFeature.TARGET_TEMPERATURE
    | WaterHeaterEntityFeature.OPERATION_MODE
)


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
    def async_new_water_heater(device_attrs: dict[str, Any]):
        _LOGGER.debug("New water heater found, %s", device_attrs)
        if "water_heater" not in added_entities:
            if device_attrs.get("DHW_setpoint") is not None:
                new_devices = [VaillantWaterHeater(client)]
                async_add_devices(new_devices)
                added_entities.append("water_heater")
            else:
                _LOGGER.warning(
                    "Missing required attribute to setup Vaillant Water Heater. skip."
                )
        else:
            _LOGGER.debug("Already added water_heater device. skip.")

    unsub = async_dispatcher_connect(
        hass, EVT_DEVICE_CONNECTED.format(device_id), async_new_water_heater
    )

    hass.data[DOMAIN][DISPATCHERS][device_id].append(unsub)

    return True


class VaillantWaterHeater(VaillantEntity, WaterHeaterEntity):
    """Vaillant vSMART Water Heater."""

    def __init__(self, client):
        self._client = client  # 保存 client 参数
        self._cache = {}  # 初始化缓存字典

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self.device.id}_water_heater"

    @property
    def name(self) -> str | None:
        """Return the name of the water heater."""
        return None

    @property
    def supported_features(self) -> int:
        """Return the flag of supported features for the climate."""
        return SUPPORTED_FEATURES

    @property
    def precision(self) -> float:
        """Return the precision of the system."""
        return PRECISION_HALVES

    @property
    def temperature_unit(self) -> str:
        """Return the measurement unit for all temperature values."""
        return UnitOfTemperature.CELSIUS

    @property
    def current_operation(self) -> str | None:
        """Return current operation ie. eco, electric, performance, ..."""
        value = self._get_cached_value("WarmStar_Tank_Loading_Enable")
        if value is None:
            return None
        return WATER_HEATER_ON if value == 1 else WATER_HEATER_OFF

    @property
    def operation_list(self) -> list[str] | None:
        """Return the list of available operation modes."""
        return [WATER_HEATER_ON, WATER_HEATER_OFF]

    @property
    def current_temperature(self) -> float:
        """Return the current dhw temperature."""
        return self._get_cached_value("DHW_setpoint")

    @property
    def target_temperature(self) -> float:
        """Return the targeted dhw temperature. Current_DHW_Setpoint or DHW_setpoint"""
        return self._get_cached_value("DHW_setpoint")

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach."""
        return self._get_cached_value("Upper_Limitation_of_DHW_Setpoint")

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach."""
        return self._get_cached_value("Lower_Limitation_of_DHW_Setpoint")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        new_temperature = kwargs.get(ATTR_TEMPERATURE)
        if new_temperature is None:
            return

        _LOGGER.debug("Setting target temperature to: %s", new_temperature)

        await self._update_device_attribute("DHW_setpoint", new_temperature)

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new target operation mode."""
        value = 1 if operation_mode == WATER_HEATER_ON else 0

        _LOGGER.debug("Setting operation mode to: %s", operation_mode)

        await self._update_device_attribute("WarmStar_Tank_Loading_Enable", value)

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self._get_cached_value("Lower_Limitation_of_DHW_Setpoint")

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self._get_cached_value("Upper_Limitation_of_DHW_Setpoint")

    def _get_cached_value(self, attr_name: str, default: Any = None) -> Any:
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

    @callback
    def update_from_latest_data(self, data: dict[str, Any]) -> None:
        """Update the water heater entity from the latest data."""
        # 更新缓存中的关键属性，确保控制参数能及时反映外部变更
        if "WarmStar_Tank_Loading_Enable" in data:
            self._cache["WarmStar_Tank_Loading_Enable"] = data["WarmStar_Tank_Loading_Enable"]
        
        if "DHW_setpoint" in data:
            self._cache["DHW_setpoint"] = data["DHW_setpoint"]
        
        if "Lower_Limitation_of_DHW_Setpoint" in data:
            self._cache["Lower_Limitation_of_DHW_Setpoint"] = data["Lower_Limitation_of_DHW_Setpoint"]
        
        if "Upper_Limitation_of_DHW_Setpoint" in data:
            self._cache["Upper_Limitation_of_DHW_Setpoint"] = data["Upper_Limitation_of_DHW_Setpoint"]
        
        self.async_write_ha_state()

    async def _update_device_attribute(self, attr_name: str, value: Any) -> None:
        """
        Update a device attribute and the cache.
        """
        try:
            await self.send_command(attr_name, value)
            self._cache[attr_name] = value  # 更新缓存
            self.set_device_attr(attr_name, value)
        except Exception as e:
            _LOGGER.error("Failed to update device attribute %s: %s", attr_name, e)
