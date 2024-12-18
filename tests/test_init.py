"""Test Cuby setup."""
from unittest.mock import patch, MagicMock
import pytest
from homeassistant.setup import async_setup_component
from custom_components.cuby import DOMAIN

async def test_setup(hass, mock_config):
    """Test the setup."""
    with patch('custom_components.cuby.CubyAPI.authenticate', return_value=True), \
         patch('custom_components.cuby.CubyAPI.get_devices', return_value=[{"id": "test"}]):
        assert await async_setup_component(hass, DOMAIN, {
            DOMAIN: mock_config
        })
        await hass.async_block_till_done()
        assert DOMAIN in hass.data

async def test_setup_failed_auth(hass, mock_config):
    """Test setup with failed authentication."""
    with patch('custom_components.cuby.CubyAPI.authenticate', return_value=False):
        assert not await async_setup_component(hass, DOMAIN, {
            DOMAIN: mock_config
        })
        await hass.async_block_till_done()
        assert DOMAIN not in hass.data 