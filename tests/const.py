"""Constants for vaillant-plus tests."""

from custom_components.vaillant_plus.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DID,
    CONF_TOKEN,
)

# Mock config data to be used across multiple tests
MOCK_USERNAME = "test_username"
MOCK_PASSWORD = "test_password"
MOCK_DID = "1"
MOCK_INPUT = {CONF_USERNAME: MOCK_USERNAME, CONF_PASSWORD: MOCK_PASSWORD}
MOCK_CONFIG_ENTRY_DATA = {
    CONF_DID: MOCK_DID,
    CONF_TOKEN: "eyJhcHBfaWQiOiAiMSIsICJ1c2VybmFtZSI6ICJ0ZXN0X3VzZXJuYW1lIiwgInBhc3N3b3JkIjogInRlc3RfcGFzc3dvcmQiLCAidG9rZW4iOiAidGVzdF90b2tlbiIsICJ1aWQiOiAidTEifQ==",
}
MOCK_DEVICE_ATTRS_WHEN_CONNECT = {
    "WarmStar_Tank_Loading_Enable": 1,
    "Fault_List": "00000000000000000000",
    "Lower_Limitation_of_CH_Setpoint": 30,
    "Upper_Limitation_of_DHW_Setpoint": 65,
    "Circulation_Enable": 0,
    "Room_Temperature_Setpoint_ECO": 5,
    "Tank_temperature": 127.5,
    "status_time": 1231234324,
    "Flow_temperature": 33.5,
    "DSN": 1500,
    "Time_slot_type": "CH",
    "Mode_Setting_DHW": "Cruising",
    "Maintenance": "00000000000000000000",
    "Weather_compensation": 1,
    "Outdoor_Temperature": 0,
    "Lower_Limitation_of_DHW_Setpoint": 35,
    "Flow_Temperature_Setpoint": 0,
    "Max_NumBer_Of_Timeslots_CH": 0,
    "Brand": "vaillant on desk",
    "Mode_Setting_CH": "Cruising",
    "Boiler_info3_bit0": "00",
    "Heating_System_Setting": "radiator",
    "Room_Temperature_Setpoint_Comfort": 5.5,
    "reserved_data2": "00",
    "BMU_Platform": 1,
    "Heating_Enable": 0,
    "reserved_data1": "00",
    "reserved_data3": "00",
    "Slot_current_DHW": 0,
    "Start_Time_DHW1": "000000000000000000000000",
    "Room_Temperature": 18.5,
    "Start_Time_DHW3": "000000000000000000000000",
    "Start_Time_DHW2": "000000000000000000000000",
    "Start_Time_DHW5": "000000000000000000000000",
    "Start_Time_DHW4": "000000000000000000000000",
    "Start_Time_DHW7": "000000000000000000000000",
    "Start_Time_DHW6": "000000000000000000000000",
    "Enabled_Heating": 0,
    "Enabled_DHW": 1,
    "Start_Time_CH1": "000000000000000000000000",
    "Upper_Limitation_of_CH_Setpoint": 75,
    "Slot_current_CH": 0,
    "Start_Time_CH7": "000000000000000000000000",
    "Max_NumBer_Of_Timeslots_DHW": 0,
    "Start_Time_CH6": "000000000000000000000000",
    "Start_Time_CH5": "000000000000000000000000",
    "Start_Time_CH4": "000000000000000000000000",
    "RF_Status": 3,
    "Start_Time_CH3": "000000000000000000000000",
    "Start_Time_CH2": "000000000000000000000000",
    "return_temperature": 0,
    "DHW_Function": "none",
    "Current_DHW_Setpoint": 45,
    "Boiler_info5_bit4": "00",
    "DHW_setpoint": 45,
    "Heating_Curve": 1
}

MOCK_DEVICE_ATTRS_WHEN_UPDATE = {
    "WarmStar_Tank_Loading_Enable": 1,
    "Fault_List": "00000000000000000000",
    "Lower_Limitation_of_CH_Setpoint": 30,
    "Upper_Limitation_of_DHW_Setpoint": 65,
    "Circulation_Enable": 0,
    "Room_Temperature_Setpoint_ECO": 5,
    "Tank_temperature": 127.5,
    "status_time": 3463532413245,
    "Flow_temperature": 55.5,
    "DSN": 1500,
    "Time_slot_type": "CH",
    "Mode_Setting_DHW": "Cruising",
    "Maintenance": "00000000000000000000",
    "Weather_compensation": 1,
    "Outdoor_Temperature": 0,
    "Lower_Limitation_of_DHW_Setpoint": 35,
    "Flow_Temperature_Setpoint": 0,
    "Max_NumBer_Of_Timeslots_CH": 0,
    "Brand": "vaillant on desk",
    "Mode_Setting_CH": "Cruising",
    "Boiler_info3_bit0": "00",
    "Heating_System_Setting": "radiator",
    "Room_Temperature_Setpoint_Comfort": 22.5,
    "reserved_data2": "00",
    "BMU_Platform": 1,
    "Heating_Enable": 1,
    "reserved_data1": "00",
    "reserved_data3": "00",
    "Slot_current_DHW": 0,
    "Start_Time_DHW1": "000000000000000000000000",
    "Room_Temperature": 20.5,
    "Start_Time_DHW3": "000000000000000000000000",
    "Start_Time_DHW2": "000000000000000000000000",
    "Start_Time_DHW5": "000000000000000000000000",
    "Start_Time_DHW4": "000000000000000000000000",
    "Start_Time_DHW7": "000000000000000000000000",
    "Start_Time_DHW6": "000000000000000000000000",
    "Enabled_Heating": 1,
    "Enabled_DHW": 1,
    "Start_Time_CH1": "000000000000000000000000",
    "Upper_Limitation_of_CH_Setpoint": 75,
    "Slot_current_CH": 0,
    "Start_Time_CH7": "000000000000000000000000",
    "Max_NumBer_Of_Timeslots_DHW": 0,
    "Start_Time_CH6": "000000000000000000000000",
    "Start_Time_CH5": "000000000000000000000000",
    "Start_Time_CH4": "000000000000000000000000",
    "RF_Status": 3,
    "Start_Time_CH3": "000000000000000000000000",
    "Start_Time_CH2": "000000000000000000000000",
    "return_temperature": 0,
    "DHW_Function": "none",
    "Current_DHW_Setpoint": 45,
    "Boiler_info5_bit4": "00",
    "DHW_setpoint": 60,
    "Heating_Curve": 1
}

CONF_HOST = "https://appapi.vaillant.com.cn"
CONF_HOST_API = "https://api.vaillant.com.cn"
