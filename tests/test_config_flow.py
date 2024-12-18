"""Test the Cuby config flow."""
from unittest.mock import patch
import pytest
from homeassistant import config_entries, data_entry_flow
from custom_components.cuby.config_flow import CubyConfigFlow
from custom_components.cuby import DOMAIN

async def test_flow_user_init(hass):
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

async def test_flow_user_success(hass, mock_config, mock_device):
    """Test successful user config flow."""
    with patch('custom_components.cuby.CubyAPI.authenticate', return_value=True), \
         patch('custom_components.cuby.CubyAPI.get_devices', return_value=[mock_device]):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=mock_config
        )

    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["title"] == mock_config["username"]
    assert result["data"] == mock_config

async def test_flow_user_invalid_auth(hass, mock_config):
    """Test failed config flow due to invalid auth."""
    with patch('custom_components.cuby.CubyAPI.authenticate', return_value=False):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}, data=mock_config
        )

    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {"base": "invalid_auth"} 