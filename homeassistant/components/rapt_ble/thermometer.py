"""RAPT Bluetooth Thermometer parser used for local integration testing."""

import logging
from struct import unpack

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import SensorLibrary

_LOGGER = logging.getLogger(__name__)

RAPT_TEMPERATURE_MANUFACTURER_ID = 76
RAPT_TEMPERATURE_IBEACON_PREFIX = bytes.fromhex(
    "02154b6567b722314977852625b74c616e64"
)


def decode_rapt_temperature(raw_temperature: int) -> float:
    """Decode RAPT Bluetooth Thermometer fixed-point Kelvin to Celsius."""
    return round(raw_temperature / 64 - 273.15, 2)


class RAPTTemperatureBluetoothDeviceData(BluetoothData):
    """Data update for the RAPT Bluetooth Thermometer."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from a RAPT Bluetooth Thermometer iBeacon advertisement."""
        data = service_info.manufacturer_data.get(RAPT_TEMPERATURE_MANUFACTURER_ID)
        if data is None:
            return

        # iBeacon payload: type/length + UUID + major + minor + TX power.
        if len(data) != 23 or not data.startswith(RAPT_TEMPERATURE_IBEACON_PREFIX):
            return

        (raw_temperature,) = unpack(">H", data[18:20])
        temperature = decode_rapt_temperature(raw_temperature)

        _LOGGER.debug(
            "Parsed RAPT Bluetooth Thermometer data: raw=%d temperature=%s",
            raw_temperature,
            temperature,
        )

        self.set_device_manufacturer("RAPT")
        self.set_device_type("RAPT Bluetooth Thermometer")
        mac_suffix = short_address(service_info.address)
        self.set_device_name(f"RAPT Temp {mac_suffix}")
        self.set_title(f"RAPT Temp {mac_suffix}")
        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS, temperature
        )
