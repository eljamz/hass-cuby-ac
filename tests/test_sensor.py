"""Test Cuby sensor platform."""
from unittest.mock import patch, MagicMock
import pytest
from custom_components.cuby.sensor import CubyWiFiSensor, CubyOnlineSensor

async def test_wifi_sensor(hass, mock_device):
    """Test WiFi signal strength sensor."""
    api = MagicMock()
    api.get_device_info.return_value = {"wifi_signal": -65}
    
    sensor = CubyWiFiSensor(api, mock_device)
    await sensor.async_update()
    
    assert sensor.native_value == -65

async def test_online_sensor(hass, mock_device):
    """Test online status sensor."""
    api = MagicMock()
    api.get_device_info.return_value = {"online": True}
    
    sensor = CubyOnlineSensor(api, mock_device)
    await sensor.async_update()
    
    assert sensor.native_value == "online" 