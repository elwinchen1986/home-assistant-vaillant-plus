"""Test vaillant-plus switch."""
from unittest.mock import call, patch

from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    ATTR_NAME,
    ATTR_TEMPERATURE,
    STATE_ON,
    STATE_OFF,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vaillant_plus import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
    VaillantDeviceApiClient,
)
from custom_components.vaillant_plus.const import (
    DOMAIN,
    DISPATCHERS,
    WEBSOCKET_CLIENT,
    EVT_DEVICE_CONNECTED,
    EVT_DEVICE_UPDATED,
)

from .const import MOCK_CONFIG_ENTRY_DATA, MOCK_DID, MOCK_DEVICE_ATTRS_WHEN_CONNECT


async def test_init_setup_and_unload_entry(hass: HomeAssistant, bypass_get_device_info):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ENTRY_DATA, entry_id=MOCK_DID
    )

    # Functions/objects can be patched directly in test code as well and can be used to test
    # additional things, like whether a function was called or what arguments it was called with
    with patch(
        "custom_components.vaillant_plus.VaillantDeviceApiClient.connect"
    ) as connect_func:
        assert await async_setup(hass, {})
        assert await async_setup_entry(hass, config_entry)

        assert DOMAIN in hass.data
        assert MOCK_DID in hass.data[DOMAIN][DISPATCHERS]
        assert config_entry.entry_id in hass.data[DOMAIN][WEBSOCKET_CLIENT]
        assert isinstance(
            hass.data[DOMAIN][WEBSOCKET_CLIENT][config_entry.entry_id],
            VaillantDeviceApiClient,
        )

        client = hass.data[DOMAIN][WEBSOCKET_CLIENT][config_entry.entry_id].client
        client._on_subscribe_handler(MOCK_DEVICE_ATTRS_WHEN_CONNECT)

        # async_dispatcher_send(
        #     hass,
        #     EVT_DEVICE_UPDATED.format(MOCK_DID),
        #     MOCK_DEVICE_ATTRS_WHEN_CONNECT,
        # )

        await hass.async_block_till_done()
        assert connect_func.called
        assert len(hass.data[DOMAIN][DISPATCHERS][MOCK_DID]) >= 2

        # Test whether the states of those entities are correct
        state_binary_sensor_heating = hass.states.get("binary_sensor.heating")
        assert (
            state_binary_sensor_heating.attributes.get(ATTR_FRIENDLY_NAME) == "Heating"
        )
        assert state_binary_sensor_heating.state == STATE_OFF

        state_water_heater = hass.states.get("water_heater.pn")
        assert state_water_heater.state == STATE_ON
        assert state_water_heater.attributes.get(ATTR_TEMPERATURE) == 45.0
        assert state_water_heater.attributes.get("min_temp") == 35.0
        assert state_water_heater.attributes.get("max_temp") == 65.0
        assert state_water_heater.attributes.get("target_temp_low") == 35.0
        assert state_water_heater.attributes.get("target_temp_high") == 65.0

        state_climate = hass.states.get("climate.pn")
        assert state_climate.state == STATE_OFF
        assert state_climate.attributes.get("hvac_action") == STATE_OFF
        assert state_climate.attributes.get("current_temperature") == 20.5

        with patch(
            "custom_components.vaillant_plus.VaillantDeviceApiClient.close"
        ) as close_func:
            assert await async_unload_entry(hass, config_entry)
            await hass.async_block_till_done()
            assert close_func.called
            assert config_entry.entry_id not in hass.data[DOMAIN][WEBSOCKET_CLIENT]
