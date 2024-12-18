"""Climate platform for Cuby integration."""
from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, CubyAPI

_LOGGER = logging.getLogger(__name__)

HVAC_MODES = {
    "off": HVACMode.OFF,
    "cool": HVACMode.COOL,
    "heat": HVACMode.HEAT,
    "auto": HVACMode.AUTO,
    "dry": HVACMode.DRY,
    "fan_only": HVACMode.FAN_ONLY,
}

FAN_MODES = {
    "auto": FAN_AUTO,
    "low": FAN_LOW,
    "medium": FAN_MEDIUM,
    "high": FAN_HIGH,
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Cuby climate platform from a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Fetching Cuby devices...")
    devices = await api.get_devices()
    
    if not devices:
        _LOGGER.error("No Cuby devices found")
        return
    
    _LOGGER.debug("Found %d Cuby devices: %s", len(devices), devices)
    
    entities = []
    for device in devices:
        _LOGGER.info("Adding Cuby device: %s", device.get("name", device["id"]))
        entities.append(CubyClimate(api, device))
    
    async_add_entities(entities)

class CubyClimate(ClimateEntity):
    """Representation of a Cuby climate device."""

    def __init__(self, api: CubyAPI, device: dict):
        """Initialize the climate device."""
        self._api = api
        self._device = device
        self._attr_unique_id = device["id"]
        self._attr_name = device.get("name", f"Cuby AC {device['id']}")
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
        )
        self._attr_hvac_modes = list(HVAC_MODES.values())
        self._attr_fan_modes = list(FAN_MODES.values())
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = 16
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1
        self._state = {}

    async def async_update(self) -> None:
        """Update the entity."""
        self._state = await self._api.get_device_state(self._device["id"])
        if self._state:
            self._attr_current_temperature = self._state.get("current_temperature")
            self._attr_target_temperature = self._state.get("target_temperature")
            self._attr_hvac_mode = HVAC_MODES.get(
                self._state.get("mode", "off"), HVACMode.OFF
            )
            self._attr_fan_mode = FAN_MODES.get(
                self._state.get("fan_mode", "auto"), FAN_AUTO
            )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        await self._api.set_ac_temperature(self._device["id"], temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        mode = next(
            (k for k, v in HVAC_MODES.items() if v == hvac_mode),
            "off"
        )
        if hvac_mode == HVACMode.OFF:
            await self._api.set_ac_power(self._device["id"], False)
        else:
            # Ensure the AC is on when changing modes
            await self._api.set_ac_full_state(
                self._device["id"],
                {
                    "power": True,
                    "mode": mode
                }
            )

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        mode = next(
            (k for k, v in FAN_MODES.items() if v == fan_mode),
            "auto"
        )
        await self._api.set_ac_fan_mode(self._device["id"], mode)

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self._api.set_ac_power(self._device["id"], True)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self._api.set_ac_power(self._device["id"], False)