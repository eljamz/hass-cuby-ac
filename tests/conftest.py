"""Global fixtures for Cuby integration tests."""
import pytest

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from custom_components.cuby import DOMAIN, CONF_EXPIRATION

@pytest.fixture
def mock_config():
    """Provide mock configuration."""
    return {
        CONF_USERNAME: "test@example.com",
        CONF_PASSWORD: "test_password",
        CONF_EXPIRATION: 0
    }

@pytest.fixture
def mock_device():
    """Provide mock device data."""
    return {
        "id": "test_device_id",
        "name": "Test AC",
        "model": "Test Model",
        "firmware_version": "1.0.0",
        "online": True,
        "wifi_signal": -65
    }

@pytest.fixture
def mock_device_state():
    """Provide mock device state."""
    return {
        "power": True,
        "mode": "cool",
        "target_temperature": 24,
        "current_temperature": 26,
        "fan_mode": "auto",
        "swing": "off"
    } 