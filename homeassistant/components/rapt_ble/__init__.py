"""The rapt_ble integration."""

import logging

from rapt_ble import RAPTPillBluetoothDeviceData

from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_DEVICE_TYPE, DEVICE_TYPE_PILL, DEVICE_TYPE_THERMOMETER
from .thermometer import RAPTTemperatureBluetoothDeviceData

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

type RAPTBLEConfigEntry = ConfigEntry[PassiveBluetoothProcessorCoordinator]


def _device_data_for_type(
    device_type: str,
) -> RAPTPillBluetoothDeviceData | RAPTTemperatureBluetoothDeviceData:
    """Create the parser for a configured RAPT BLE device type."""
    if device_type == DEVICE_TYPE_THERMOMETER:
        return RAPTTemperatureBluetoothDeviceData()
    return RAPTPillBluetoothDeviceData()


async def async_setup_entry(hass: HomeAssistant, entry: RAPTBLEConfigEntry) -> bool:
    """Set up RAPT BLE device from a config entry."""
    address = entry.unique_id
    assert address is not None
    device_type = entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_PILL)
    data = _device_data_for_type(device_type)
    coordinator = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.ACTIVE,
        update_method=data.update,
    )
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(
        coordinator.async_start()
    )  # only start after all platforms have had a chance to subscribe
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RAPTBLEConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
