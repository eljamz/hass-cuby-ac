"""Test Cuby climate platform."""
from unittest.mock import patch, MagicMock
import pytest
from homeassistant.components.climate.const import (
    HVACMode,
    ATTR_TEMPERATURE,
)
from custom_components.cuby.climate import CubyClimate

async def test_climate_update(hass, mock_device, mock_device_state):
    """Test climate entity updates."""
    api = MagicMock()
    api.get_device_state.return_value = mock_device_state
    
    climate = CubyClimate(api, mock_device)
    await climate.async_update()
    
    assert climate.hvac_mode == HVACMode.COOL
    assert climate.current_temperature == mock_device_state["current_temperature"]
    assert climate.target_temperature == mock_device_state["temperature"]

async def test_set_temperature(hass, mock_device):
    """Test setting temperature."""
    api = MagicMock()
    api.set_ac_temperature.return_value = True
    
    climate = CubyClimate(api, mock_device)
    await climate.async_set_temperature(**{ATTR_TEMPERATURE: 25})
    
    api.set_ac_temperature.assert_called_once_with(mock_device["id"], 25)

async def test_set_hvac_mode(hass, mock_device):
    """Test setting HVAC mode."""
    api = MagicMock()
    api.set_ac_full_state.return_value = True
    
    climate = CubyClimate(api, mock_device)
    await climate.async_set_hvac_mode(HVACMode.HEAT)
    
    api.set_ac_full_state.assert_called_once_with(
        mock_device["id"],
        {"power": True, "mode": "heat"}
    ) 