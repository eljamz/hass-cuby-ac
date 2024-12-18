"""Sensor platform for Cuby integration."""
from __future__ import annotations

import logging
from typing import Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    PERCENTAGE,
)
from . import DOMAIN, CubyAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Cuby sensor platform."""
    api: CubyAPI = hass.data[DOMAIN]
    devices = await api.discover_devices()
    
    entities = []
    for device in devices:
        entities.extend([
            CubyWiFiSensor(api, device),
            CubyOnlineSensor(api, device),
            CubyModeSensor(api, device),
        ])
    
    async_add_entities(entities)

class CubyBaseSensor(SensorEntity):
    """Base class for Cuby sensors."""

    def __init__(self, api: CubyAPI, device: dict):
        """Initialize the sensor."""
        self._api = api
        self._device = device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device["id"])},
            "name": device.get("name", f"Cuby AC {device['id']}"),
            "manufacturer": "Cuby",
            "model": device.get("model", "AC Controller"),
            "sw_version": device.get("firmware_version"),
        }

class CubyWiFiSensor(CubyBaseSensor):
    """Representation of Cuby WiFi strength sensor."""

    def __init__(self, api: CubyAPI, device: dict):
        """Initialize the WiFi sensor."""
        super().__init__(api, device)
        self._attr_unique_id = f"{device['id']}_wifi"
        self._attr_name = f"{device.get('name', 'Cuby AC')} WiFi Signal"
        self._attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    async def async_update(self) -> None:
        """Update the sensor."""
        info = await self._api.get_device_info(self._device["id"])
        if info:
            self._attr_native_value = info.get("wifi_signal")

class CubyOnlineSensor(CubyBaseSensor):
    """Representation of Cuby online status sensor."""

    def __init__(self, api: CubyAPI, device: dict):
        """Initialize the online status sensor."""
        super().__init__(api, device)
        self._attr_unique_id = f"{device['id']}_online"
        self._attr_name = f"{device.get('name', 'Cuby AC')} Online Status"

    async def async_update(self) -> None:
        """Update the sensor."""
        info = await self._api.get_device_info(self._device["id"])
        if info:
            self._attr_native_value = "online" if info.get("online", False) else "offline"

class CubyModeSensor(CubyBaseSensor):
    """Representation of Cuby operation mode sensor."""

    def __init__(self, api: CubyAPI, device: dict):
        """Initialize the mode sensor."""
        super().__init__(api, device)
        self._attr_unique_id = f"{device['id']}_mode"
        self._attr_name = f"{device.get('name', 'Cuby AC')} Mode"

    async def async_update(self) -> None:
        """Update the sensor."""
        state = await self._api.get_device_state(self._device["id"])
        if state:
            self._attr_native_value = state.get("mode", "unknown")
